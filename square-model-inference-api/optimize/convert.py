import time

import nebullvm
from nebullvm.api.functions import optimize_model

import torch

# from transformers import GPT2Tokenizer, GPT2Model
#
#
# tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
# model = GPT2Model.from_pretrained('gpt2')
# text = "Short text you wish to process"
# long_text = " ".join([text]*100)
#
# # Move the model to gpu if available
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model.to(device)
# model.eval()
#
# encoded_input = tokenizer(text, return_tensors='pt')
# encoded_input = {key: encoded_input[key].to(device) for key in encoded_input}

# times = []
# for _ in range(100):
#     st = time.time()
#     with torch.no_grad():
#         output = model(**encoded_input)
#     times.append(time.time()-st)
# vanilla_short_token_time = sum(times)/len(times)*1000
# print(f"Average response time for GPT2: ({encoded_input['input_ids'].shape[1]} tokens): {vanilla_short_token_time} ms")


# optimize


#
# dynamic_info = {
#     "inputs": [
#         {0: 'batch', 1: 'num_tokens'},
#         {0: 'batch', 1: 'num_tokens'}
#     ],
#     "outputs": [
#         {0: 'batch', 1: 'num_tokens'},
#         {0: 'batch'}
#     ]
# }
#
# optimized_model = optimize_model(
#     model=model,
#     input_data=[encoded_input],
#     optimization_time="constrained",
#     dynamic_info=dynamic_info
# )
#
# times = []
# for _ in range(100):
#     st = time.time()
#     with torch.no_grad():
#         final_out = optimized_model(**encoded_input)
#     times.append(time.time()-st)
# optimized_short_token_time = sum(times)/len(times)*1000
# print(f"Average response time for GPT2 ({encoded_input['input_ids'].shape[1]} tokens): {optimized_short_token_time} ms")


# BERT optimization
from transformers import BertTokenizer, BertModel

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

text = "Short text you wish to process"
inputs = tokenizer(text, return_tensors="pt")
inputs = {key: inputs[key].to(device) for key in inputs}

# times = []
# for _ in range(100):
#     st = time.time()
#     with torch.no_grad():
#         outputs = model(**inputs)
#     times.append(time.time()-st)
# vanilla_bert_short = sum(times)/len(times)*1000
# print(f"Average response time for BERT: ({inputs['input_ids'].shape[1]} tokens): {vanilla_bert_short}")

optimized_model = optimize_model(
    model=model,
    input_data=[inputs],
    metric_drop_ths=0,
    optimization_time="constrained",
)


times = []
for _ in range(100):
    st = time.time()
    with torch.no_grad():
        outputs = optimized_model(**inputs)
    times.append(time.time()-st)
optimized_bert_short = sum(times)/len(times)*1000
print(f"Average response time for BERT: ({inputs['input_ids'].shape[1]} tokens): {optimized_bert_short} ms")
print(outputs)
