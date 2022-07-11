from transformers import BertTokenizer, BertForQuestionAnswering
import torch
from datasets import load_dataset
from torch.nn.functional import normalize
import numpy as np
import random

torch.manual_seed(0)
random.seed(0)
np.random.seed(0)


from transformers import (
    AutoTokenizer,
    BertAdapterModel,
    RobertaAdapterModel
)


def get_gradients(model, inputs, start, end):
    """Function to calculate the gradients of the input tokens

    args:
        inputs : encoded input using hugginface tokenizer
        start : answer start token index in the input
        end : answer end token index in the input
    return:
        embedding_gradient : gradient of each token
        start_ = predicted starting token index
        end_ = predicted ending token index
    """
    embedding_gradients = []
    answer_start = torch.tensor([start])
    answer_end = torch.tensor([end])
    def grad_hook(module, grad_in, grad_out):
        embedding_gradients.append(grad_out[0])
    embedding = model.bert.embeddings.word_embeddings
    handle = embedding.register_full_backward_hook(grad_hook)
    outputs = model(**inputs, start_positions=answer_start, end_positions=answer_end)
    start_ = torch.argmax(outputs.start_logits).item()
    end_ = torch.argmax(outputs.end_logits).item()
    loss = outputs.loss
    loss.backward()
    handle.remove()
    return embedding_gradients,start_,end_ 

def simple_gradient(model, inputs, start, end):
    """Function to get the saliency, start index and end index of the predicted answer using simple gradient

    args:
        inputs : encoded input using hugginface tokenizer
        start : answer start token index in the input
        end : answer end token index in the input
    return:
        saliency : saliency score of each token
        start_ = predicted starting token index
        end_ = predicted ending token index
    """
    forward_embeddings = []
    def forward_hook(module, inputs, outputs):
        forward_embeddings.append(outputs)
    embedding = model.bert.embeddings.word_embeddings
    handle = embedding.register_forward_hook(forward_hook)
    gradients, start_, end_ = get_gradients(model, inputs, start, end)
    handle.remove()
    saliency = dot_and_normalize(gradients[0], forward_embeddings[0])
    return saliency, start_, end_

def integreted_gradient(model, inputs, start, end):
    """Function to get the saliency, start index and end index of the predicted answer using integreted gradient

    args:
        inputs : encoded input using hugginface tokenizer
        start : answer start token index in the input
        end : answer end token index in the input
    return:
        saliency : saliency score of each token
        start_ = predicted starting token index
        end_ = predicted ending token index
    """
    grads = []
    for alpha in np.linspace(0, 1, num=10):
        def hook(module, inputs, outputs):
            outputs.mul_(torch.tensor(alpha))
        embedding = model.bert.embeddings.word_embeddings
        if alpha == 0.0 :
            forward_embeddings = embedding(inputs.input_ids)
        handle = embedding.register_forward_hook(hook)
        gradients, start_, end_ = get_gradients(model, inputs, start, end)
        grads.append(gradients)        
        handle.remove()
    
    for i in range(len(grads)):
        if i == 0:
            sum_tensor = grads[i][0]
        else:
            sum_tensor = torch.add(sum_tensor, grads[i][0])
    gradients = sum_tensor / float(len(grads))
    saliency = dot_and_normalize(gradients, forward_embeddings)
    return saliency, start_, end_

def smooth_gradient(model, inputs, start, end):
    """Function to get the saliency, start index and end index of the predicted answer using smooth gradient

    args:
        inputs : encoded input using hugginface tokenizer
        start : answer start token index in the input
        end : answer end token index in the input
    return:
        saliency : saliency score of each token
        start_ = predicted starting token index
        end_ = predicted ending token index
    """
    grads = []
    stdev = 0.01
    for i in range(10):
        def hook(module, inputs, outputs):
            noise = torch.randn(outputs.shape, device=outputs.device) * stdev
            outputs.add_(torch.tensor(noise))
        embedding = model.bert.embeddings.word_embeddings
        if i == 0:
            forward_embeddings = embedding(inputs.input_ids)
        handle = embedding.register_forward_hook(hook)
        gradients, start_, end_ = get_gradients(model, inputs, start, end)
        grads.append(gradients)        
        handle.remove()
    for i in range(len(grads)):
        if i == 0:
            sum_tensor = grads[i][0]
        else:
            sum_tensor = torch.add(sum_tensor, grads[i][0])
    gradients = sum_tensor / float(len(grads))
    saliency = dot_and_normalize(gradients, forward_embeddings)
    return saliency, start_, end_

