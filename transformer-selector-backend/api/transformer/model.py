from collections import defaultdict
import torch
from torch import nn
from ..models import db, SkillExampleSentence, Skill
from ..models import TransformerModel as TransformerModelDB
from sqlalchemy import desc
class TransformerModule(nn.Module):
    def __init__(self, config, bert):
        super(TransformerModel, self).__init__()
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
            # against class imbalances
            if pos_weight is None:
                pos_weight = torch.ones(logits.size()[1]).float()
            loss_fct = nn.BCEWithLogitsLoss(pos_weight=pos_weight, reduction="mean")
            loss = loss_fct(logits, labels)
            outputs = outputs + (loss,)

        return outputs  # sigmoid(logits), (loss)
import logging

logger = logging.getLogger(__name__)

class TransformerModel:
    def __init__(self, config, model_folder, ignore_list):
        self.config = config

    def train(self, train_dataset, dev_datasets):
        self.model.train()
        train_config = self.config["train"]
        train_sampler = RandomSampler(train_dataset)
        gradient_accumulation_steps = train_config.get("gradient_accumulation_steps", 1)
        train_dataloader = DataLoader(train_dataset, sampler=train_sampler,
                                      batch_size=int(train_config["batch_size"]/gradient_accumulation_steps), collate_fn=self._collate)

        epochs = train_config["epochs"]

        if train_config.get("max_steps", 0) > 0:
            t_total = train_config["max_steps"]
            epochs = train_config["max_steps"] // (len(train_dataloader) // gradient_accumulation_steps) + 1
        else:
            t_total = len(train_dataloader) // gradient_accumulation_steps * epochs

        if train_config.get("freeze_bert", False) or train_config.get("freeze_extend", False):
            logger.warning("! Freezing Bert Parameters !")
            for param in self.model.bert.parameters():
                param.requires_grad = False
            #if self.config["model"].get("version", "v1") == "v1":
            #    for param in self.model.preclass.parameters():
            #        param.requires_grad = False
        if train_config.get("freeze_extend", False):
            if self.config["model"].get("version", "v1") == "v3":
                for param in self.model.preclass1.parameters():
                    param.requires_grad = False
                for param in self.model.preclass2.parameters():
                    param.requires_grad = False
                self.model.embedding.requires_grad = False
            else:
                for param in self.model.classifier.parameters():
                    param.requires_grad = False
                if self.config["model"].get("version", "v1") == "v2":
                    for param in self.model.adapter.parameters():
                        param.requires_grad = False


        # Prepare optimizer and schedule (linear warmup and decay)
        no_decay = ["bias", "LayerNorm.weight"]
        weight_decay = train_config.get("weight_decay", 0.0)
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in self.model.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": weight_decay,
            },
            {"params": [p for n, p in self.model.named_parameters() if any(nd in n for nd in no_decay)], "weight_decay": 0.0},
        ]

        learning_rate = train_config.get("learning_rate", 5e-5)
        adam_epsilon = train_config.get("adam_epsilon", 1e-8)
        warmup_fraction = train_config.get("warmup_fraction", 0.0)
        warmup_steps = t_total*warmup_fraction
        max_grad_norm = train_config.get("max_grad_norm", 1.0)
        optimizer = AdamW(optimizer_grouped_parameters, lr=learning_rate, eps=adam_epsilon)
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=warmup_steps, num_training_steps=t_total
        )

        latest_optim = os.path.join(self.out_dir, "latest_model", "optimizer.pty")
        latest_scheduler = os.path.join(self.out_dir, "latest_model", "scheduler.pty")
        if os.path.isfile(latest_optim) and os.path.isfile(latest_scheduler):
            # Load in optimizer and scheduler states
            optimizer.load_state_dict(torch.load(latest_optim))
            scheduler.load_state_dict(torch.load(latest_scheduler))

        # Train!
        logger.info("***** Running training *****")
        logger.info("  Num examples = %d", len(train_dataset))
        logger.info("  Num Epochs = %d", epochs)
        logger.info("  Batchsize = %d", train_config["batch_size"])
        logger.info("  Gradient Accumulation steps = %d", gradient_accumulation_steps)
        logger.info("  Total optimization steps = %d", t_total)

        epochs_trained = 0
        # Check if continuing training from a checkpoint
        if self.all_results["latest_epoch"] >= 0:
            # set global_step to global_step of last saved checkpoint from model path
            epochs_trained = self.all_results["latest_epoch"]+1

            logger.info("  Continuing training from checkpoint")
            logger.info("  Continuing training from epoch %d", epochs_trained)

        tr_loss, log_loss, epoch_loss = 0.0, 0.0, 0.0
        self.model.zero_grad()
        train_iterator = trange(epochs_trained, int(epochs), desc="Epoch", position=0)
        for current_epoch in train_iterator:
            epoch_iterator = tqdm(train_dataloader, position=1, desc="Iteration")
            loss_log = tqdm(total=0, position=2, bar_format="{desc}")
            for step, batch in enumerate(epoch_iterator):
                self.model.train()
                batch = tuple(t.to(self.device) for t in batch)
                inputs = {"input_ids": batch[0], "attention_mask": batch[1], "labels": batch[2], "pos_weight": batch[3]}
                outputs = self.model(**inputs)
                loss = outputs[1]  # model outputs are always tuple in transformers (see doc)

                loss.backward()

                tr_loss += loss.item()
                if (step + 1) % gradient_accumulation_steps == 0:
                    if max_grad_norm>0:
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_grad_norm)

                    optimizer.step()
                    scheduler.step()  # Update learning rate schedule
                    self.model.zero_grad()

                if step%10 == 0:
                    l = (tr_loss-log_loss)/10
                    log_loss = tr_loss
                    loss_log.set_description_str("loss: {}".format(l))

            if dev_datasets is not None:
                logs = {}
                results = self.eval(dev_datasets, is_test=False)
                for key, value in results.items():
                    logs[key] = value
                results["epoch"] = current_epoch
                self.all_results["epoch_results"].append(results)

                # Save model checkpoint
                best_model_file = os.path.join(self.out_dir, "best_model", "model.pty")
                latest_model_file = os.path.join(self.out_dir, "latest_model", "model.pty")
                latest_optim = os.path.join(self.out_dir, "latest_model", "optimizer.pty")
                latest_scheduler = os.path.join(self.out_dir, "latest_model", "scheduler.pty")

                state_dict = self.model.state_dict()

                main_metric = self.config["dev"].get("main_metric", "accuracy")
                current_main_metric = results[main_metric]
                old_main_matric = self.all_results["epoch_results"][self.all_results["best_epoch"]][main_metric]
                # true iff result larger previous best and larger better or result smaller and larger not better
                better = (self.config["dev"].get("larger_is_better", True) ==
                          (current_main_metric > old_main_matric)) or current_epoch==0
                if better:
                    self.all_results["best_epoch"] = current_epoch
                    torch.save(state_dict, best_model_file)
                    logger.info("New best epoch result. Current epoch improves in {} from {:.4f} to {:.4f}".format(
                        main_metric, old_main_matric, current_main_metric))
                torch.save(state_dict, latest_model_file)
                logger.info("Saving latest model checkpoint")

                torch.save(optimizer.state_dict(), latest_optim)
                torch.save(scheduler.state_dict(), latest_scheduler)
                logger.info("Saving optimizer and scheduler states")
                self.all_results["latest_epoch"] = current_epoch

                with open(os.path.join(self.out_dir, "results.json"), "w") as f:
                    json.dump(self.all_results, f, indent=4)

    def eval(self, datasets):
        self.model.eval()
        if is_test:
            eval_config = self.config["test"]
        else:
            eval_config = self.config["dev"]

        results_all = defaultdict(lambda: list())
        confusion_matrix = [[0]*len(self.all_skills) for _ in self.all_skills]

        activation_mean = [[0]*len(self.all_skills) for _ in self.all_skills]
        activation_max = [[0]*len(self.all_skills) for _ in self.all_skills]
        activation_min = [[0]*len(self.all_skills) for _ in self.all_skills]
        activation_std = [[0]*len(self.all_skills) for _ in self.all_skills]

        for i, dataset in enumerate(datasets):
            skill_label = dataset[0][1]
            skill = self.all_skills[dataset[0][1]]
            dataloader = DataLoader(dataset, shuffle=False, batch_size=eval_config["batch_size"], collate_fn=self._collate)
            dataset_iterator = tqdm(dataloader, desc="Iteration ({})".format(skill))
            logger.info("Evaluating skill {}/{}: {}".format(i+1, len(datasets), skill))
            logger.info("{} questions".format(len(dataset)))
            start = datetime.datetime.now()
            ranks = []
            average_precisions = []
            activation = []
            for batch in dataset_iterator:
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
            end = datetime.datetime.now()
            time_taken = end - start
            correct_answers = len([a for a in ranks if a == 1])
            recall_3 = len([a for a in ranks if a <= 3 and a != 0])
            recall_5 = len([a for a in ranks if a <= 5 and a != 0])
            results = {
                'accuracy': correct_answers / float(len(ranks)),
                'mrr': np.mean([1 / float(r) if r>0 else 0 for r in ranks]),
                'r@3': recall_3/float(len(ranks)),
                'r@5': recall_5/float(len(ranks)),
                'query_per_second': float(len(ranks))/time_taken.total_seconds()
            }
            #activation = (activation/float(len(ranks))).tolist()
            activation = np.array(activation)
            mean = np.mean(activation, axis=0).tolist()
            max = np.max(activation, axis=0).tolist()
            min = np.min(activation, axis=0).tolist()
            std = np.std(activation, axis=0).tolist()
            activation_mean[skill_label] = mean
            activation_min[skill_label] = min
            activation_max[skill_label] = max
            activation_std[skill_label] = std
            for key, value in results.items():
                results_all[key].append(value)
            results_all[skill] = results

        results_all["confusion_matrix"] = confusion_matrix
        results_all["activation"] = {}
        results_all["activation"]["mean"] = activation_mean
        results_all["activation"]["std"] = activation_std
        results_all["activation"]["min"] = activation_min
        results_all["activation"]["max"] = activation_max

        precision, recall, f1 = self._compute_f1(confusion_matrix)
        for dataset in datasets:
            skill = self.all_skills[dataset[0][1]]
            idx = self.all_skills.index(skill)
            results = results_all[skill]
            results["precision"] = precision[idx]
            results["recall"] = recall[idx]
            results["f1"] = f1[idx]
            results_all["precision"].append(precision[idx])
            results_all["recall"].append(recall[idx])
            results_all["f1"].append(f1[idx])

            logger.info('\nResults for skill {}'.format(skill))
            self._log_results(results)

        for key in ["accuracy", "precision", "recall", "f1", "mrr", "r@3", 'r@5', "query_per_second"]:
            results_all[key] = np.mean(results_all[key])
        logger.info('\nResults for all datasets:')
        self._log_results(results_all)

        if eval_config.get("print_confusion_matrix", False):
            self._log_confusion_matrix(confusion_matrix)

        return results_all

    def inference(self, sentences):
        outputs = []
        for i in range(0, len(sentences), self.config["eval_batchsize"]):
            sents = sentences[i: i+self.config["eval_batchsize"]]
            tokenized = self.tokenizer.batch_encode_plus(sents, add_special_tokens=True, max_length=self.config["model"]["max_length"],
                                              return_token_type_ids=False, return_attention_masks=True)
            input_ids = torch.tensor(tokenized["input_ids"], dtype=torch.long).to(self.device)
            attention_mask = torch.tensor(tokenized["attention_mask"], dtype=torch.long).to(self.device)

            inputs = {"input_ids": input_ids, "attention_mask": attention_mask}
            with torch.no_grad():
                batch_outputs = self.model(**inputs)[0].cpu().numpy().list()
            outputs.extend(batch_outputs)
        return outputs

