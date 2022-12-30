---
sidebar_position: 5
---


# Architecture

![square-arch](../../static/img/square-arch.png)

SQuARE is composed of 4 modules:

- **Datastores**: contains knowledge bases (e.g. ConceptNet) and indexes for large collections of documents (e.g. Wikipedia, PubMed). These indexes can be from 
  traditional systems such as BM25 or new dense retrieval systems such as Facebook’s DPR.
- **Models**: manages the three type of models used in SQuARE:
    - Embedding models for indexing documents.
    - Fine-tuned HuggingFace (HF) Transformer models for QA.
    - The backbone Transformer models for Adapters (e.g., bert-base-uncased)
- **Skills**: module defines a QA pipeline. There are two base pipelines depending on the input:
    - Machine Reading Comprehension (i.e., the input is a question and a document). In this case, 
      we can define how to use a fine-tuned HF Transformer for QA (e.g. [distilBERT for SQuAD](https://huggingface.co/distilbert-base-uncased-distilled-squad)). or set the Adapter weights for a Transformer model (e.g. [SQuAD Adapter for RoBERTa](https://adapterhub.ml/adapters/AdapterHub/roberta-base-pf-squad/)).
    - Open-retrieval (a.k.a. open-domain; i.e., the input is only a question). In this case, we can define the model to retrieve documents and the consecutive steps as in the previous case.
- **User Interface**: allows the user to interact with the Skills.
