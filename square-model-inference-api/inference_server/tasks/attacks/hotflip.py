from typing import List, Dict, Tuple
import random
import torch
import numpy as np
import string
from tasks.attacks.attack import Attacker
from transformers.models.gpt2.tokenization_gpt2 import bytes_to_unicode


from nltk.corpus import stopwords, words
stop_words = stopwords.words('english')
#special = ["@@NULL@@", ".", ",", ";", "!", "?", "[MASK]", "[SEP]", "[CLS]", "[PAD]", "<s>", "</s>"]
valid_words = set(words.words())



class Hotflip(Attacker):
    """
    Flips the tokens in the input text and returns the flipped text
    """

    def __init__(self, task, request, model_outputs, tokenizer, grads, embeddings, model_type, word_mappings, include_answer=False):
        """
        Initialize the Hotflip attack
        Args:
            task: task object
            request: request object
            model_outputs: model outputs
            tokenizer : tokenizer of the model
            grads : gradients of the each input tokens
            embeddings : embedding matrix of the model
            model_type : type of the model (bert or roberta or bart)
            word_mapping : token to input word mapping 
            include_answer : if False tokens of the context won't be considered for hotlfip 
        """
        super().__init__(request, task, model_outputs)
        self.tokenizer = tokenizer
        self.include_answer = include_answer
        self.top_k = self.request.attack_kwargs.get("max_flips", 10)
        self.model_type = model_type
        self.grads = grads
        self.embeddings = embeddings
        self.word_mappings = word_mappings
        self.task = task
        
    def attack_instance(
        self, ans_start, ans_end
    ) -> Tuple[List[List], List]:  # ignore the signature
        """
        post-process the word attributions to merge the sub-words tokens
        to words
        Args:
            ans_start: start index of the answer
            ans_end: end index of the answer
        Returns:
           Tuple of flipped inputs and the largest indices
        """

        (
            question_attributions,
            context_attributions,
            _,
            _,
            _,
            _,
            _,
            _,
        ) = self._get_tokens_and_attributions()

        # first newly added section start here

        # to get the sep tokens length
        if self.model_type in ["roberta", "bart"]:
            sep_length = 2
        elif self.model_type == "bert":
            sep_length = 1

        # for question answering context is before the question for sequence the opposite
        # below we try to get the word mapping of the question and context tokens 
        context_length = len(context_attributions)
        context_start = None


        # we need to exactly know from where the context start to differentiate between 
        # question and context for extractive question answering model's the context 
        # comes after question whereas for sequence classifier models the question 
        # comes after context and we also need the word map for questions
        if self.task == "question_answering":
            context_start = len(question_attributions) + sep_length + 1
            question_word_map = self.word_mappings[0][1:context_start]
        else:
            question_word_map = self.word_mappings[0][context_length+sep_length+1:]
            context_start = 1

        # to get the word map of the context
        context_word_map = self.word_mappings[0][context_start:context_start+context_length+1]

        # first newly added section end here

        # check flip value
        if self.top_k > len(context_attributions):
            self.top_k = len(context_attributions)

        if not self.include_answer:
            proc_context = [
                word
                for word in context_attributions
                if word[0] < ans_start or word[0] > ans_end
            ]
        else:
            proc_context = context_attributions

        # imp_tokens_idx = [
        #     i
        #     for i, k, v in sorted(proc_context, key=lambda item: item[2], reverse=True)[
        #         : self.top_k
        #     ]
        # ]
    
        # vocab = self.tokenizer.get_vocab()
        # invalid_replacement_indices = []
        # for k, v in vocab.items():
        #     if k in special or k in stop_words or k.isalnum() == False:
        #         invalid_replacement_indices.append(v)      
        # replacement_tokens = self._first_order_taylor(imp_tokens_idx, proc_context, invalid_replacement_indices, context_start)


        # new_contexts = []
        # tmp_attributions = context_attributions

        # for value in range(self.top_k):
        #     token_to_replace = replacement_tokens[value]
        #     token_idx = imp_tokens_idx[value]
        #     context = [
        #         (token[0], token_to_replace)
        #         if token[0] == token_idx
        #         else (token[0], token[1])
        #         for token in tmp_attributions
        #     ]
        #     tmp_attributions = context
        #     context_text = " ".join([token[1] for token in tmp_attributions])
        #     new_contexts.append(context_text)

        # old_context = [" ".join([word[1] for word in context_attributions])]
        # questions = [" ".join([w[1] for w in question_attributions])] * (self.top_k + 1)
        # prepared_inputs = [
        #     [q, c] for q, c in zip(questions, old_context + new_contexts)
        # ]

        # batch_request = self.base_prediction_request
        # batch_request["input"] = prepared_inputs
        # batch_request["contexts"] = old_context + new_contexts

        # return batch_request, imp_tokens_idx


        # second newly added section start here
        # get the impoortant tokens indexes
        imp_tokens_idx = [
           i
           for i, k, v in sorted(proc_context, key=lambda item: item[2], reverse=True)
        ]

        # get the question tokens indexes
        question_tokens = [
           k
           for i, k, v in question_attributions
        ]

        # get the context tokens indexes
        context_tokens = [
           k
           for i, k, v in context_attributions
        ]

        # since the tokens contains the subwords of, that is why more than one subword of the 
        # same token can be in the top_k tokens of the here we try to make sure that only subword
        # taken from all the subwords of subword splitted token 
        new_imp_token_idx = []
        n = 0
        for i in range(len(imp_tokens_idx)):
            n = n  + 1
            if context_word_map[imp_tokens_idx[i]] not in new_imp_token_idx:
                new_imp_token_idx.append(context_word_map[imp_tokens_idx[i]])
            if len(new_imp_token_idx) == self.top_k:
                break
        
        # make the subword tokens of question and context full word by processing
        processed_question = self.process_tokens(question_tokens, question_word_map)
        processed_context = self.process_tokens(context_tokens, context_word_map)

        # get the invalid tokens 
        vocab = self.tokenizer.get_vocab()
        vocab = {k: v for k, v in sorted(vocab.items(), key=lambda item: item[1])}
        invalid_replacement_indices = []
        for k, v in vocab.items():
            k = k.replace("Ġ", "")
            if k.isalnum() == False or k in stop_words or (k not in valid_words and k.isnumeric() == False):
                invalid_replacement_indices.append(v)

        # get the replcement tokens for the chosen tokens   
        if self.grads == None:
            replacement_tokens = self._get_random_tokens(proc_context, vocab, invalid_replacement_indices)
        else:
            replacement_tokens = self._first_order_taylor(imp_tokens_idx[0:n], proc_context, invalid_replacement_indices, context_start)
    
        #print("\nReplacement Tokens :")
        #print(replacement_tokens)

        # get contexts with flipped tokens and use them as input
        new_contexts = []
        old_context = [" ".join([word for word in processed_context])]
        tmp_context = processed_context
        for value in range(self.top_k):
            token_to_replace = replacement_tokens[value]
            token_idx = new_imp_token_idx[value]
            tmp_context[token_idx] = token_to_replace
            context_text = " ".join([token for token in tmp_context])
            new_contexts.append(context_text)
        all_contexts = old_context
        all_contexts.extend(new_contexts)

        questions = [" ".join([w for w in processed_question])] * (self.top_k + 1)
        prepared_inputs = [
           [q, c] for q, c in zip(questions, all_contexts)
        ]

        batch_request = self.base_prediction_request
        batch_request["input"] = prepared_inputs
        batch_request["contexts"] = all_contexts

        return batch_request, new_imp_token_idx

    def _get_random_tokens(self, tokens, vocab, invalid_replacement_indices):
        """
        Function to generate a random token

        Args:
            tokens : list of all the tokens
            vocab : tokenizer
        Return:
            number : id of the token in the vocabulary
            token : token with the random id in the vocabulary
            already_generated : list of already generated tokens
        """
        already_generated = []
        tokens = [word[1] for word in tokens]
        replacement_tokens = []
        # new added section start
        words = list(vocab.keys())
        # new added section end
        for _ in range(self.top_k):
            # we only considers the words from vocab
            new_token = random.choice(words)
            while (
                new_token in tokens
                or new_token in already_generated
                or vocab[new_token] in invalid_replacement_indices
                or "#" in new_token
                or len(new_token) < 3
            ):
                new_token = random.choice(words)
            already_generated.append(new_token)
            replacement_tokens.append(new_token.replace("Ġ", ""))
        return replacement_tokens

    def _first_order_taylor(self, imp_tokens, context_tokens, invalid_replacement_indices, context_start):
        """Function to generate replacemment tokens to flip a word

            args:

                imp_tokens : indices of the important tokens of the context
                context_tokens : index, token and salienct scores of all the tokens
                invalid_replacement_indices : contains indices of the special tokens, stop words and subwords
                context_start : from where the context tokens start in grad matrix

            returns:

                replacement_tokens : replacement tokens of the topk tokens 

        """

        already_generated = []
        replacement_tokens = []

        for idx in range(len(imp_tokens)):
            i, token, v = context_tokens[idx]
            imp_tok = imp_tokens[idx]
            # add the integer to get the exact token in the gradient matrix
            grad_idx = imp_tokens[idx] + context_start
            # get the gradient
            token_grad = self.grads[0][0][grad_idx]
            token_id_in_vocab = self.tokenizer.convert_tokens_to_ids(token)
            grad_to_emb_matrix = torch.einsum("in,kj->ik", (token_grad.unsqueeze(0), self.embeddings.weight))
            # multiply the gradient of the token of domension (1, 768) and the word emebdding of the token of dimension (1 , 768)
            grad_to_word_emb = torch.einsum("in,kj->ik", (token_grad.unsqueeze(0), self.embeddings.weight[token_id_in_vocab, :].unsqueeze(0)))
            # subtract
            sub = (-1) * (grad_to_emb_matrix - grad_to_word_emb)
            sub = sub.detach().numpy()
            # replace invalid indexes with -inf
            sub[:, invalid_replacement_indices] = -np.inf
            best_index = sub.argmax(1)
            best_index = best_index.data[0]

            # when the best index is already in generated indexes we need to get the second best and so on
            while best_index in already_generated:
                # replace index with -inf to get the nex best
                sub[:, best_index] = -np.inf
                best_index = sub.argmax(1)
                best_index = best_index.data[0]
            # include the new generated token index in the already generated list
            already_generated.append(best_index)
            # append it in the replacement tokens
            replacement_token = self.tokenizer.convert_ids_to_tokens(best_index)
            replacement_tokens.append(replacement_token.replace("Ġ", ""))
        
        return replacement_tokens

    
    def process_tokens(self, tokens, word_map):
        """Function to process the tokens of question and context

        args:
            tokens : list of tokens with subwords
            word_map : list of word maps for corresponding tokens
        
        returns:
            filtered_tokens : list of processed tokens with no subwords

        """

        filtered_tokens = [tokens[0]]
        for idx, (word_idx, word) in enumerate(zip(word_map, tokens[1:])):
            word = word.replace("##", "")
            word = word.replace("Ġ", "")
            if word_idx == word_map[idx + 1] and not word == self.tokenizer.sep_token:
                filtered_tokens[-1] = f'{filtered_tokens[-1]}{word}'
            else:
                filtered_tokens.append(word)
        return filtered_tokens