class ModelManager:
    def __init__(self, config):
        self.inference_config = config["inference"]
        self.train_config = config["train"]
        skills = Skill.query.filter(Skill.is_published == False).all()
        self.ignore_list = {skill.id for skill in skills}  # need to be initialized with DB and not empty for case of unpublished skill with no retraining since
        newest_model = TransformerModelDB.query.order_by(desc(TransformerModelDB.training_timestamp)).first()
        self.inference_model = TransformerModel(self.inference_config, newest_model.model_folder)
        db.session.remove()

    def train(self, id):
        # if training thread in progress: stop it and delete folder
        # remove id from ignore list
        # load dev & train data for all published skills and for new skill with given id
        # make datasets & dataloader
        # create folder for new model
        # create new TransformerModel and prepare config for it
        # train model on thread
        # update db with new model
        # set inference model to new model
        # remove oldest model if limit of backups is reached

    def unpublish(self, id):
        self.ignore_list.add(id)
        self.inference_model.ignore_list.add(id)
        logger.info("Added {} to ignore list".format(id))
        # set skill with id on ignore_list
        # update ignore_list of inference model
        # do not delete model -> we probably have no model that fits the remaining skills, ignoring is better

    def scores(self, question):
        scores = self.inference_model.inference([question])[0]
        score_dict = {skill_id: score for skill_id, score in zip(self.inference_model.skills, scores)
                      if skill_id not in self.ignore_list}
        return score_dict
        # calculate scores with inference model
        # return dict with skill: score, removing blacklisted skills
        # sorting, filtering etc should be done by selector in core-backend not here