import datetime
import json
import os
import shutil
from collections import defaultdict
from copy import deepcopy

import numpy as np
import torch
import yaml
import asyncio
from concurrent.futures import ThreadPoolExecutor
from torch import nn
from torch.utils.data import RandomSampler, DataLoader, Dataset
from transformers import AutoTokenizer, AutoModel, AutoConfig, AdamW, get_linear_schedule_with_warmup
from ..models import db, SkillExampleSentence, Skill
from ..models import TransformerModel as TransformerModelDB
from sqlalchemy import desc, or_, asc, func
import logging

logger = logging.getLogger(__name__)


class TransformerModule(nn.Module):
    def __init__(self, config, bert):
        super(TransformerModule, self).__init__()
        self.config = config
        self.model_config = config["model"]
        self.num_labels = len(config["all_skills"])
        self.bert = bert
        self.dropout = nn.Dropout(self.model_config.get("dropout", 0.1))
        class_dim = self.model_config.get("classification_dim", 256)
        self.adapter = nn.Conv1d(1, self.num_labels*class_dim, bert.config.hidden_size)
        self.classifier = nn.Conv1d(self.num_labels*class_dim, self.num_labels, 1, groups=self.num_labels)
        self.sigmoid = nn.Sigmoid()

    def forward(self, input_ids=None, attention_mask=None, labels=None, pos_weight=None):
        bert_outputs = self.bert(input_ids, attention_mask=attention_mask)

        pooled_output = bert_outputs[0][:, 0]
        pooled_output = self.dropout(pooled_output)
        pooled_output = nn.GELU()(self.adapter(pooled_output.unsqueeze(1)))
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output).squeeze(dim=2)
        outputs = (self.sigmoid(logits),)

        if labels is not None:
            loss_fct = nn.BCEWithLogitsLoss(pos_weight=pos_weight, reduction="mean")
            loss = loss_fct(logits, labels)
            outputs = outputs + (loss,)

        return outputs  # sigmoid(logits), (loss)


class CustomDataset(Dataset):
    def __init__(self, input_ids, labels):
        self.input_ids = input_ids
        self.labels = labels

    def __getitem__(self, index: int):
        return self.input_ids[index], self.labels[index]

    def __len__(self) -> int:
        return len(self.labels)


