import itertools
import json
import logging
import operator
import os
from typing import List, Tuple, Union

import networkx as nx
import numpy as np
import spacy
import torch
from spacy.matcher import Matcher
from tasks.config.model_config import model_config
from tasks.inference.model import Model
from tasks.models.prediction import (
    PredictionOutput,
    PredictionOutputForGraphSequenceClassification,
)
from tasks.models.request import PredictionRequest, Task
from tqdm import tqdm
from transformers import (
    BERT_PRETRAINED_CONFIG_ARCHIVE_MAP,
    OPENAI_GPT_PRETRAINED_CONFIG_ARCHIVE_MAP,
    ROBERTA_PRETRAINED_CONFIG_ARCHIVE_MAP,
    XLNET_PRETRAINED_CONFIG_ARCHIVE_MAP,
    AutoTokenizer,
)

from .utils.modelling import qagnn, roberta
from .utils.preprocess import graph, grounding, statement


os.environ["TOKENIZERS_PARALLELISM"] = "true"

MODEL_CLASS_TO_NAME = {
    "gpt": list(OPENAI_GPT_PRETRAINED_CONFIG_ARCHIVE_MAP.keys()),
    "bert": list(BERT_PRETRAINED_CONFIG_ARCHIVE_MAP.keys()),
    "xlnet": list(XLNET_PRETRAINED_CONFIG_ARCHIVE_MAP.keys()),
    "roberta": list(ROBERTA_PRETRAINED_CONFIG_ARCHIVE_MAP.keys()),
    "lstm": ["lstm"],
}

logger = logging.getLogger(__name__)

CPNET_VOCAB = "/concept.txt"
CPNET_PATH = "/conceptnet.en.pruned.graph"
PATTERN_PATH = "/matcher_patterns.json"
ENTITIES_PATH = "/tzw.ent.npy"

LM_MODEL = "roberta-base"
MAX_NODE_NUM = 200

NUM_PROCESSES = os.getenv("NUM_PROCESSES", 16)

nlp = None
matcher = None

merged_relations = [
    "antonym",
    "atlocation",
    "capableof",
    "causes",
    "createdby",
    "isa",
    "desires",
    "hassubevent",
    "partof",
    "hascontext",
    "hasproperty",
    "madeof",
    "notcapableof",
    "notdesires",
    "receivesaction",
    "relatedto",
    "usedfor",
]
id2relation = merged_relations


