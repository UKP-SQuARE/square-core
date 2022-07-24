import torch
from datasets import load_dataset
import numpy as np
import random
import json
try:
    from .utils import * 
except Exception as ex:
    from utils import * 

def input_reduction(model, tokenizer, question, context, model_answer, sep_token,
        gradient_way = 'simple', number_of_reductions = None):

    inputs = tokenizer(question, context, return_tensors="pt")
    tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
    chosen_tokens = [0] * len(tokens)
    sep_index = tokens.index(sep_token)
    answer_input = tokenizer(model_answer, return_tensors="pt")
    answer_tokens = tokenizer.convert_ids_to_tokens(answer_input.input_ids[0])

    start = tokens.index(answer_tokens[1])
    end = tokens.index(answer_tokens[len(answer_tokens)-2])
    answer = tokens[start:end+1]
    actual_answer = answer_tokens[1:len(answer_tokens)-1]

    saliencies, start_index, end_index = interpret(model, gradient_way, inputs, start, end)
    saliencies[0:sep_index+1] = [100] * len(saliencies[0:sep_index+1])
            
    
    deleted_words = []
    steps = 0
    while tokens[start_index:end_index+1] == answer:
        min_index = get_min(saliencies)
        while "##" in tokens[min_index] or "##" in tokens[min_index+1]:
            saliencies[min_index] = 100
            min_index = get_min(saliencies)
        deleted_word = tokens[min_index]
        deleted_words.append(deleted_word)

        del tokens[min_index]
        temp_list = inputs['input_ids'][0].tolist()
        del temp_list[min_index]
        inputs['input_ids'] = torch.tensor([temp_list])

        temp_list = inputs['token_type_ids'][0].tolist()
        del temp_list[min_index]
        inputs['token_type_ids'] = torch.tensor([temp_list])

        temp_list = inputs['attention_mask'][0].tolist()
        del temp_list[min_index]
        inputs['attention_mask'] = torch.tensor([temp_list])

        tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
        start = tokens.index(answer_tokens[1])
        end = tokens.index(answer_tokens[len(answer_tokens)-2])

        saliencies, start_index, end_index = interpret(model, gradient_way, inputs, start, end)
        saliencies[0:sep_index+1] = [100] * len(saliencies[0:sep_index+1])
        steps = steps + 1   
        if number_of_reductions != None and steps == number_of_reductions:
            break
        new_answer = tokenizer.decode(tokenizer.convert_tokens_to_ids(tokens[start_index:end_index+1]), skip_special_tokens = True)
        actual_answer = tokenizer.decode(tokenizer.convert_tokens_to_ids(answer))
        #print("Step : "+str(steps))
        #print("New answer : ")
        #if len(new_answer.strip()) > 0:
        #    print(new_answer)
        #else:
        #    print("Undefined Answer")
        #print("Actual Answer : ")
        #print(actual_answer)    
        #print("Deleted Word :")
        #print(deleted_word)              
    #print("Total Deleted Words : "+ str(len(deleted_words)))
    #print("Deleted Words : ")
    #print(deleted_words)
    remaining = tokenizer.decode(tokenizer.convert_tokens_to_ids(tokens[sep_index:]), skip_special_tokens = True)
    #print("Remaining Words of Context : "+remaining)
    return_dict = {
        "question": question.lower(),
        "context" : context.lower(),
        "answer" : model_answer,
        "deleted_tokens" : deleted_words,
        "total_deleted_words": len(deleted_words),
        "remaining_context" : remaining
    }
    return return_dict

def do_input_reduction(args):
    model, tokenizer, sep_token = get_model_tokenizer(args)
    if args["number_of_reductions"] == 0:
        args["number_of_reductions"] = None
    if type(args["question"]) != list:
        inputs = tokenizer(args["question"], args["context"], return_tensors="pt")
        answer, start, end = get_answer(model, tokenizer, inputs)
        response = input_reduction(model, tokenizer, args["question"], args["context"], answer, sep_token,
                gradient_way = args["gradient_way"], number_of_reductions = args["number_of_reductions"])
    else:
        response = []
        for i in range(len(args["question"])):
            inputs = tokenizer(args["question"][i], args["context"][i], return_tensors="pt")
            answer, start, end = get_answer(model, tokenizer, inputs)
            response_ = input_reduction(model, tokenizer, args["question"][i], args["context"][i], answer, sep_token,
                gradient_way = args["gradient_way"], number_of_reductions = args["number_of_reductions"])
            response.append(response_)
    #response = json.dumps(response, indent = 4)
    return response


if __name__ == '__main__':

    squad = load_dataset("squad", split = "validation")
    args = {
        "model_name" : "bert-base-uncased",
        "adapter" : "AdapterHub/bert-base-uncased-pf-squad_v2",
        "question" : squad[0]['question'],
        "context" : squad[0]['context'],
        #"question" : squad[0]['question'],
        #"context" : squad[0]['context'],
        "gradient_way" : "simple",
        "number_of_reductions" : 20
    }
    print(do_input_reduction(args))



    
    