class TransformerModel:
    def __init__(self, config_or_model_folder, ignore_list):
        if isinstance(config_or_model_folder, str):
            config = yaml.load(open(os.path.join(config_or_model_folder, "config.yaml")))
        else:
            config = config_or_model_folder
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() and not config.get("no_gpu", False) else "cpu")
        self.all_skills = config["all_skills"]
        self.skill_weights = [1.0] * len(self.all_skills)
        self.model_folder = config["model_folder"]
        with open(os.path.join(self.model_folder, "config.yaml"), mode="w") as f:
            yaml.dump(config, f)
        if os.path.exists(os.path.join(self.model_folder, "results.json")):
            with open(os.path.join(self.model_folder, "results.json")) as f:
                self.all_results = json.load(f)
        else:
            self.all_results = {"best_epoch": -1, "latest_epoch": -1, "epoch_results": []}
        self.tokenizer = AutoTokenizer.from_pretrained(config["model"]["model_name"], cache_dir=config["cache_dir"])
        if config.get("make_new_model", False):
            bert_model = AutoModel.from_pretrained(config["model"]["model_name"], cache_dir=config["cache_dir"])
        else:
            bert_config = AutoConfig.from_pretrained(config["model"]["model_name"], cache_dir=config["cache_dir"])
            bert_model = AutoModel.from_config(bert_config)
        self.model = TransformerModule(config, bert_model)
        if not config.get("make_new_model", False):
            model_file = os.path.join(self.model_folder, "model.pty")
            state_dict = torch.load(model_file)
            self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()
        self.ignore_list = ignore_list

    def train(self, train_dataset, dev_datasets):
        self.model.train()
        model_file = os.path.join(self.model_folder, "model.pty")
        train_dataset = self._create_dataset(train_dataset, is_trainset=True)
        dev_datasets = self._create_dataset(dev_datasets, is_trainset=False)
        train_config = self.config["train"]
        train_sampler = RandomSampler(train_dataset)
        gradient_accumulation_steps = train_config.get("gradient_accumulation_steps", 1)
        train_dataloader = DataLoader(train_dataset, sampler=train_sampler,
                                      batch_size=int(train_config["batch_size"]/gradient_accumulation_steps),
                                      collate_fn=self._collate)
        epochs = train_config["epochs"]

        no_decay = ["bias", "LayerNorm.weight"]
        weight_decay = train_config.get("weight_decay", 0.0)
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in self.model.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": weight_decay,
            },
            {"params": [p for n, p in self.model.named_parameters() if any(nd in n for nd in no_decay)],
             "weight_decay": 0.0},
        ]

        learning_rate = train_config.get("learning_rate", 5e-5)
        adam_epsilon = train_config.get("adam_epsilon", 1e-8)
        warmup_fraction = train_config.get("warmup_fraction", 0.0)
        t_total = len(train_dataloader) // gradient_accumulation_steps * epochs
        warmup_steps = int(t_total*warmup_fraction)
        max_grad_norm = train_config.get("max_grad_norm", 1.0)
        optimizer = AdamW(optimizer_grouped_parameters, lr=learning_rate, eps=adam_epsilon)
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=warmup_steps, num_training_steps=t_total
        )
        # Train!
        #  logger.info("***** Running training *****")
        #  logger.info("  Num examples = %d", len(train_dataset))
        #  logger.info("  Num Epochs = %d", epochs)
        #  logger.info("  Batchsize = %d", train_config["batch_size"])
        #  logger.info("  Gradient Accumulation steps = %d", gradient_accumulation_steps)
        #  logger.info("  Total optimization steps = %d", t_total)

        self.model.zero_grad()
        for current_epoch in range(epochs):
            for step, batch in enumerate(train_dataloader):
                self.model.train()
                batch = tuple(t.to(self.device) for t in batch)
                inputs = {"input_ids": batch[0], "attention_mask": batch[1], "labels": batch[2], "pos_weight": batch[3]}
                outputs = self.model(**inputs)
                loss = outputs[1]  # model outputs are always tuple in transformers (see doc)

                loss.backward()
                if (step + 1) % gradient_accumulation_steps == 0:
                    if max_grad_norm>0:
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_grad_norm)
                    optimizer.step()
                    scheduler.step()  # Update learning rate schedule
                    self.model.zero_grad()

            results = self.eval(dev_datasets)
            self.all_results["epoch_results"].append(results)

            # Save model checkpoint
            state_dict = self.model.state_dict()

            main_metric = self.config["dev"].get("main_metric", "recall")
            current_main_metric = results[main_metric]
            old_main_matric = self.all_results["epoch_results"][self.all_results["best_epoch"]][main_metric]
            # true iff result larger previous best and larger better or result smaller and larger not better
            better = (self.config["dev"].get("larger_is_better", True) ==  # == between two booleans is like not xor
                      (current_main_metric > old_main_matric)) or current_epoch == 0
            if better:
                self.all_results["best_epoch"] = current_epoch
                torch.save(state_dict, model_file)
            self.all_results["latest_epoch"] = current_epoch

            with open(os.path.join(self.model_folder, "results.json"), "w") as f:
                json.dump(self.all_results, f, indent=2)

        # load best model after training since it will be the next inference model
        state_dict = torch.load(model_file)
        self.model.load_state_dict(state_dict)

    def _create_dataset(self, dataset, is_trainset):
        all_examples = {"input_ids": [], "label": []}
        num_examples_per_skill = {}
        for skill, sentences in dataset.items():
            input_ids = self.tokenizer.batch_encode_plus(sentences, add_special_tokens=True,
                                                         max_length=self.config["model"]["max_length"],
                                                         return_token_type_ids=False,
                                                         return_attention_masks=False)["input_ids"]
            label = self.all_skills.index(skill)
            labels = [label]*len(input_ids)
            all_examples["input_ids"].append(input_ids)
            all_examples["label"].append(labels)
            num_examples_per_skill[skill] = len(labels)
        if is_trainset:
            total_examples = sum(num_examples_per_skill.values())
            for i, skill in enumerate(self.all_skills):
                if skill in num_examples_per_skill:
                    self.skill_weights[i] = (total_examples-num_examples_per_skill[skill])/num_examples_per_skill[skill]
            dataset = CustomDataset([example for examples in all_examples["input_ids"] for example in examples],
                                    [label for labels in all_examples["label"] for label in labels])
            self.all_results["trainset_size"] = num_examples_per_skill
        else:
            dataset = [CustomDataset(examples,  labels)
                       for examples, labels in zip(all_examples["input_ids"], all_examples["label"])]
            self.all_results["devset_size"] = num_examples_per_skill
        return dataset

    def eval(self, datasets):
        self.model.eval()
        eval_config = self.config["dev"]
        results_all = defaultdict(lambda: list())
        results_all["skills"] = {}
        confusion_matrix = [[0]*len(self.all_skills) for _ in self.all_skills]
        activation_mean = [[0]*len(self.all_skills) for _ in self.all_skills]

        for i, dataset in enumerate(datasets):
            skill_label = dataset[0][1]
            skill = self.all_skills[skill_label]
            dataloader = DataLoader(dataset, shuffle=False, batch_size=eval_config["batch_size"],
                                    collate_fn=self._collate)
            ranks = []
            average_precisions = []
            activation = []
            for batch in dataloader:
                batch = tuple(t.to(self.device) for t in batch[:2])
                inputs = {"input_ids": batch[0], "attention_mask": batch[1]}
                with torch.no_grad():
                    outputs = self.model(**inputs)[0].cpu().numpy()
                for res in outputs:
                    rank = 0
                    precisions = 0
                    activation.append(res)
                    ranking = np.argsort(res)[::-1]
                    confusion_matrix[skill_label][ranking[0]] += 1
                    for j, answer in enumerate(ranking, start=1):
                        if answer == skill_label:
                            if rank == 0:
                                rank = j
                            precisions = 1 / float(j)
                    ranks.append(rank)
                    average_precisions.append(precisions)
            recall_3 = len([a for a in ranks if a <= 3 and a != 0])
            recall_5 = len([a for a in ranks if a <= 5 and a != 0])
            results = {
                'mrr': np.mean([1 / float(r) if r>0 else 0 for r in ranks]),
                'r@3': recall_3/float(len(ranks)),
                'r@5': recall_5/float(len(ranks))
            }
            activation = np.array(activation)
            activation_mean[skill_label] = np.mean(activation, axis=0).tolist()
            for key, value in results.items():
                results_all[key].append(value)
            results_all["skills"][skill] = results

        results_all["confusion_matrix"] = confusion_matrix
        results_all["activation_mean"] = activation_mean

        precision, recall, f1 = self._compute_f1(confusion_matrix)
        for dataset in datasets:
            skill = self.all_skills[dataset[0][1]]
            idx = self.all_skills.index(skill)
            results = results_all["skills"][skill]
            results["precision"] = precision[idx]
            results["recall"] = recall[idx]
            results["f1"] = f1[idx]
            results_all["precision"].append(precision[idx])
            results_all["recall"].append(recall[idx])
            results_all["f1"].append(f1[idx])

        for key in ["precision", "recall", "f1", "mrr", "r@3", 'r@5']:
            results_all[key] = np.mean(results_all[key])

        return results_all

    @staticmethod
    def _compute_f1(confusion_matrix):
        matrix = np.array(confusion_matrix)
        relevant = np.sum(matrix, axis=1)
        retrieved = np.sum(matrix, axis=0)
        precision, recall, f1 = [], [], []
        for i, val in enumerate(np.diag(matrix)):
            if retrieved[i]==0:
                p=0
            else:
                p = val/retrieved[i]
            if relevant[i]==0:
                r=0
            else:
                r = val/relevant[i]
            precision.append(p)
            recall.append(r)
            if r==0 or p==0:
                f1.append(0)
            else:
                f1.append((2*r*p)/(r+p))
        return precision, recall, f1

    def _collate(self, samples):
        input_ids, labels = zip(*samples)
        max_len = min(self.config["model"]["max_length"], max([len(input) for input in input_ids]))
        attention_mask = [[1]*len(input)+[0]*(max_len-len(input)) for input in input_ids]
        input_ids = [input+[0]*(max_len-len(input)) for input in input_ids]
        pos_weights = torch.FloatTensor(self.skill_weights)
        one_hot_labels = torch.FloatTensor(len(labels), len(self.config["all_skills"])) \
            .zero_() \
            .scatter_(1, torch.Tensor(labels).long().unsqueeze(1), 1)
        input_ids = torch.tensor(input_ids, dtype=torch.long)
        attention_mask = torch.tensor(attention_mask, dtype=torch.long)

        return input_ids, attention_mask, one_hot_labels, pos_weights

    def inference(self, sentence):
        tokenized = self.tokenizer.batch_encode_plus([sentence], add_special_tokens=True,
                                                     max_length=self.config["model"]["max_length"],
                                                     return_token_type_ids=False, return_attention_masks=True)
        input_ids = torch.tensor(tokenized["input_ids"], dtype=torch.long).to(self.device)
        attention_mask = torch.tensor(tokenized["attention_mask"], dtype=torch.long).to(self.device)

        inputs = {"input_ids": input_ids, "attention_mask": attention_mask}
        with torch.no_grad():
            scores = self.model(**inputs)[0].cpu().tolist()[0]
        score_dict = {skill_id: score for skill_id, score in zip(self.all_skills, scores)
                      if skill_id not in self.ignore_list}
        return score_dict


