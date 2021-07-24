"""
Just a dummy module.
"""
import transformers

tokenizer = transformers.DPRQuestionEncoderTokenizer.from_pretrained('facebook/dpr-question_encoder-single-nq-base')
model = transformers.DPRQuestionEncoder.from_pretrained('facebook/dpr-question_encoder-single-nq-base', return_dict=True)
pipeline = transformers.Pipeline(model=model, tokenizer=tokenizer)


def encode_document(encoder: str, document: str):
    pass


def encode_query(encoder: str, query: str):
    return pipeline([query])[0].tolist() + [0]
