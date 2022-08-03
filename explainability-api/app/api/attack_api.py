from fastapi import APIRouter, HTTPException
from transformers import BertTokenizer
from app.models.heartbeat import HeartbeatResult
from app.models.hotflip import HotFlip
from app.models.input_reduction import InputReduction
from app.models.topk_tokens import TopkTokens
from app.models.tokens_span import TokensSpan
from app.explainers.hotflip import do_hotflip
from app.explainers.input_reduction import do_input_reduction
from app.explainers.topk_span import do_topk_tokens, do_tokens_span


router = APIRouter()

@router.post("/hotflip", name="hotflip")
async def get_hotflip(hotflip_input: HotFlip):
    """
        Input request format:
        a dictionary of following attributes
        {
            "model_name" : name of the model,
            "adapter" : name of the adapter,
            "question" : input question,
            "context" : input context,
            "gradient_way" : gradient calculation format simple/integreted/smooth,
            "include_answer" : true or flase in string format,
            "number_of_flips" : number of flips to do 0 indicates do as much as flips necessary
        }   

    """
    args = {
        "model_name" : str(hotflip_input.model_name),
        "adapter" : str(hotflip_input.adapter),
        "question" : str(hotflip_input.question),
        "context" : str(hotflip_input.context),
        "gradient_way" : str(hotflip_input.gradient_way),
        "include_answer" : str(hotflip_input.include_answer),
        "number_of_flips" : int(hotflip_input.number_of_flips)
    }

    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    tokenized_context = tokenizer(args["context"], return_tensors = "pt")
    context_tokens = tokenizer.convert_ids_to_tokens(tokenized_context.input_ids[0])
    length = len(context_tokens) - 2
    if args['model_name'] != "bert-base-uncased":
        message = "Until now only bert-base-uncased is supported"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['question'].strip() == "":
        message = "Question can not be a empty string"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['context'].strip() == "":
        message = "Context can not be a empty string"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['include_answer'].strip() != "true" and args['include_answer'].strip() != "false":
        message = "Include answer must be 'true' or 'false'"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['number_of_flips'] > length:
        message = "Number of flips must be smaller then the length of tokenized context"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['number_of_flips'] > 20 or args['number_of_flips'] < 0:
        message = "value of number of flips must be between 0 and 20"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    
    try:
        response = do_hotflip(args)
    except Exception as ex:
        message = ex
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    return  response

@router.post("/input_reduction", name="input reduction")
async def get_reduction(input_reduction_input: InputReduction):
    """
        Input request format:
        a dictionary of following attributes
        {
            "model_name" : name of the model,
            "adapter" : name of the adapter,
            "question" : input question,
            "context" : input context,
            "gradient_way" : gradient calculation format simple/integreted/smooth,
            "number_of_reductions" : number of reductions to do 0 indicates do as much as reduction necessary
        }   

    """
    args = {
        "model_name" : str(input_reduction_input.model_name),
        "adapter" : str(input_reduction_input.adapter),
        "question" : str(input_reduction_input.question),
        "context" : str(input_reduction_input.context),
        "gradient_way" : str(input_reduction_input.gradient_way),
        "number_of_reductions" : int(input_reduction_input.number_of_reductions)
    }

    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    tokenized_context = tokenizer(args["context"], return_tensors = "pt")
    context_tokens = tokenizer.convert_ids_to_tokens(tokenized_context.input_ids[0])
    length = len(context_tokens) - 2
    if args['model_name'] != "bert-base-uncased":
        message = "Until now only bert-base-uncased is supported"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['question'].strip() == "":
        message = "Question can not be a empty string"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['context'].strip() == "":
        message = "Context can not be a empty string"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['number_of_reductions'] > length:
        message = "Number of reductions must be smaller then the length of tokenized context"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['number_of_reductions'] > 20 or args['number_of_reductions'] < 0:
        message = "value of number of reductions must be between 0 and 20"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    try:
        response = do_input_reduction(args)
    except Exception as ex:
        message = ex
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    return  response

@router.post("/topk_tokens", name="topk tokens")
async def get_topk_tokens(topk_tokens_input: TopkTokens):
    """
        Input request format:
        a dictionary of following attributes
        {
            "model_name" : name of the model,
            "adapter" : name of the adapter,
            "question" : input question,
            "context" : input context,
            "gradient_way" : gradient calculation format simple/integreted/smooth,
            "topk" : number of tokens to be selected (between 5 and 20)
        }   

    """
    args = {
        "model_name" : str(topk_tokens_input.model_name),
        "adapter" : str(topk_tokens_input.adapter),
        "question" : str(topk_tokens_input.question),
        "context" : str(topk_tokens_input.context),
        "gradient_way" : str(topk_tokens_input.gradient_way),
        "topk" : int(topk_tokens_input.topk)
    }

    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    tokenized_context = tokenizer(args["context"], return_tensors = "pt")
    context_tokens = tokenizer.convert_ids_to_tokens(tokenized_context.input_ids[0])
    length = len(context_tokens) - 2
    if args['model_name'] != "bert-base-uncased":
        message = "Until now only bert-base-uncased is supported"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['question'].strip() == "":
        message = "Question can not be a empty string"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['context'].strip() == "":
        message = "Context can not be a empty string"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['topk'] > length:
        message = "topk must be smaller then the length of tokenized context"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['topk'] > 20 or args['topk'] < 5:
        message = "value of topk must be between 5 and 20"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}

    try:
        response = do_topk_tokens(args)
    except Exception as ex:
        message = ex
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    
    return  response

@router.post("/tokens_span", name="tokens span")
async def get_tokens_span(tokens_span_input: TokensSpan):
    """
        Input request format:
        a dictionary of following attributes
        {
            "model_name" : name of the model,
            "adapter" : name of the adapter,
            "question" : input question,
            "context" : input context,
            "gradient_way" : gradient calculation format simple/integreted/smooth,
            "window" : number of tokens in the span (between 5 and 20)
        }   

    """
    
    args = {
        "model_name" : str(tokens_span_input.model_name),
        "adapter" : str(tokens_span_input.adapter),
        "question" : str(tokens_span_input.question),
        "context" : str(tokens_span_input.context),
        "gradient_way" : str(tokens_span_input.gradient_way),
        "window" : int(tokens_span_input.window)
    }
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    tokenized_context = tokenizer(args["context"], return_tensors = "pt")
    context_tokens = tokenizer.convert_ids_to_tokens(tokenized_context.input_ids[0])
    length = len(context_tokens) - 2
    if args['model_name'] != "bert-base-uncased":
        message = "Until now only bert-base-uncased is supported"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['question'].strip() == "":
        message = "Question can not be a empty string"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['context'].strip() == "":
        message = "Context can not be a empty string"
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    if args['window'] >= length:
        message = "window must be smaller then the length of tokenized context"
        raise HTTPException(status_code=404, detail= message)
        return {"message" : message}
    if args['window'] > 20 or args['window'] < 5:
        message = "value of window must be between 5 and 20"
        raise HTTPException(status_code=404, detail= message)
        return {"message" : message}
    try:
        response = do_tokens_span(args)
    except Exception as ex:
        message = ex
        raise HTTPException(status_code=404, detail=message)
        return {"message" : message}
    
    return  response