class ModelManager:
    def __init__(self):
        self.inference_config = {}
        self.train_config = {}
        self.ignore_list = set()
        self.inference_model = None
        self.inference_executor = None
        self.training_executor = ThreadPoolExecutor(max_workers=1)
        self.max_num_stored_models = -1

    def init(self, config):
        self.inference_executor = ThreadPoolExecutor(max_workers=config.get("max_inference_threads", 3))
        self.train_config = config["model_config"]
        self.max_num_stored_models = config.get("max_num_stored_models", 0)
        skills = Skill.query.filter(Skill.is_published == False).all()
        # need to be initialized with DB and not empty for case of unpublished skill with no retraining since
        self.ignore_list = {skill.id for skill in skills}
        newest_model = TransformerModelDB.query.with_entities(TransformerModelDB.model_folder)\
            .order_by(desc(TransformerModelDB.training_timestamp)).first()
        self.inference_model = TransformerModel(newest_model.model_folder, self.ignore_list)
        db.session.remove()

    async def train(self, id):
        logger.info("Training new model with new skill {}".format(id))
        new_ignore_list = set(self.ignore_list)
        new_ignore_list.remove(id)
        train_config = deepcopy(self.train_config)
        model_timestamp = datetime.datetime.now()
        model_folder = os.path.join(self.train_config["model_folder"], model_timestamp.strftime("%Y-%m-%d_%H-%M"))
        os.makedirs(model_folder, exist_ok=True)
        train_config["model_folder"] = model_folder
        train_config["make_new_model"] = True
        # load dev & train data for all published skills and for new skill with given id
        sentences = db.session.query(SkillExampleSentence, Skill) \
            .with_entities(SkillExampleSentence.skill_id, SkillExampleSentence.is_dev, SkillExampleSentence.sentence)\
            .filter(Skill.id==SkillExampleSentence.skill_id)\
            .filter(or_(Skill.is_published==True, Skill.id==id)).all()
        train_dataset = defaultdict(lambda: list())
        dev_dataset = defaultdict(lambda: list())
        for (sent_id, is_dev, sent) in sentences:
            if is_dev:
                dev_dataset[sent_id].append(sent)
            else:
                train_dataset[sent_id].append(sent)
        all_skills = list(train_dataset.keys())
        train_config["all_skills"] = all_skills
        train_model = TransformerModel(train_config, new_ignore_list)
        try:
            await asyncio.get_running_loop().run_in_executor(self.training_executor, train_model.train, train_dataset, dev_dataset)
        except Exception as e:
            logger.warning("Failed to train new model with new skill {}.\n{}".format(id, e))
            raise e
        logger.info("Finished training new model with new skill {}".format(id))
        db.sesssion.add(TransformerModelDB(model_folder, model_timestamp))
        if self.max_num_stored_models > 0 and db.session.query(func.count(TransformerModelDB.id)).scalar() > self.max_num_stored_models:
            oldest_model = TransformerModelDB.query.order_by(asc(TransformerModelDB.training_timestamp)).first()
            db.session.delete(oldest_model)
            shutil.rmtree(oldest_model.model_folder)
            logger.info("Storing more than {} models. Deleting the oldest at {}".format(self.max_num_stored_models,
                                                                                        oldest_model.model_folder))
        db.session.commit()
        db.session.remove()
        self.inference_model = train_model
        self.ignore_list = new_ignore_list

    def unpublish(self, id):
        self.ignore_list.add(id)
        self.inference_model.ignore_list.add(id)
        logger.info("Added {} to ignore list".format(id))

    async def scores(self, question):
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(self.inference_executor, self.inference_model.inference, [question])
        return result
