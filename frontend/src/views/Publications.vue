<template>
    <div class="d-flex align-items-center">
        <div class="d-flex flex-column flex-md-row w-100 ps-md-3">
            <div class="bg-light flex-fill my-2 me-md-3 pt-3 px-3 pt-md-5 px-md-5 overflow-hidden">
                <div class="mb-3 pb-3">
                    <h1>Scientific Publications about SQuARE</h1>
                    <div class="accordion" id="accordion_square_papers">
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="square_v3_header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                                    data-bs-target="#square_v3" aria-expanded="false" aria-controls="square_v3">
                                    [<b>ACL</b>, 2023] UKP-SQuARE v3: A Platform for Multi-Agent QA Research
                                </button>
                            </h2>
                            <div id="square_v3" class="accordion-collapse collapse" aria-labelledby="square_v3_header"
                                data-bs-parent="#accordion_square_papers">
                                <div class="accordion-body">
                                    <strong>Link: </strong><a href="https://aclanthology.org/2023.acl-demo.55/"
                                        target="_blank">https://aclanthology.org/2023.acl-demo.55/</a> <br />
                                    <strong>Authors: </strong>Haritz Puerto, Tim Baumgärtner, Rachneet Sachdeva, Haishuo
                                    Fang, Hao Zhang, Sewin Tariverdian, Kexin Wang, Iryna Gurevych <br />
                                    <strong>Abstract: </strong> The continuous development of Question Answering (QA)
                                    datasets has drawn the research community's attention toward multi-domain models. A
                                    popular approach is to use multi-dataset models, which are models trained on multiple
                                    datasets to learn their regularities and prevent overfitting to a single dataset.
                                    However, with the proliferation of QA models in online repositories such as GitHub or
                                    Hugging Face, an alternative is becoming viable. Recent works have demonstrated that
                                    combining expert agents can yield large performance gains over multi-dataset models. To
                                    ease research in multi-agent models, we extend UKP-SQuARE, an online platform for QA
                                    research, to support three families of multi-agent systems: i) agent selection, ii)
                                    early-fusion of agents, and iii) late-fusion of agents. We conduct experiments to
                                    evaluate their inference speed and discuss the performance vs. speed trade-off compared
                                    to multi-dataset models. UKP-SQuARE is open-source and publicly available at
                                    https://square.ukp-lab.de/.
                                </div>
                            </div>
                        </div>

                        <div class="accordion-item">
                            <h2 class="accordion-header" id="aacl2022_square_header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                                    data-bs-target="#aacl2022_square" aria-expanded="false" aria-controls="aacl2022_square">
                                    [<b>AACL</b>, 2022] UKP-SQuARE v2: Explainability and Adversarial Attacks for
                                    Trustworthy QA
                                </button>
                            </h2>
                            <div id="aacl2022_square" class="accordion-collapse collapse"
                                aria-labelledby="aacl2022_square_header" data-bs-parent="#accordion_square_papers">
                                <div class="accordion-body">
                                    <strong>Link: </strong><a href="https://aclanthology.org/2022.aacl-demo.4/"
                                        target="_blank">https://aclanthology.org/2022.aacl-demo.4/</a> <br />
                                    <strong>Authors: </strong>Rachneet Sachdeva, Haritz Puerto, Tim Baumgärtner, Sewin
                                    Tariverdian, Hao Zhang, Kexin Wang, Hossain Shaikh Saadi, Leonardo F. R. Ribeiro, Iryna
                                    Gurevych <br />
                                    <strong>Abstract: </strong>Question Answering (QA) systems are increasingly deployed in
                                    applications where they support real-world decisions. However, state-of-the-art models
                                    rely on deep neural networks, which are difficult to interpret by humans. Inherently
                                    interpretable models or post hoc explainability methods can help users to comprehend how
                                    a model arrives at its prediction and, if successful, increase their trust in the
                                    system. Furthermore, researchers can leverage these insights to develop new methods that
                                    are more accurate and less biased. In this paper, we introduce SQuARE v2, the new
                                    version of SQuARE, to provide an explainability infrastructure for comparing models
                                    based on methods such as saliency maps and graph-based explanations. While saliency maps
                                    are useful to inspect the importance of each input token for the model's prediction,
                                    graph-based explanations from external Knowledge Graphs enable the users to verify the
                                    reasoning behind the model prediction. In addition, we provide multiple adversarial
                                    attacks to compare the robustness of QA models. With these explainability methods and
                                    adversarial attacks, we aim to ease the research on trustworthy QA models. SQuARE is
                                    available on https://square.ukp-lab.de/.
                                </div>
                            </div>
                        </div>

                        <div class="accordion-item">
                            <h2 class="accordion-header" id="acl2022_square_header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                                    data-bs-target="#acl2022_square" aria-expanded="false" aria-controls="acl2022_square">
                                    [<b>ACL</b>, 2022] UKP-SQUARE: An Online Platform for Question Answering Research
                                </button>
                            </h2>
                            <div id="acl2022_square" class="accordion-collapse collapse"
                                aria-labelledby="acl2022_square_header" data-bs-parent="#accordion_square_papers">
                                <div class="accordion-body">
                                    <strong>Link: </strong><a href="https://aclanthology.org/2022.acl-demo.2/"
                                        target="_blank">https://aclanthology.org/2022.acl-demo.2/</a> <br />
                                    <strong>Authors: </strong>Tim Baumgärtner, Kexin Wang, Rachneet Sachdeva, Gregor Geigle,
                                    Max Eichler, Clifton Poth, Hannah Sterz, Haritz Puerto, Leonardo F. R. Ribeiro, Jonas
                                    Pfeiffer, Nils Reimers, Gözde Şahin, Iryna Gurevych <br />
                                    <strong>Abstract: </strong>Recent advances in NLP and information retrieval have given
                                    rise to a diverse set of question answering tasks that are of different formats (e.g.,
                                    extractive, abstractive), require different model architectures (e.g., generative,
                                    discriminative), and setups (e.g., with or without retrieval). Despite having a large
                                    number of powerful, specialized QA pipelines (which we refer to as Skills) that consider
                                    a single domain, model or setup, there exists no framework where users can easily
                                    explore and compare such pipelines and can extend them according to their needs. To
                                    address this issue, we present UKP-SQUARE, an extensible online QA platform for
                                    researchers which allows users to query and analyze a large collection of modern Skills
                                    via a user-friendly web interface and integrated behavioural tests. In addition, QA
                                    researchers can develop, manage, and share their custom Skills using our microservices
                                    that support a wide range of models (Transformers, Adapters, ONNX), datastores and
                                    retrieval techniques (e.g., sparse and dense). UKP-SQUARE is available on
                                    thttps://square.ukp-lab.de/.
                                </div>
                            </div>
                        </div>

                    </div>

                    <h1>Scientific Publications funded by SQuARE</h1>

                    <div class="accordion" id="accordion_funded_by_square">
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="arxiv2021_haritz_header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                                    data-bs-target="#arxiv2021_haritz" aria-expanded="false"
                                    aria-controls="arxiv2021_haritz">
                                    [<b>EACL</b>, 2023] MetaQA: Combining Expert Agents for Multi-Skill Question Answering
                                </button>
                            </h2>
                            <div id="arxiv2021_haritz" class="accordion-collapse collapse"
                                aria-labelledby="arxiv2021_haritz_header" data-bs-parent="#accordion_funded_by_square">
                                <div class="accordion-body">
                                    <strong>Link: </strong><a href="https://aclanthology.org/2023.eacl-main.259/"
                                        target="_blank">https://aclanthology.org/2023.eacl-main.259/</a> <br />
                                    <strong>Authors: </strong>Haritz Puerto, Gözde Gül Şahin, Iryna Gurevych<br />
                                    <strong>Abstract: </strong>The recent explosion of question answering (QA) datasets and
                                    models has increased the interest in the generalization of models across multiple
                                    domains and formats by either training on multiple datasets or by combining multiple
                                    models. Despite the promising results of multi-dataset models, some domains or QA
                                    formats may require specific architectures, and thus the adaptability of these models
                                    might be limited. In addition, current approaches for combining models disregard cues
                                    such as question-answer compatibility. In this work, we propose to combine expert agents
                                    with a novel, flexible, and training-efficient architecture that considers questions,
                                    answer predictions, and answer-prediction confidence scores to select the best answer
                                    among a list of answer candidates. Through quantitative and qualitative experiments we
                                    show that our model i) creates a collaboration between agents that outperforms previous
                                    multi-agent and multi-dataset approaches in both in-domain and out-of-domain scenarios,
                                    ii) is highly data-efficient to train, and iii) can be adapted to any QA format. We
                                    release our code and a dataset of answer predictions from expert agents for 16 QA
                                    datasets to foster future developments of multi-agent systems on this https URL.

                                </div>
                            </div>
                        </div>

                        <div class="accordion-item">
                            <h2 class="accordion-header" id="emnlp2022_tim_header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                                    data-bs-target="#emnlp2022_tim" aria-expanded="false" aria-controls="emnlp2022_tim">
                                    [<b>EMNLP</b>, 2022] Incorporating Relevance Feedback for Information-Seeking Retrieval
                                    using Few-Shot Document Re-Ranking
                                </button>
                            </h2>
                            <div id="emnlp2022_tim" class="accordion-collapse collapse"
                                aria-labelledby="emnlp2022_tim_header" data-bs-parent="#accordion_funded_by_square">
                                <div class="accordion-body">
                                    <strong>Link: </strong><a href="https://arxiv.org/abs/2210.10695"
                                        target="_blank">https://arxiv.org/abs/2210.10695</a> <br />
                                    <strong>Authors: </strong>Tim Baumgärtner, Leonardo F. R. Ribeiro, Nils Reimers, Iryna
                                    Gurevych<br />
                                    <strong>Abstract: </strong>Pairing a lexical retriever with a neural re-ranking model
                                    has set state-of-the-art performance on large-scale information retrieval datasets. This
                                    pipeline covers scenarios like question answering or navigational queries, however, for
                                    information-seeking scenarios, users often provide information on whether a document is
                                    relevant to their query in form of clicks or explicit feedback. Therefore, in this work,
                                    we explore how relevance feedback can be directly integrated into neural re-ranking
                                    models by adopting few-shot and parameter-efficient learning techniques. Specifically,
                                    we introduce a kNN approach that re-ranks documents based on their similarity with the
                                    query and the documents the user considers relevant. Further, we explore Cross-Encoder
                                    models that we pre-train using meta-learning and subsequently fine-tune for each query,
                                    training only on the feedback documents. To evaluate our different integration
                                    strategies, we transform four existing information retrieval datasets into the relevance
                                    feedback scenario. Extensive experiments demonstrate that integrating relevance feedback
                                    directly in neural re-ranking models improves their performance, and fusing lexical
                                    ranking with our best performing neural re-ranker outperforms all other methods by 5.2
                                    nDCG@20.
                                </div>
                            </div>
                        </div>


                        <div class="accordion-item">
                            <h2 class="accordion-header" id="naacl2022_kexin_header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                                    data-bs-target="#naacl2022_kexin" aria-expanded="false" aria-controls="naacl2022_kexin">
                                    [<b>NAACL</b>, 2022] GPL: Generative Pseudo Labeling for Unsupervised Domain Adaptation
                                    of Dense Retrieval.
                                </button>
                            </h2>
                            <div id="naacl2022_kexin" class="accordion-collapse collapse"
                                aria-labelledby="naacl2022_kexin_header" data-bs-parent="#accordion_funded_by_square">
                                <div class="accordion-body">
                                    <strong>Link: </strong><a href="https://aclanthology.org/2022.naacl-main.168"
                                        target="_blank">https://aclanthology.org/2022.naacl-main.168</a> <br />
                                    <strong>Authors: </strong>Kexin Wang, Nandan Thakur, Nils Reimers, Iryna Gurevych<br />
                                    <strong>Abstract: </strong>Dense retrieval approaches can overcome the lexical gap and
                                    lead to significantly improved search results. However, they require large amounts of
                                    training data which is not available for most domains. As shown in previous work (Thakur
                                    et al., 2021b), the performance of dense retrievers severely degrades under a domain
                                    shift. This limits the usage of dense retrieval approaches to only a few domains with
                                    large training datasets. In this paper, we propose the novel unsupervised domain
                                    adaptation method Generative Pseudo Labeling (GPL), which combines a query generator
                                    with pseudo labeling from a cross-encoder. On six representative domain-specialized
                                    datasets, we find the proposed GPL can outperform an out-of-the-box state-of-the-art
                                    dense retrieval approach by up to 9.3 points nDCG@10. GPL requires less (unlabeled) data
                                    from the target domain and is more robust in its training than previous methods. We
                                    further investigate the role of six recent pre-training methods in the scenario of
                                    domain adaptation for retrieval tasks, where only three could yield improved results.
                                    The best approach, TSDAE (Wang et al., 2021) can be combined with GPL, yielding another
                                    average improvement of 1.4 points nDCG@10 across the six tasks. The code and the models
                                    are available at https://github.com/UKPLab/gpl.
                                </div>
                            </div>
                        </div>

                        <div class="accordion-item">
                            <h2 class="accordion-header" id="neurips2021_nandan_header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                                    data-bs-target="#neurips2021_nandan" aria-expanded="false"
                                    aria-controls="neurips2021_nandan">
                                    [<b>NeurIPS</b>, 2021] BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of
                                    Information Retrieval Models.
                                </button>
                            </h2>
                            <div id="neurips2021_nandan" class="accordion-collapse collapse"
                                aria-labelledby="neurips2021_nandan_header" data-bs-parent="#accordion_funded_by_square">
                                <div class="accordion-body">
                                    <strong>Link: </strong><a href="https://openreview.net/forum?id=wCu6T5xFjeJ"
                                        target="_blank">https://openreview.net/forum?id=wCu6T5xFjeJ</a> <br />
                                    <strong>Authors: </strong>Nandan Thakur, Nils Reimers, Andreas Rücklé, Abhishek
                                    Srivastava, Iryna Gurevych<br />
                                    <strong>Abstract: </strong>Existing neural information retrieval (IR) models have often
                                    been studied in homogeneous and narrow settings, which has considerably limited insights
                                    into their out-of-distribution (OOD) generalization capabilities. To address this, and
                                    to facilitate researchers to broadly evaluate the effectiveness of their models, we
                                    introduce Benchmarking-IR (BEIR), a robust and heterogeneous evaluation benchmark for
                                    information retrieval. We leverage a careful selection of 18 publicly available datasets
                                    from diverse text retrieval tasks and domains and evaluate 10 state-of-the-art retrieval
                                    systems including lexical, sparse, dense, late-interaction, and re-ranking architectures
                                    on the BEIR benchmark. Our results show BM25 is a robust baseline and re-ranking and
                                    late-interaction based models on average achieve the best zero-shot performances,
                                    however, at high computational costs. In contrast, dense and sparse-retrieval models are
                                    computationally more efficient but often underperform other approaches, highlighting the
                                    considerable room for improvement in their generalization capabilities. We hope this
                                    framework allows us to better evaluate and understand existing retrieval systems and
                                    contributes to accelerating progress towards more robust and generalizable systems in
                                    the future. BEIR is publicly available at https://github.com/UKPLab/beir.
                                </div>
                            </div>
                        </div>

                        <div class="accordion-item">
                            <h2 class="accordion-header" id="NLPConv2021_Leo_header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                                    data-bs-target="#NLPConv2021_Leo" aria-expanded="false" aria-controls="NLPConv2021_Leo">
                                    [<b>NLP for Conversational AI Workshop@EMNLP</b>, 2021] Investigating Pretrained
                                    Language Models for Graph-to-Text Generation.
                                </button>
                            </h2>
                            <div id="NLPConv2021_Leo" class="accordion-collapse collapse"
                                aria-labelledby="NLPConv2021_Leo_header" data-bs-parent="#accordion_funded_by_square">
                                <div class="accordion-body">
                                    <strong>Link: </strong><a href="https://aclanthology.org/2021.nlp4convai-1.20/"
                                        target="_blank">https://aclanthology.org/2021.nlp4convai-1.20/</a> <br />
                                    <strong>Authors: </strong>Leonardo F. R. Ribeiro, Martin Schmitt, Hinrich Schütze, Iryna
                                    Gurevych<br />
                                    <strong>Abstract: </strong>Graph-to-text generation aims to generate fluent texts from
                                    graph-based data. In this paper, we investigate two recent pretrained language models
                                    (PLMs) and analyze the impact of different task-adaptive pretraining strategies for PLMs
                                    in graph-to-text generation. We present a study across three graph domains: meaning
                                    representations, Wikipedia knowledge graphs (KGs) and scientific KGs. We show that
                                    approaches based on PLMs BART and T5 achieve new state-of-the-art results and that
                                    task-adaptive pretraining strategies improve their performance even further. We report
                                    new state-of-the-art BLEU scores of 49.72 on AMR-LDC2017T10, 59.70 on WebNLG, and 25.66
                                    on AGENDA datasets - a relative improvement of 31.8%, 4.5%, and 42.4%, respectively,
                                    with our models generating significantly more fluent texts than human references. In an
                                    extensive analysis, we identify possible reasons for the PLMs’ success on graph-to-text
                                    tasks. Our findings suggest that the PLMs benefit from similar facts seen during
                                    pretraining or fine-tuning, such that they perform well even when the input graph is
                                    reduced to a simple bag of node and edge labels.
                                </div>
                            </div>
                        </div>

                        <div class="accordion-item">
                            <h2 class="accordion-header" id="emnlp2021_leo_header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                                    data-bs-target="#emnlp2021_leo" aria-expanded="false" aria-controls="emnlp2021_leo">
                                    [<b>EMNLP</b>, 2021] Smelting Gold and Silver for Improved Multilingual AMR-to-Text
                                    Generation.
                                </button>
                            </h2>
                            <div id="emnlp2021_leo" class="accordion-collapse collapse"
                                aria-labelledby="emnlp2021_leo_header" data-bs-parent="#accordion_funded_by_square">
                                <div class="accordion-body">
                                    <strong>Link: </strong><a href="https://aclanthology.org/2021.emnlp-main.57"
                                        target="_blank">https://aclanthology.org/2021.emnlp-main.57/</a> <br />
                                    <strong>Authors: </strong>Leonardo F. R. Ribeiro, Jonas Pfeiffer, Yue Zhang, Iryna
                                    Gurevych<br />
                                    <strong>Abstract: </strong>Recent work on multilingual AMR-to-text generation has
                                    exclusively focused on data augmentation strategies that utilize silver AMR. However,
                                    this assumes a high quality of generated AMRs, potentially limiting the transferability
                                    to the target task. In this paper, we investigate different techniques for automatically
                                    generating AMR annotations, where we aim to study which source of information yields
                                    better multilingual results. Our models trained on gold AMR with silver (machine
                                    translated) sentences outperform approaches which leverage generated silver AMR. We find
                                    that combining both complementary sources of information further improves multilingual
                                    AMR-to-text generation. Our models surpass the previous state of the art for German,
                                    Italian, Spanish, and Chinese by a large margin.

                                </div>
                            </div>
                        </div>

                        <div class="accordion-item">
                            <h2 class="accordion-header" id="emnlp2021_kexin_header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                                    data-bs-target="#emnlp2021_kexin" aria-expanded="false" aria-controls="emnlp2021_kexin">
                                    [<b>Findings of EMNLP</b>, 2021] TSDAE: Using Transformer-based Sequential Denoising
                                    Auto-Encoder for Unsupervised Sentence Embedding Learning.
                                </button>
                            </h2>
                            <div id="emnlp2021_kexin" class="accordion-collapse collapse"
                                aria-labelledby="emnlp2021_kexin_header" data-bs-parent="#accordion_funded_by_square">
                                <div class="accordion-body">
                                    <strong>Link: </strong><a href="https://aclanthology.org/2021.findings-emnlp.59/"
                                        target="_blank">https://aclanthology.org/2021.findings-emnlp.59/</a> <br />
                                    <strong>Authors: </strong>Kexin Wang, Nils Reimers, Iryna Gurevych<br />
                                    <strong>Abstract: </strong>Learning sentence embeddings often requires a large amount of
                                    labeled data. However, for most tasks and domains, labeled data is seldom available and
                                    creating it is expensive. In this work, we present a new state-of-the-art unsupervised
                                    method based on pre-trained Transformers and Sequential Denoising Auto-Encoder (TSDAE)
                                    which outperforms previous approaches by up to 6.4 points. It can achieve up to 93.1% of
                                    the performance of in-domain supervised approaches. Further, we show that TSDAE is a
                                    strong domain adaptation and pre-training method for sentence embeddings, significantly
                                    outperforming other approaches like Masked Language Model. A crucial shortcoming of
                                    previous studies is the narrow evaluation: Most work mainly evaluates on the single task
                                    of Semantic Textual Similarity (STS), which does not require any domain knowledge. It is
                                    unclear if these proposed methods generalize to other domains and tasks. We fill this
                                    gap and evaluate TSDAE and other recent approaches on four different datasets from
                                    heterogeneous domains.

                                </div>
                            </div>
                        </div>

                        <div class="accordion-item">
                            <h2 class="accordion-header" id="arxiv2021_gregor_header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                                    data-bs-target="#arxiv2021_gregor" aria-expanded="false"
                                    aria-controls="arxiv2021_gregor">
                                    [<b>ArXiv</b>, 2021] TWEAC: Transformer with Extendable QA Agent Classifiers
                                </button>
                            </h2>
                            <div id="arxiv2021_gregor" class="accordion-collapse collapse" aria-labelledby="headingThree"
                                data-bs-parent="#accordion_funded_by_square">
                                <div class="accordion-body">
                                    <strong>Link: </strong><a href="https://arxiv.org/abs/2104.07081"
                                        target="_blank">https://arxiv.org/abs/2104.07081</a> <br />
                                    <strong>Authors: </strong>Gregor Geigle, Nils Reimers, Andreas Rücklé, Iryna
                                    Gurevych<br />
                                    <strong>Abstract: </strong>Question answering systems should help users to access
                                    knowledge on a broad range of topics and to answer a wide array of different questions.
                                    Most systems fall short of this expectation as they are only specialized in one
                                    particular setting, e.g., answering factual questions with Wikipedia data. To overcome
                                    this limitation, we propose composing multiple QA agents within a meta-QA system. We
                                    argue that there exist a wide range of specialized QA agents in literature. Thus, we
                                    address the central research question of how to effectively and efficiently identify
                                    suitable QA agents for any given question. We study both supervised and unsupervised
                                    approaches to address this challenge, showing that TWEAC -- Transformer with Extendable
                                    Agent Classifiers -- achieves the best performance overall with 94% accuracy. We provide
                                    extensive insights on the scalability of TWEAC, demonstrating that it scales robustly to
                                    over 100 QA agents with each providing just 1000 examples of questions they can answer.
                                    Our code and data is available: this https URL
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>


<script>
import Vue from 'vue'

export default Vue.component('list-publications', {})
</script>