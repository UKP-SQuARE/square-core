.. SQuARE Docs documentation master file, created by
   sphinx-quickstart on Mon Dec 27 13:03:18 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==================================================
SQuARE - Software for Question Answering Research
==================================================

SQuARE is an **open-source** QA platform that enables researchers and developers to:

- Use *QA Skills* in a web browser without writing any code.
- Study the strengths and weaknesses of existing *QA Skills* by comparing them in parallel with a user-friendly interface.
- Analyze the general behavior of QA Skills through `behavioral testing of NLP models <https://github.com/marcotcr/checklist>`_.

.. note::
   To try out SQuARE directly, please visit the `SQuARE Website <https://square.ukp-lab.de>`_.


Why SQuARE?
------------

Recent advances in NLP and information retrieval have given rise to a diverse set of question answering tasks that are of different formats (e.g., extractive, multiple-choice), require different model architectures (e.g., generative, discriminative), and setups (e.g., with or without retrieval). Despite having a large number of powerful, specialized QA pipelines (a.k.a., Skills) that consider a single domain, model, or setup, there is no framework where users can easily explore and compare such pipelines.

To address this issue, we present SQuARE, an online QA platform for researchers that allows to query and analyze a large collection of modern Skills via a user-friendly web interface and integrated behavioral tests.

.. note::
   Find out more about the project on `UKPs Website <https://www.informatik.tu-darmstadt.de/ukp/research_ukp/ukp_research_projects/ukp_project_square/ukp_project_square_details.en.jsp>`_.

Architecture
-------------

.. figure:: images/square-arch.png
   :width: 800
   :align: center
   :alt: SQuARE Architecture

SQuARE is composed of 5 modules:

- Datastore: contains the index of large collections of documents (e.g. Wikipedia, PubMed). These indexes can be for traditional systems such as BM25 or new dense retrieval systems such as Facebook’s DPR.
- Model: manages the three type of models used in SQuARE:
    - Embedding models for indexing documents.
    - Fine-tuned HuggingFace (HF) Transformer models for QA.
    - The backbone Transformer models for Adapters (e.g., bert-base-uncased)
- Skill: module defines a QA pipeline. There are two base pipelines depending on the input:
    - Machine Reading Comprehension (i.e., the input is a question and a document). In this case, we can define how to use a fine-tuned HF Transformer for QA (e.g. `distilBERT for SQuAD <https://huggingface.co/distilbert-base-uncased-distilled-squad>`_). or set the Adapter weights for a Transformer model (e.g. `SQuAD Adapter for RoBERTa <https://adapterhub.ml/adapters/AdapterHub/roberta-base-pf-squad/>`_).
    - Open-retrieval (a.k.a. open-domain; i.e., the input is only a question). In this case, we can define the model to retrieve documents and the consecutive steps as in the previous case.
- User Interface: allows the user to interact with the Skills.
- Explainability: uses `CheckList <https://github.com/marcotcr/checklist>`_ to conduct behavioral tests on the Skills. This allows to easily see biases of the Skills.

.. toctree::
    :caption: Overview
    :maxdepth: 1
    :hidden:

    pages/overview/get_started.md
    pages/overview/use_cases.md
    pages/overview/tutorials.md
    pages/overview/roadmap.md
    pages/overview/faq.md

.. toctree::
    :caption: Components
    :maxdepth: 1
    :hidden:

    pages/components/datastores.md
    pages/components/models.md
    pages/components/skills.md
    pages/components/explainability.md

.. toctree::
    :caption: API
    :maxdepth: 1
    :hidden:

    pages/api/datastore_api/datastores.rst
    pages/api/model_api/models.rst
    pages/api/skill_api/skills.rst
