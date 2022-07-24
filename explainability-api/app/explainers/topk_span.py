import torch
from datasets import load_dataset
import numpy as np
import random
import json

try:
    from .utils import * 
except Exception as ex:
    from utils import * 

def topk_tokens(model, tokenizer, question, context, answer, answer_start, answer_end, sep_token, gradient_way = "simple", topk = 5):

    inputs = tokenizer(question, context, return_tensors="pt")
    tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
    sep_index = tokens.index(sep_token)
    saliencies, start, end = interpret(model, gradient_way, inputs, answer_start, answer_end)
    saliencies[0:sep_index+1] = [0] * len(saliencies[0:sep_index+1])
    indexes = []
    max_sal = []
    max_tokens = []
    for i in range(len(saliencies)):
        max_index = np.argmax(saliencies)
        indexes.append(int(max_index))
        max_tokens.append(tokens[max_index])
        max_sal.append(inputs.input_ids[0][max_index])
        saliencies[max_index] = 0
        if len(max_sal) >= topk:
            break
    max_sal = torch.tensor(max_sal)
    new_context = tokenizer.decode(max_sal, skip_special_tokens = True)
    inputs = tokenizer(question, new_context, return_tensors="pt")
    new_answer, start, end = get_answer(model, tokenizer, inputs)

    if len(new_answer.strip()) <= 0:
        new_answer = "Undefined Answer"
    return_dict = {
        "question": question.lower(),
        "context" : context.lower(),
        "answer" : answer,
        "tokens" : max_tokens,
        "indexes" : indexes,
        "new_context" : new_context,
        "new_answer": new_answer
    } 
    return return_dict

def tokens_span(model, tokenizer, question, context, answer, answer_start, answer_end, sep_token, gradient_way = "simple", window = 5):

    inputs = tokenizer(question, context, return_tensors="pt")
    tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
    sep_index = tokens.index(sep_token)
    saliencies, start, end = interpret(model, gradient_way, inputs, answer_start, answer_end)
    saliencies[0:sep_index+1] = [0] * len(saliencies[0:sep_index+1])

    high = 0
    for i in range(len(saliencies)- window):
        j = i + window
        temp = sum(saliencies[i:j])
        if temp > high:
            high = temp
            start_span = i
            end_span = j

    new_context = tokenizer.decode(inputs.input_ids[0][start_span:end_span], skip_special_tokens = True)
    inputs = tokenizer(question, new_context, return_tensors="pt")
    new_answer, start, end = get_answer(model, tokenizer, inputs)
    if len(new_answer.strip()) <= 0:
        new_answer = "Undefined Answer"

    return_dict = {
        "question": question.lower(),
        "context" : context.lower(),
        "answer" : answer,
        "new_context" : new_context,
        "new_answer": new_answer,
        "span" : [start_span, end_span]
    } 
    return return_dict
    

def do_topk_tokens(args):
    model, tokenizer, sep_token = get_model_tokenizer(args)
    if type(args["question"]) != list:
        inputs = tokenizer(args["question"], args["context"], return_tensors="pt")
        answer, start, end = get_answer(model, tokenizer, inputs)
        response = topk_tokens(model, tokenizer, args["question"], args["context"], answer, start, end, sep_token, 
                gradient_way = args["gradient_way"], topk = args["topk"])
    else:
        response = []
        for i in range(len(args["question"])):
            inputs = tokenizer(args["question"][i], args["context"][i], return_tensors="pt")
            answer, start, end = get_answer(model, tokenizer, inputs)
            response_ = topk_tokens(model, tokenizer, args["question"][i], args["context"][i], answer, start, end, sep_token, 
                gradient_way = args["gradient_way"], topk = args["topk"])
            response.append(response_)
    #response = json.dumps(response, indent = 4)
    return response

def do_tokens_span(args):
    model, tokenizer, sep_token = get_model_tokenizer(args)
    if type(args["question"]) != list:
        inputs = tokenizer(args["question"], args["context"], return_tensors="pt")
        answer, start, end = get_answer(model, tokenizer, inputs)
        response = tokens_span(model, tokenizer, args["question"], args["context"], answer, start, end, sep_token, 
                gradient_way = args["gradient_way"], window = args["window"])
    else:
        response = []
        for i in range(len(args["question"])):
            inputs = tokenizer(args["question"][i], args["context"][i], return_tensors="pt")
            answer, start, end = get_answer(model, tokenizer, inputs)
            response_ = tokens_span(model, tokenizer, args["question"][i], args["context"][i], answer, start, end, sep_token, 
                gradient_way = args["gradient_way"], window = args["window"])
            response.append(response_)
    #response = json.dumps(response, indent = 4)
    return response



if __name__ == '__main__':

    squad = load_dataset("squad", split = "validation")
    args = {
        "gradient_way" : "simple",
        "model_name" : "bert-base-uncased",
        "adapter" : "AdapterHub/bert-base-uncased-pf-squad_v2",
        "question" : [squad[0]['question'], squad[1]['question']],
        "context" : [squad[0]['context'], squad[1]['context']],
        #"question" : squad[0]['question'],
        #"context" : squad[0]['context'],
        "include_answer" : False,
        "topk": 15,
        "window" : 20
    }

    response = do_topk_tokens(args)
    write_to_file(response, "topk_squad.json")
    
    response = do_tokens_span(args)
    write_to_file(response, "tokens_span_squad.json")



    
    


