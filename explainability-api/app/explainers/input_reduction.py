import torch
#from datasets import load_dataset
import numpy as np
import random
import json
try:
    from .utils import * 
except Exception as ex:
    from utils import * 

def input_reduction(model, tokenizer, question, context, answer, answer_start, answer_end, sep_token,
        gradient_way = 'simple', number_of_reductions = None):
    
    """
        return:
            perform input reduction and returns a dictionary
    """
    
    inputs = tokenizer(question, context, return_tensors="pt")
    tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])

    saliencies, start_index, end_index = interpret(model, gradient_way, inputs, answer_start, answer_end)
    processed_tokens, processed_saliencies = process(tokens, saliencies, tokenizer)
    sep_index = processed_tokens.index(sep_token)
    processed_saliencies[0:sep_index+1] = [100] * len(processed_saliencies[0:sep_index+1])
    context_tokens = processed_tokens[sep_index+1 : (len(processed_tokens) -1)]
    new_context = " ".join(context_tokens)
    
    context_tokens = processed_tokens[sep_index+1 : (len(processed_tokens) -1)]


    tokenized_answer = process_answer(tokens[answer_start:answer_end+1], tokenizer)
    if len(tokenized_answer) > 1:
        tokenized_answer = " ".join(tokenized_answer)
    elif len(tokenized_answer) == 1:
        tokenized_answer = tokenized_answer[0]
    else:
        tokenized_answer = ""

    
    deleted_words = []
    steps = 0
    p_deleted = []
    p_tokens = processed_tokens
    while tokenized_answer == answer:
        p_deleted = deleted_words
        p_tokens = processed_tokens

        min_index = get_min(processed_saliencies)
        deleted_word = processed_tokens[min_index]
        processed_tokens = processed_tokens[0:min_index] + processed_tokens[min_index+1:len(processed_tokens)-1]
    
        new_input = ' '.join(processed_tokens[1:len(processed_tokens)])
        inputs = tokenizer(new_input, return_tensors="pt")
        tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])

        saliencies, start_index, end_index = interpret(model, gradient_way, inputs, start_index, answer_end)
        processed_tokens, processed_saliencies = process(tokens, saliencies, tokenizer)
        sep_index = processed_tokens.index(sep_token)
        processed_saliencies[0:sep_index+1] = [100] * len(processed_saliencies[0:sep_index+1])
        
        new_answer = tokenizer.decode(tokenizer.convert_tokens_to_ids(tokens[sep_index:end_index+1]), skip_special_tokens = True)
        tokenized_answer = process_answer(tokens[start_index:end_index+1], tokenizer)
        if len(tokenized_answer) > 1:
            tokenized_answer = " ".join(tokenized_answer)
        elif len(tokenized_answer) == 1:
            tokenized_answer = tokenized_answer[0]
        else:
            tokenized_answer = ""
        if len(new_answer.strip()) <= 0:
            new_answer = "Undefined Answer"   
        elif new_answer == '[CLS]':
            new_answer = "Undefined Answer"  
        else:
            deleted_words.append(deleted_word)  
        steps = steps + 1  
        if number_of_reductions != None and steps == number_of_reductions:
            break     
    remaining = " ".join(p_tokens[sep_index+1:len(p_tokens)-1])
    return_dict = {
        "question": question.lower(),
        "context" : new_context,
        "answer" : answer,
        "deleted_tokens" : p_deleted,
        "total_deleted_words": len(deleted_words),
        "remaining_context" : remaining
    }
    return return_dict

def do_input_reduction(args):
    """
        return:
            perform input reduction and returns a dictionary
    """

    model, tokenizer, sep_token = get_model_tokenizer(args)
    if args["number_of_reductions"] == 0:
        args["number_of_reductions"] = None
    if type(args["question"]) != list:
        inputs = tokenizer(args["question"], args["context"], return_tensors="pt")
        answer, start, end = get_answer(model, tokenizer, inputs)
        response = input_reduction(model, tokenizer, args["question"], args["context"], answer, start, end, sep_token,
                gradient_way = args["gradient_way"], number_of_reductions = args["number_of_reductions"])
    else:
        response = []
        for i in range(len(args["question"])):
            inputs = tokenizer(args["question"][i], args["context"][i], return_tensors="pt")
            answer, start, end = get_answer(model, tokenizer, inputs)
            response_ = input_reduction(model, tokenizer, args["question"][i], args["context"][i], answer, start, end, sep_token,
                gradient_way = args["gradient_way"], number_of_reductions = args["number_of_reductions"])
            response.append(response_)
    #response = json.dumps(response, indent = 4)
    return response


if __name__ == '__main__':

    squad = load_dataset("squad", split = "validation")
    args = {
        "model_name" : "bert-base-uncased",
        "adapter" : "AdapterHub/bert-base-uncased-pf-squad_v2",
        "question" :  squad[1]['question'],
        "context" : squad[1]['context'],
        "gradient_way" : "simple",
        "number_of_reductions" : 300
    }
    print(do_input_reduction(args))



    
    