def interpret(model, gradient_way, inputs, start, end):
    """Function to get the saliency, start index and end index of the predicted answer using specified gradient calculation technique

    args:
        gradient_way : gradient calculation technique (simple or integreted or smooth)
        inputs : encoded input using hugginface tokenizer
        start : answer start token index in the input
        end : answer end token index in the input
    return:
        saliency : saliency score of each token
        start_ = predicted starting token index
        end_ = predicted ending token index
    """
    if gradient_way == "simple":
        saliency, start_, end_ = simple_gradient(model, inputs, start, end)
    elif gradient_way == "integreted":
        saliency, start_, end_ = integreted_gradient(model, inputs, start, end)
    elif gradient_way == "smooth":
        saliency, start_, end_ = smooth_gradient(model, inputs, start, end)
    
    return saliency, start_, end_


def dot_and_normalize(gradients, forward_embeddings):
    """Function to calculate the saliency scores of the input tokens

    args:
        gradients : gradients of the tokens
        forward_embeddings : token embeddings extracted from the embedding layer
    
    return:
        l1_normalized_scores : for each of the tokens its gradient and embeddings is 
                               element wise multiplied then L1 norm is applied. After 
                               calculating each of the tokens saliency scores, normalization
                               is applied.
    """
    l1_normalized_scores = []
    for i in range(gradients[0].shape[0]):
        grad = gradients[0][i].view(1,gradients[0].shape[1])
        input_emb = forward_embeddings[0][i].view(1, gradients[0].shape[1])
        dot_products = torch.mul(grad,input_emb)[0]
        l1_norm = torch.norm(dot_products, dim=0)
        l1_norm = l1_norm.item()
        #l1_norm = float("{:.2f}".format(l1_norm))
        l1_normalized_scores.append(l1_norm)
    normalization_factor = sum(l1_normalized_scores)
    #normalization_factor = float("{:.2f}".format(normalization_factor))
    for i in range(len(l1_normalized_scores)):
        l1_normalized_scores[i] = l1_normalized_scores[i]/normalization_factor
        l1_normalized_scores[i] = float("{:.3f}".format(l1_normalized_scores[i]))
    return l1_normalized_scores
    
def get_max(saliencies, chosen_tokens):
    #to get the index with maximum saliency score in context
    max_index = np.argmax(saliencies)
    while chosen_tokens[max_index] == 1 or chosen_tokens[max_index] == 2:
        saliencies[max_index] = 0
        max_index = np.argmax(saliencies)
    chosen_tokens[max_index] = 1
    return saliencies, chosen_tokens, max_index

def get_random_token(tokens, already_generated, tokenizer):
    #generate a random token id between 10000 and 20000
    number = random.randint(10000, 20000)
    token = tokenizer.convert_ids_to_tokens(number)[0]
    while token in tokens or number in already_generated or "#" in token or len(token) < 3:
        number = random.randint(10000, 20000)
        token = tokenizer.convert_ids_to_tokens(number)
    already_generated.append(number)
    return number, token, already_generated

def saliency(model, question, context, answer_start, answer_end, gradient_way = 'simple'):
    try:
        inputs = tokenizer(question, context, return_tensors="pt")
        tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
        saliencies, _, _ = interpret(model, gradient_way, inputs, answer_start, answer_end)
        for saliency, token in zip(saliencies, tokens):
            print(token + " : "+str(saliency))
    except Exception as ex:
        print(ex)

