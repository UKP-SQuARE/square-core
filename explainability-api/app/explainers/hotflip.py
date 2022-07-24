import torch
from datasets import load_dataset
import numpy as np
import random
import json

try:
    from .utils import * 
except Exception as ex:
    from utils import * 

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
    flipped_indexes = []
    steps = 0
    while tokens[start_index:end_index+1] == answer_tokens:
        saliencies, chosen_tokens, max_index = get_max(saliencies, chosen_tokens)
        flipped_indexes.append(int(max_index))
        random_token_id, random_token, already_generated = get_random_token(tokens, already_generated, tokenizer)
        actual_word = tokens[max_index]
        inputs['input_ids'][0][max_index] = random_token_id
        tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
        flips.append((actual_word, random_token))
        saliencies, start_index, end_index = interpret(model, gradient_way, inputs, answer_start, answer_end)
        saliencies[0:sep_index+1] = [0] * len(saliencies[0:sep_index+1])
        new_answer = tokenizer.decode(tokenizer.convert_tokens_to_ids(tokens[start_index:end_index+1]), skip_special_tokens = True)
        #actual_answer = tokenizer.decode(tokenizer.convert_tokens_to_ids(answer_tokens))
        #print("Step : "+str(steps+1))
        #print("New answer : ")
        if len(new_answer.strip()) <= 0:
           new_answer = "Undefined Answer"
        #else:
        #    print("Undefined Answer")
        #print("Actual Answer : ")
        #print(actual_answer)  
        steps = steps + 1
        if number_of_flips != None and steps == number_of_flips:
            break
        
    return_dict = {
        "question": question.lower(),
        "context" : context.lower(),
        "answer" : answer,
        "flips" : flips,
        "total_flips": len(flips),
        "new_answer" : new_answer,
        "indexes" : flipped_indexes
    }

    return return_dict

def do_hotflip(args):
    model, tokenizer, sep_token = get_model_tokenizer(args)
    inputs = tokenizer(args["question"], args["context"], return_tensors="pt")
    answer, start, end = get_answer(model, tokenizer, inputs)
    if args["include_answer"] == 'true':
        args["include_answer"] = True
    else:
        args["include_answer"] = False
    if args['number_of_flips'] == 0:
        args['number_of_flips'] = None

    hotflip_response = hotflip(model, tokenizer, args["question"], args["context"], answer, start, end, sep_token, 
                include_answer = args["include_answer"], gradient_way = args["gradient_way"], number_of_flips = args['number_of_flips'])
    return hotflip_response


if __name__ == '__main__':

    squad = load_dataset("squad", split = "validation")
    args = {
        "model_name" : "bert-base-uncased",
        "adapter" : "AdapterHub/bert-base-uncased-pf-squad_v2",
        "question" : [squad[0]['question'], squad[1]['question']],
        "context" : [squad[0]['context'], squad[1]['context']],
        #"question" : squad[0]['question'],
        #"context" : squad[0]['context'],
        "gradient_way" : "integreted",
        "include_answer" : "false",
        "number_of_flips" : 0,
    }
    print(do_hotflip(args))


    
    


