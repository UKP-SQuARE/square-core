from typing import List, Dict, Tuple
import random


class Hotflip:
    def __init__(self, tokenizer, top_k=10, include_answer=False):

        self.tokenizer = tokenizer
        self.top_k = top_k
        self.include_answer = include_answer

    def flip_tokens(self, model_outputs, ans_start, ans_end) -> Tuple[List[List], List]:
        """
        post-process the word attributions to merge the sub-words tokens
        to words
        Args:
            model_outputs: word importance scores
            ans_start:
            ans_end:
        Returns:
           Tuple of flipped inputs and the largest indices
        """
        attributions = model_outputs["attributions"][0]
        context_attributions = attributions["context_tokens"]
        question_attributions = attributions["question_tokens"]

        if not self.include_answer:
            proc_context = [
                word
                for word in context_attributions
                if word[0] < ans_start or word[0] > ans_end
            ]
        else:
            proc_context = context_attributions
        imp_tokens_idx = [
            i
            for i, k, v in sorted(proc_context, key=lambda item: item[2], reverse=True)[
                : self.top_k
            ]
        ]

        # randomly choose max_tokens; save memory
        max_tokens = 5000
        vocab = random.sample(list(self.tokenizer.get_vocab().keys()), max_tokens)
        # ignore non-alphanumeric words for replacement
        invalid_replacement_indices = []
        for word in vocab:
            if not word.isalnum():
                invalid_replacement_indices.append(word)

        replacement_tokens = self._get_random_tokens(
            proc_context, vocab, invalid_replacement_indices,
        )

        new_contexts = []
        tmp_attributions = context_attributions
        for value in range(self.top_k):
            token_to_replace = replacement_tokens[value]
            token_idx = imp_tokens_idx[value]
            context = [
                (token[0], token_to_replace)
                if token[0] == token_idx
                else (token[0], token[1])
                for token in tmp_attributions
            ]
            tmp_attributions = context
            context_text = " ".join([token[1] for token in tmp_attributions])
            new_contexts.append(context_text)

        old_context = [" ".join([word[1] for word in context_attributions])]
        questions = [" ".join([w[1] for w in question_attributions])] * (self.top_k + 1)
        prepared_inputs = [
            [q, c] for q, c in zip(questions, old_context + new_contexts)
        ]

        return prepared_inputs, imp_tokens_idx

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
        for _ in range(self.top_k):
            new_token = random.choice(vocab)
            while (
                new_token in tokens
                or new_token in already_generated
                or new_token in invalid_replacement_indices
                or "#" in new_token
                or len(new_token) < 3
            ):
                new_token = random.choice(vocab)
            already_generated.append(new_token)
            replacement_tokens.append(new_token.replace("Ġ", ""))
        return replacement_tokens

    # def _first_order_taylor(self, grad: numpy.ndarray, token_idx: torch.Tensor, sign: int) -> int:
    #     """
    #     The below code is based on
    #     https://github.com/pmichel31415/translate/blob/paul/pytorch_translate/
    #     research/adversarial/adversaries/brute_force_adversary.py
    #     Replaces the current token_idx with another token_idx to increase the loss. In particular, this
    #     function uses the grad, alongside the embedding_matrix to select the token that maximizes the
    #     first-order taylor approximation of the loss.
    #     """
    #     grad = util.move_to_device(torch.from_numpy(grad), self.cuda_device)
    #     if token_idx.size() != ():
    #         # We've got an encoder that only has character ids as input.  We don't curently handle
    #         # this case, and it's not clear it's worth it to implement it.  We'll at least give a
    #         # nicer error than some pytorch dimension mismatch.
    #         raise NotImplementedError(
    #             "You are using a character-level indexer with no other indexers. This case is not "
    #             "currently supported for hotflip. If you would really like to see us support "
    #             "this, please open an issue on github."
    #         )
    #     if token_idx >= self.embedding_matrix.size(0):
    #         # This happens when we've truncated our fake embedding matrix.  We need to do a dot
    #         # product with the word vector of the current token; if that token is out of
    #         # vocabulary for our truncated matrix, we need to run it through the embedding layer.
    #         inputs = self._make_embedder_input([self.vocab.get_token_from_index(token_idx.item())])
    #         word_embedding = self.embedding_layer(inputs)[0]
    #     else:
    #         word_embedding = torch.nn.functional.embedding(
    #             util.move_to_device(torch.LongTensor([token_idx]), self.cuda_device),
    #             self.embedding_matrix,
    #         )
    #     word_embedding = word_embedding.detach().unsqueeze(0)
    #     grad = grad.unsqueeze(0).unsqueeze(0)
    #     # solves equation (3) here https://arxiv.org/abs/1903.06620
    #     new_embed_dot_grad = torch.einsum("bij,kj->bik", (grad, self.embedding_matrix))
    #     prev_embed_dot_grad = torch.einsum("bij,bij->bi", (grad, word_embedding)).unsqueeze(-1)
    #     neg_dir_dot_grad = sign * (prev_embed_dot_grad - new_embed_dot_grad)
    #     neg_dir_dot_grad = neg_dir_dot_grad.detach().cpu().numpy()
    #     # Do not replace with non-alphanumeric tokens
    #     neg_dir_dot_grad[:, :, self.invalid_replacement_indices] = -numpy.inf
    #     best_at_each_step = neg_dir_dot_grad.argmax(2)
    #     return best_at_each_step[0].data[0]