def hotflip(model, tokenizer, question, context, answer, answer_start, answer_end, sep_token, 
            include_answer = False, gradient_way = 'simple', number_of_flips = None):

    already_generated = []
    inputs = tokenizer(question, context, return_tensors="pt")
    tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
    chosen_tokens = [0] * len(tokens)
    sep_index = tokens.index(sep_token)
    if include_answer == False:
        chosen_tokens[answer_start:answer_end+1] = [2] * len(chosen_tokens[answer_start:answer_end+1])
    answer_tokens = tokens[answer_start:answer_end+1]
    saliencies, start_index, end_index = interpret(model, gradient_way, inputs, answer_start, answer_end)
    saliencies[0:sep_index+1] = [0] * len(saliencies[0:sep_index+1])
    
    flips = []
    steps = 0
    while tokens[start_index:end_index+1] == answer_tokens:
        saliencies, chosen_tokens, max_index = get_max(saliencies, chosen_tokens)
        random_token_id, random_token, already_generated = get_random_token(tokens, already_generated, tokenizer)
        actual_word = tokens[max_index]
        inputs['input_ids'][0][max_index] = random_token_id
        tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
        flips.append((actual_word, random_token))
        saliencies, start_index, end_index = interpret(model, gradient_way, inputs, answer_start, answer_end)
        saliencies[0:sep_index+1] = [0] * len(saliencies[0:sep_index+1])
        new_answer = tokenizer.decode(tokenizer.convert_tokens_to_ids(tokens[start_index:end_index+1]), skip_special_tokens = True)
        actual_answer = tokenizer.decode(tokenizer.convert_tokens_to_ids(answer_tokens))
        print("Step : "+str(steps+1))
        print("New answer : ")
        if len(new_answer.strip()) > 0:
            print(new_answer)
        else:
            print("Undefined Answer")
        print("Actual Answer : ")
        print(actual_answer)  
        steps = steps + 1
        if number_of_flips != None and steps == number_of_flips:
            break
        
    return_dict = {
        "question": question.lower(),
        "context" : context.lower(),
        "model_answer" : answer,
        "flips" : flips,
        "total_flips": len(flips)
    }

    return return_dict

def get_answer(model, tokenizer, inputs):
    outputs = model(**inputs)
    start = torch.argmax(outputs.start_logits).item()
    end = torch.argmax(outputs.end_logits).item()
    answer_token_ids = inputs.input_ids[0][start:end+1]
    answer = tokenizer.convert_ids_to_tokens(answer_token_ids)
    answer = tokenizer.decode(tokenizer.convert_tokens_to_ids(answer), skip_special_tokens = True)
    return answer, torch.tensor([start]), torch.tensor([end])

def get_model_tokenizer(args):
    if args["model_name"] == 'bert-base-uncased':
        model = BertAdapterModel.from_pretrained(args["model_name"])
    tokenizer = AutoTokenizer.from_pretrained(args["model_name"])
    adapter_name = model.load_adapter(args["adapter"], source="hf")
    model.active_adapters = adapter_name
    model.eval()
    if args["model_name"] == 'bert-base-uncased':
        sep_token = '[SEP]'
    elif "roberta" in args["model_name"]:
        sep_token = '</s>'
    return model, tokenizer, sep_token

def do_hotflip(args):
    model, tokenizer, sep_token = get_model_tokenizer(args)
    inputs = tokenizer(args["question"], args["context"], return_tensors="pt")
    answer, start, end = get_answer(model, tokenizer, inputs)
    hotflip_response = hotflip(model, tokenizer, args["question"], args["context"], answer, start, end, sep_token, 
                include_answer = args["include_answer"], gradient_way = args["gradient_way"], number_of_flips = args['number_of_flips'])
    return hotflip_response


if __name__ == '__main__':

    squad = load_dataset("squad", split = "validation")
    args = {
        "model_name" : "bert-base-uncased",
        "adapter" : "AdapterHub/bert-base-uncased-pf-squad_v2",
        "question" : squad[0]['question'],
        "context" : squad[0]['context'],
        "gradient_way" : "integreted",
        "include_answer" : False,
        "number_of_flips" : None,
    }
    print(do_hotflip(args))


    
    