class GraphTransformers(Model):
    def __init__(self, **kwargs) -> None:

        """
        Args:
            model_path: path where the model is stored
            model_name: the LM model name
            kwargs: Not used
        """
        # This assumes that a corresponding model file exists
        self.device = "cuda" if torch.cuda.is_available() and not model_config.disable_gpu else "cpu"
        self.model_path = model_config.model_path
        self.data_path = model_config.data_path
        # load matcher
        self.nlp, self.matcher = self._load_matcher()
        # load DS
        self._load_resources(self.data_path + CPNET_VOCAB)
        self._load_cpnet(self.data_path + CPNET_PATH)
        # load lm model on init
        self._load_lm()
        self._load_qagnn()
        logger.info(f"LOADED modules!")

    def _load_matcher(self):
        """
        Loads the spacy matcher with the selected
        matching patterns
        """
        nlp = spacy.load("en_core_web_sm", disable=["ner", "parser", "textcat"])
        nlp.add_pipe("sentencizer")
        with open(self.data_path + PATTERN_PATH, "r", encoding="utf8") as fin:
            all_patterns = json.load(fin)
        matcher = Matcher(nlp.vocab)
        for concept, pattern in all_patterns.items():
            matcher.add(concept, [pattern])
        logger.info("loaded matcher...")
        return nlp, matcher

    def _load_resources(self, cpnet_vocab_path):
        """
        Loads conceptnet vocab
        """
        global concept2id, id2concept
        with open(cpnet_vocab_path, "r", encoding="utf8") as fin:
            id2concept = [w.strip() for w in fin]
        concept2id = {w: i for i, w in enumerate(id2concept)}

    def _load_cpnet(self, cpnet_graph_path):
        """
        Loads the conceptnet
        """
        global cpnet, cpnet_simple
        cpnet = nx.read_gpickle(cpnet_graph_path)  # Multigraph class
        cpnet_simple = nx.Graph()  # Graph class
        for u, v, data in cpnet.edges(data=True):
            w = data["weight"] if "weight" in data else 1.0
            if cpnet_simple.has_edge(u, v):
                cpnet_simple[u][v]["weight"] += w
            else:
                cpnet_simple.add_edge(u, v, weight=w)
        # print(cpnet_simple.nodes)
        logger.info("loaded conceptnet...")

    def _load_lm(self):
        """
        Loads LM model in eval mode for relevance scoring
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_config.model_name)
        self.lm_model = roberta.RobertaForMaskedLMwithLoss.from_pretrained(model_config.model_name)
        self.lm_model.to(self.device)
        self.lm_model.eval()
        logger.info("loaded pre-trained LM...")

    def _load_qagnn(self):
        """
        Loads the QaGNN model from disk
        """
        cp_emb = [np.load(self.data_path + ENTITIES_PATH)]
        cp_emb = torch.tensor(np.concatenate(cp_emb, 1), dtype=torch.float)
        concept_num, concept_dim = cp_emb.size(0), cp_emb.size(1)

        model_state_dict, model_args = torch.load(model_config.model_path, map_location=self.device)

        # create the model template
        self.model = qagnn.LM_QAGNN(
            model_args,
            model_args.encoder,
            k=model_args.k,
            n_ntype=4,
            n_etype=model_args.num_relation,
            n_concept=concept_num,
            concept_dim=model_args.gnn_dim,
            concept_in_dim=concept_dim,
            n_attention_head=model_args.att_head_num,
            fc_dim=model_args.fc_dim,
            n_fc_layer=model_args.fc_layer_num,
            p_emb=model_args.dropouti,
            p_gnn=model_args.dropoutg,
            p_fc=model_args.dropoutf,
            pretrained_concept_emb=cp_emb,
            freeze_ent_emb=model_args.freeze_ent_emb,
            init_range=model_args.init_range,
            encoder_config={},
        )

        # load the model
        self.model.load_state_dict(model_state_dict, False)
        self.model.encoder.to(self.device)
        self.model.decoder.to(self.device)
        self.model.eval()
        logger.info("loaded QaGNN model...")

    def _prepare_input(self, input: List):
        """
        Prepares the input for the _predict method.
        Args:
             encoder_features: the features of the prompt
             generated_sequence: the generated ids

        Returns:
             the features for the model
        """
        global id2concept, concept2id, cpnet, cpnet_simple
        statements = statement.convert_to_entailment(input=input)
        grounded = grounding.ground(
            statements,
            cpnet_vocab=id2concept,
            _nlp=self.nlp,
            _matcher=self.matcher,
            num_processes=NUM_PROCESSES,
        )
        graph_adj = graph.generate_adj_data_from_grounded_concepts__use_LM(
            statements,
            grounded,
            concept2id=concept2id,
            _cpnet_vocab=id2concept,
            _cpnet=cpnet,
            _cpnet_simple=cpnet_simple,
            model=self.lm_model,
            tokenizer=self.tokenizer,
            num_processes=NUM_PROCESSES,
        )
        return statements, grounded, graph_adj

    def _truncate_seq_pair(self, tokens_a, tokens_b, max_length):
        """
        Truncates a sequence pair in place to the maximum length.
        """

        # This is a simple heuristic which will always
        # truncate the longer sequence one token at a time.
        # This makes more sense than truncating an equal percent
        # of tokens from each, since if one sequence is very
        # short then each token that's truncated likely
        # contains more information than a longer sequence.
        while True:
            total_length = len(tokens_a) + len(tokens_b)
            if total_length <= max_length:
                break
            if len(tokens_a) > len(tokens_b):
                tokens_a.pop()
            else:
                tokens_b.pop()

    def convert_features_to_tensors(self, features):
        """
        Transforms the features to tensors for the
        model
        """

        all_input_ids = torch.tensor(self.select_field(features, "input_ids"), dtype=torch.long)
        all_input_mask = torch.tensor(self.select_field(features, "input_mask"), dtype=torch.long)
        all_segment_ids = torch.tensor(self.select_field(features, "segment_ids"), dtype=torch.long)
        all_output_mask = torch.tensor(self.select_field(features, "output_mask"), dtype=torch.bool)
        all_label = torch.tensor([f.label for f in features], dtype=torch.long)
        return (
            all_input_ids,
            all_input_mask,
            all_segment_ids,
            all_output_mask,
            all_label,
        )

    def select_field(self, features, field):
        return [[choice[field] for choice in feature.choices_features] for feature in features]

    def _convert_examples_to_features(
        self,
        examples,
        max_seq_length,
        tokenizer,
        cls_token_at_end=False,
        cls_token="[CLS]",
        cls_token_segment_id=1,
        sep_token="[SEP]",
        sequence_a_segment_id=0,
        sequence_b_segment_id=1,
        sep_token_extra=False,
        pad_token_segment_id=0,
        pad_on_left=False,
        pad_token=0,
        mask_padding_with_zero=True,
    ):
        """
        Loads a data file into a list of `InputBatch`s
            `cls_token_at_end` define the location of the CLS token:
                - False (Default, BERT/XLM pattern): [CLS] + A + [SEP] + B + [SEP]
                - True (XLNet/GPT pattern): A + [SEP] + B + [SEP] + [CLS]
            `cls_token_segment_id` define the segment id associated to
                the CLS token (0 for BERT, 2 for XLNet)
        """

        class InputFeatures(object):
            def __init__(self, choices_features, label):
                self.choices_features = [
                    {
                        "input_ids": input_ids,
                        "input_mask": input_mask,
                        "segment_ids": segment_ids,
                        "output_mask": output_mask,
                    }
                    for _, input_ids, input_mask, segment_ids, output_mask in choices_features
                ]
                self.label = label

        question = examples["question"]
        endings = examples["choices"]
        contexts = [question] * len(endings)
        label_list = list(range(len(endings)))

        labels = ord(examples["answerKey"]) - ord("A") if "answerKey" in examples else 0
        label_map = {label: i for i, label in enumerate(label_list)}

        features = []
        # for ex_index, example in enumerate(tqdm(examples)):
        choices_features = []
        for ending_idx, (context, ending) in enumerate(zip(contexts, endings)):
            tokens_a = tokenizer.tokenize(context)
            tokens_b = tokenizer.tokenize(question + " " + ending)

            special_tokens_count = 4 if sep_token_extra else 3
            self._truncate_seq_pair(tokens_a, tokens_b, max_seq_length - special_tokens_count)

            # The convention in BERT is:
            # (a) For sequence pairs:
            #  tokens:   [CLS] is this jack ##son ##ville ? [SEP] no it is not . [SEP]
            #  type_ids:   0   0  0    0    0     0       0   0   1  1  1  1   1   1
            # (b) For single sequences:
            #  tokens:   [CLS] the dog is hairy . [SEP]
            #  type_ids:   0   0   0   0  0     0   0
            #
            # Where "type_ids" are used to indicate whether this is the first
            # sequence or the second sequence. The embedding vectors for `type=0` and
            # `type=1` were learned during pre-training and are added to the wordpiece
            # embedding vector (and position vector). This is not *strictly* necessary
            # since the [SEP] token unambiguously separates the sequences, but it makes
            # it easier for the model to learn the concept of sequences.
            #
            # For classification tasks, the first vector (corresponding to [CLS]) is
            # used as as the "sentence vector". Note that this only makes sense because
            # the entire model is fine-tuned.
            tokens = tokens_a + [sep_token]
            if sep_token_extra:
                # roberta uses an extra separator b/w pairs of sentences
                tokens += [sep_token]

            segment_ids = [sequence_a_segment_id] * len(tokens)

            if tokens_b:
                tokens += tokens_b + [sep_token]
                segment_ids += [sequence_b_segment_id] * (len(tokens_b) + 1)

            if cls_token_at_end:
                tokens = tokens + [cls_token]
                segment_ids = segment_ids + [cls_token_segment_id]
            else:
                tokens = [cls_token] + tokens
                segment_ids = [cls_token_segment_id] + segment_ids

            input_ids = tokenizer.convert_tokens_to_ids(tokens)

            # The mask has 1 for real tokens and 0 for padding tokens. Only real
            # tokens are attended to.

            input_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)
            special_token_id = tokenizer.convert_tokens_to_ids([cls_token, sep_token])
            output_mask = [1 if id in special_token_id else 0 for id in input_ids]  # 1 for mask

            # Zero-pad up to the sequence length.
            padding_length = max_seq_length - len(input_ids)
            if pad_on_left:
                input_ids = ([pad_token] * padding_length) + input_ids
                input_mask = ([0 if mask_padding_with_zero else 1] * padding_length) + input_mask
                output_mask = ([1] * padding_length) + output_mask

                segment_ids = ([pad_token_segment_id] * padding_length) + segment_ids
            else:
                input_ids = input_ids + ([pad_token] * padding_length)
                input_mask = input_mask + ([0 if mask_padding_with_zero else 1] * padding_length)
                output_mask = output_mask + ([1] * padding_length)
                segment_ids = segment_ids + ([pad_token_segment_id] * padding_length)

            label = label_map[labels]
            choices_features.append((tokens, input_ids, input_mask, segment_ids, output_mask))
        features.append(InputFeatures(choices_features=choices_features, label=label))

        return features

    def load_sparse_adj_data_with_contextnode(self, adj_concept_pairs, max_node_num, num_choice):
        # this is actually n_questions x n_choices
        n_samples = len(adj_concept_pairs)
        edge_index, edge_type = [], []
        adj_lengths = torch.zeros((n_samples,), dtype=torch.long)
        concept_ids = torch.full((n_samples, max_node_num), 1, dtype=torch.long)
        node_type_ids = torch.full((n_samples, max_node_num), 2, dtype=torch.long)  # default 2: "other node"
        node_scores = torch.zeros((n_samples, max_node_num, 1), dtype=torch.float)

        adj_lengths_ori = adj_lengths.clone()
        for idx, _data in tqdm(enumerate(adj_concept_pairs), total=n_samples, desc="loading adj matrices"):
            adj, concepts, qm, am, cid2score = (
                _data["adj"],
                _data["concepts"],
                _data["qmask"],
                _data["amask"],
                _data["cid2score"],
            )
            # adj: e.g. <4233x249 (n_nodes*half_n_rels x n_nodes) sparse matrix of type
            # '<class 'numpy.bool'>' with 2905 stored elements in COOrdinate format>
            # concepts: np.array(num_nodes, ), where entry is concept id
            # qm: np.array(num_nodes, ), where entry is True/False
            # am: np.array(num_nodes, ), where entry is True/False
            # concepts = np.array(list(set(concepts)))
            # TODO: should be removed after fixing the api concept2id_api ()
            assert len(concepts) == len(set(concepts))
            qam = qm | am
            # sanity check: should be T,..,T,F,F,..F
            assert qam[0] == True
            F_start = False
            for TF in qam:
                if TF == False:
                    F_start = True
                else:
                    assert F_start == False
            # this is the final number of nodes including
            # contextnode but excluding PAD
            num_concept = min(len(concepts), max_node_num - 1) + 1
            adj_lengths_ori[idx] = len(concepts)
            adj_lengths[idx] = num_concept

            # Prepare nodes
            concepts = concepts[: num_concept - 1]
            # To accomodate contextnode, original concept_ids incremented by 1
            concept_ids[idx, 1:num_concept] = torch.tensor(concepts + 1)
            # this is the "concept_id" for contextnode
            concept_ids[idx, 0] = 0

            # Prepare node scores
            if cid2score is not None:
                for _j_ in range(num_concept):
                    _cid = int(concept_ids[idx, _j_]) - 1
                    assert _cid in cid2score
                    node_scores[idx, _j_, 0] = torch.tensor(cid2score[_cid])

            # Prepare node types
            node_type_ids[idx, 0] = 3  # context node
            node_type_ids[idx, 1:num_concept][torch.tensor(qm, dtype=torch.bool)[: num_concept - 1]] = 0
            node_type_ids[idx, 1:num_concept][torch.tensor(am, dtype=torch.bool)[: num_concept - 1]] = 1

            # Load adj
            # (num_matrix_entries, ), where each entry is coordinate
            ij = torch.tensor(adj.row, dtype=torch.int64)
            # (num_matrix_entries, ), where each entry is coordinate
            k = torch.tensor(adj.col, dtype=torch.int64)
            n_node = adj.shape[1]
            half_n_rel = adj.shape[0] // n_node
            i, j = torch.div(ij, n_node, rounding_mode="floor"), ij % n_node

            # Prepare edges
            i += 2
            j += 1
            # **** increment coordinate by 1, rel_id by 2 ****
            k += 1
            extra_i, extra_j, extra_k = [], [], []
            for _coord, q_tf in enumerate(qm):
                _new_coord = _coord + 1
                if _new_coord > num_concept:
                    break
                if q_tf:
                    extra_i.append(0)  # rel from context node to question concept
                    extra_j.append(0)  # context node coordinate
                    extra_k.append(_new_coord)  # question concept coordinate
            for _coord, a_tf in enumerate(am):
                _new_coord = _coord + 1
                if _new_coord > num_concept:
                    break
                if a_tf:
                    extra_i.append(1)  # rel from context node to answer concept
                    extra_j.append(0)  # context node coordinate
                    extra_k.append(_new_coord)  # answer concept coordinate

            half_n_rel += 2  # should be 19 now
            if len(extra_i) > 0:
                i = torch.cat([i, torch.tensor(extra_i)], dim=0)
                j = torch.cat([j, torch.tensor(extra_j)], dim=0)
                k = torch.cat([k, torch.tensor(extra_k)], dim=0)

            mask = (j < max_node_num) & (k < max_node_num)
            i, j, k = i[mask], j[mask], k[mask]
            i, j, k = (
                torch.cat((i, i + half_n_rel), 0),
                torch.cat((j, k), 0),
                torch.cat((k, j), 0),
            )  # add inverse relations
            edge_index.append(torch.stack([j, k], dim=0))  # each entry is [2, E]
            edge_type.append(i)  # each entry is [E, ]

        # list of size (n_questions, n_choices), where each entry is tensor[2, E]
        # this operation corresponds to .view(n_questions, n_choices)
        edge_index = list(map(list, zip(*(iter(edge_index),) * num_choice)))
        # list of size (n_questions, n_choices), where each entry is tensor[E, ]
        edge_type = list(map(list, zip(*(iter(edge_type),) * num_choice)))

        concept_ids, node_type_ids, node_scores, adj_lengths = [
            x.view(-1, num_choice, *x.size()[1:]) for x in (concept_ids, node_type_ids, node_scores, adj_lengths)
        ]
        return (
            concept_ids,
            node_type_ids,
            node_scores,
            adj_lengths,
            (edge_index, edge_type),
        )

    def to_numpy(self, x):
        """
        Converts tensors to arrays
        """
        if type(x) is not np.ndarray:
            x = x.detach().cpu().numpy() if x.requires_grad else x.cpu().numpy()
        return x

    def _predict(self, request: PredictionRequest) -> Union[np.array, Tuple[np.array, np.array]]:
        """
        featurize data and get the model prediction
        """

        num_choices = len(request.input)
        statements, grounded, graphs = self._prepare_input(request.input)
        model_type = self.lm_model.config.model_type

        features = self._convert_examples_to_features(
            examples=statements,
            max_seq_length=request.model_kwargs.get("max_seq_length", 128),
            tokenizer=self.tokenizer,
            cls_token_at_end=bool(model_type in ["xlnet"]),  # xlnet has a cls token at the end
            cls_token=self.tokenizer.cls_token,
            sep_token=self.tokenizer.sep_token,
            sep_token_extra=bool(model_type in ["roberta", "albert"]),
            cls_token_segment_id=2 if model_type in ["xlnet"] else 0,
            pad_on_left=bool(model_type in ["xlnet"]),  # pad on the left for xlnet
            pad_token_segment_id=4 if model_type in ["xlnet"] else 0,
            sequence_b_segment_id=0 if model_type in ["roberta", "albert"] else 1,
        )
        *data_tensors, all_label = self.convert_features_to_tensors(features)

        *test_decoder_data, test_adj_data = self.load_sparse_adj_data_with_contextnode(
            graphs,
            max_node_num=request.model_kwargs.get("max_node_num", MAX_NODE_NUM),
            num_choice=num_choices,
        )

        input_data = [*data_tensors, *test_decoder_data, *test_adj_data]
        output_lm_subgraph = request.model_kwargs.get("output_lm_subgraph", False)
        topk_lm_scores = request.model_kwargs.get("topk_lm_scores", 50)
        output_attn_subgraph = request.model_kwargs.get("output_attn_subgraph", False)
        topk_attn = request.model_kwargs.get("topk_attn", 5)

        with torch.no_grad():
            if not output_attn_subgraph:
                logits, attn = self.model(*input_data)
                # return logits, self.to_numpy(attn)
            else:
                (
                    logits,
                    attn,
                    concept_ids,
                    node_type_ids,
                    edge_index_orig,
                    edge_type_orig,
                ) = self.model(*input_data, detail=output_attn_subgraph)
                # return logits, attn, concept_ids, node_type_ids

        predictions = {}
        task_outputs = {}
        # If logits dim > 1 or if the 'is_regression' flag is not set, we assume classification:
        # We replace the logits by the softmax and add labels chosen with argmax
        if logits.size()[-1] != 1:
            probabilities = torch.softmax(logits, dim=-1)
            predictions["logits"] = probabilities
            task_outputs["labels"] = torch.argmax(predictions["logits"], dim=-1).tolist()
            label_id = task_outputs["labels"][0]

        if request.model_kwargs.get("output_attentions", False):
            predictions["attentions"] = attn

        if output_lm_subgraph:
            graph = graphs[label_id]
            grounded = grounded[label_id]
            lm_subgraph = self._get_subgraphs(graph, grounded, topk_scores=topk_lm_scores)
            task_outputs["lm_subgraph"] = lm_subgraph

        if output_attn_subgraph:
            attn_subgraph = self._get_attentions_graph(
                label_id,
                attn,
                concept_ids,
                node_type_ids,
                num_choices=num_choices,
                topk_attn=topk_attn,
            )
            task_outputs["attn_subgraph"] = attn_subgraph
        return predictions, task_outputs

    def _get_edge_info(self, node_ids: list) -> dict:
        pair_list = [list(i) for i in list(itertools.product(node_ids, node_ids))]
        # edges = [
        #     cpnet[pair[0]][pair[1]][0]
        #     for pair in pair_list
        #     if cpnet_simple.has_edge(pair[0], pair[1])
        # ]
        edges = []
        linked_pairs = []
        for pair in pair_list:
            if cpnet_simple.has_edge(pair[0], pair[1]):
                edges.append(cpnet[pair[0]][pair[1]][0])
                linked_pairs.append([pair[0], pair[1]])
        edge_attributes = {}
        for i, (node_pair, edge) in enumerate(zip(linked_pairs, edges)):
            tmp_dict = dict()
            tmp_dict["source"] = node_pair[0]
            tmp_dict["target"] = node_pair[1]
            tmp_dict["weight"] = edge["weight"]
            if edge["rel"] >= len(id2relation):
                tmp_dict["label"] = id2relation[edge["rel"] - len(id2relation)]
            else:
                tmp_dict["label"] = id2relation[edge["rel"]]
            edge_attributes[i] = tmp_dict
        return edge_attributes

    def _get_subgraphs(self, graph, grounded, topk_scores: int = 50):
        """
        Get the retrieved subgraph with the LM
        relevance scores
        """

        def _get_node_info(lm_scores: dict, grounded: dict) -> dict:
            def softmax(score: float, score_map: dict):
                values = np.array(list(score_map.values()))
                sum = np.exp(values).sum()

                return np.exp(score) / sum

            node_attributes = {}
            for node_id, score in lm_scores.items():
                node = dict()
                node["id"] = node_id
                node["name"] = id2concept[node_id]
                node["q_node"] = False
                node["ans_node"] = False
                if node["name"] in grounded["qc"]:
                    node["q_node"] = True
                elif node["name"] in grounded["ac"]:
                    node["ans_node"] = True
                node["weight"] = float(softmax(float(score), lm_scores))
                node_attributes[node_id] = node
            return node_attributes

        subgraph = {"nodes": {}, "edges": {}}
        lm_scores = graph["cid2score"]
        ranked_lm_scores = dict(sorted(lm_scores.items(), key=operator.itemgetter(1), reverse=True)[:topk_scores])
        subgraph["nodes"] = _get_node_info(ranked_lm_scores, grounded)
        subgraph["edges"] = self._get_edge_info(list(ranked_lm_scores.keys()))
        # subgraph = json.dumps(subgraph, indent=4)
        # print(subgraph)
        return subgraph

    def _get_attentions_graph(
        self,
        label_id,
        attentions,
        concept_ids,
        node_type_ids,
        num_choices,
        topk_attn=10,
    ):
        """
        Gets the graphs based on highest model attentions
        to the nodes
        """

        info = dict()
        info["concept_ids"] = concept_ids.squeeze()  # (5,200)
        info["node_type_ids"] = node_type_ids.squeeze()  # (5,200)
        # 0: question node
        # 1: ans node
        # 2: extra/other nodes
        # 3: qa context node
        attn_h1 = attentions[:num_choices]
        attn_h2 = attentions[num_choices:]
        # info['attn'] = (attn_h1 + attn_h2) / 2  # (5,200)
        info["attn"] = attn_h1 + attn_h2  # (5,200)

        a_idx = [info["node_type_ids"] == 1]
        # they add 1 to concept_ids while processing,
        # so we subtract it
        a_id = set((info["concept_ids"][a_idx] - 1).tolist())
        o_idx = [info["node_type_ids"] == 2]
        o_id = set((info["concept_ids"][o_idx] - 1).tolist())
        q_idx = [info["node_type_ids"] == 0]
        q_id = set((info["concept_ids"][q_idx] - 1).tolist())

        def _get_node_info(nodes: dict, node_type_id: int) -> dict:
            node_attributes = {}
            for node_name, attn in nodes.items():
                node = dict()
                node["id"] = concept2id[node_name]
                node["name"] = node_name
                node["q_node"] = False
                node["ans_node"] = False
                if node_type_id == 0:
                    node["q_node"] = True
                elif node_type_id == 1:
                    node["ans_node"] = True
                node["weight"] = float(attn)
                node_attributes[node["id"]] = node
            return node_attributes

        def bfs_attn(target) -> dict:
            """
            do best first search to get the nodes with higher
            attentions
            """

            target_id_connected_with_source_attn = []
            for i in target:
                row_attn = []
                idx = (info["concept_ids"][label_id] == (i + 1)).nonzero()
                if idx.tolist():
                    try:
                        row_attn.append(info["attn"][label_id][idx])
                    except IndexError:
                        continue
                    target_id_connected_with_source_attn.append(row_attn)
            ranked_attn = dict()
            for t, attn in zip(target, target_id_connected_with_source_attn):
                ranked_attn[id2concept[t]] = float(attn[0][0][0])
            if "ab_extra" in ranked_attn:
                ranked_attn.pop("ab_extra")

            ranked_attn = dict(sorted(ranked_attn.items(), key=operator.itemgetter(1), reverse=True)[:topk_attn])
            return ranked_attn

        q_concepts = bfs_attn(q_id)
        o_concepts = bfs_attn(o_id)
        a_concepts = bfs_attn(a_id)
        # all_concepts = {**q_concepts, **o_concepts, **a_concepts}
        # node_type_ids
        q_nodes = _get_node_info(q_concepts, node_type_id=0)
        a_nodes = _get_node_info(a_concepts, node_type_id=1)
        o_nodes = _get_node_info(o_concepts, node_type_id=2)

        all_nodes = {**q_nodes, **a_nodes, **o_nodes}

        qo_edges = self._get_edge_info(
            [concept2id[concept] for concept in list(q_concepts.keys()) + list(o_concepts.keys())]
        )
        oa_edges = self._get_edge_info(
            [concept2id[concept] for concept in list(o_concepts.keys()) + list(a_concepts.keys())]
        )
        ao_edges = self._get_edge_info(
            [concept2id[concept] for concept in list(a_concepts.keys()) + list(o_concepts.keys())]
        )

        all_edges = {**qo_edges, **oa_edges, **ao_edges}
        attention_subgraph = {"nodes": all_nodes, "edges": all_edges}
        # attention_subgraph = json.dumps(attention_subgraph, indent=4)
        # print("attn sg: ", attention_subgraph)
        return attention_subgraph

    def _sequence_classification(self, request: PredictionRequest) -> PredictionOutput:
        """
        Classifies the given input
        Args:
             request: The request containing e.g. the input text
        Returns:
                 The prediction output containing the predicted labels
        """
        predictions, task_outputs = self._predict(request)

        return PredictionOutputForGraphSequenceClassification(model_outputs=predictions, **task_outputs)

    def predict(self, request: PredictionRequest, task: Task) -> PredictionOutput:
        if request.is_preprocessed:
            raise ValueError("is_preprocessed=True is not " "supported for this model. " "Please use text as input.")
        if len(request.input) > model_config.max_input_size:
            raise ValueError(f"Input is too large. Max input size is " f"{model_config.max_input_size}")

        if task == Task.sequence_classification:
            return self._sequence_classification(request)
