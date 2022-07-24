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

    saliencies, start_index, end_index = interpret(model, gradient_way, inputs, answer_start, answer_end)
    processed_tokens, processed_saliencies = process(tokens, saliencies, tokenizer)
    sep_index = processed_tokens.index(sep_token)
    processed_saliencies[0:sep_index+1] = [0] * len(processed_saliencies[0:sep_index+1])
    context_tokens = processed_tokens[sep_index+1 : (len(processed_tokens) -1)]
    new_context = " ".join(context_tokens)
    chosen_tokens = [0] * len(processed_tokens)
    answer_tokens = answer.split()
    length = len(answer_tokens)
    s, e = find_answer_index(processed_tokens, answer_tokens, length)
    context_tokens = processed_tokens[sep_index+1 : (len(processed_tokens) -1)]

    if include_answer == False:
        chosen_tokens[s:e+1] = [2] * len(chosen_tokens[s:e+1])
    answer_tokens = processed_tokens[s:e+1]
    flips = []
    flipped_indexes = []
    steps = 0

    tokenized_answer = process_answer(tokens[answer_start:answer_end+1], tokenizer)
    if len(tokenized_answer) > 1:
        tokenized_answer = " ".join(tokenized_answer)
    elif len(tokenized_answer) == 1:
        tokenized_answer = tokenized_answer[0]
    else:
        tokenized_answer = ""
    
    while  tokenized_answer == answer:
        proccessed_saliencies, chosen_tokens, max_index = get_max(processed_saliencies, chosen_tokens)
        random_token_id, random_token, already_generated = get_random_token(processed_tokens, already_generated, tokenizer)
        actual_word = processed_tokens[max_index]
        flips.append((actual_word, random_token))
        val = max_index-sep_index-1
        flipped_indexes.append(int(val))
        processed_tokens[max_index] = random_token
        new_input = ' '.join(processed_tokens[1:len(processed_tokens)])
        inputs = tokenizer(new_input, return_tensors="pt")
        saliencies, start_index, end_index = interpret(model, gradient_way, inputs, answer_start, answer_end)
        processed_tokens, processed_saliencies = process(tokens, saliencies, tokenizer)
        tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
        processed_saliencies[0:sep_index+1] = [0] * len(processed_saliencies[0:sep_index+1])
        new_answer = tokenizer.decode(tokenizer.convert_tokens_to_ids(tokens[start_index:end_index+1]), skip_special_tokens = True)
        tokenized_answer = process_answer(tokens[start_index:end_index+1], tokenizer)
        if len(tokenized_answer) > 1:
            tokenized_answer = " ".join(tokenized_answer)
        elif len(tokenized_answer) == 1:
            tokenized_answer = tokenized_answer[0]
        else:
            tokenized_answer = ""
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
        "context" : new_context,
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
    print(answer)
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
        "question" : "where is munich",
        "context" : "Munich is beautiful city in Germany and Europe as well it is located in Bavaria or Bayern",
        "gradient_way" : "simple",
        "include_answer" : "false",
        "number_of_flips" : 4,
    }
    
    try:
        return_c = do_hotflip(args)
        print(return_c)

        for i in range(len(return_c["indexes"])):
            print(return_c["context"].split()[return_c["indexes"][i]])
    except Exception as ex:
        print("Anwer is empty. Give something correct")
    


    


    
    


