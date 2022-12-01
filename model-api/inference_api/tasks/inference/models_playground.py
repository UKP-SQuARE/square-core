from transformers import AutoModelForSequenceClassification, AutoTokenizer


model = AutoModelForSequenceClassification.from_pretrained("UKP-SQuARE/tweac_16")
tokenizer = AutoTokenizer.from_pretrained("UKP-SQuARE/tweac_16")
print(tokenizer)
encodings = tokenizer(['do iran and afghanistan speak the same language?'], return_tensors='pt')
print(encodings)
preds = model(**encodings)
print(preds)
