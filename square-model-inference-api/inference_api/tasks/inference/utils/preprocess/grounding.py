import multiprocessing

import nltk
# import multiprocessing.pool
# from multiprocessing import Pool
from billiard.pool import Pool
from spacy.matcher import Matcher
from tqdm import tqdm

__all__ = ["ground"]

# the lemma of it/them/mine/.. is -PRON-

blacklist = {
    "-PRON-",
    "actually",
    "likely",
    "possibly",
    "want",
    "make",
    "my",
    "someone",
    "sometimes_people",
    "sometimes",
    "would",
    "want_to",
    "one",
    "something",
    "sometimes",
    "everybody",
    "somebody",
    "could",
    "could_be",
}


nltk.download("stopwords", quiet=True)
nltk_stopwords = nltk.corpus.stopwords.words("english")

CPNET_VOCAB = None
PATTERN_PATH = None
nlp = None
matcher = None


class NoDaemonProcess(multiprocessing.Process):
    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, value):
        pass


class NoDaemonContext(type(multiprocessing.get_context())):
    Process = NoDaemonProcess


# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class NestablePool(multiprocessing.pool.Pool):
    def __init__(self, *args, **kwargs):
        kwargs["context"] = NoDaemonContext()
        super(NestablePool, self).__init__(*args, **kwargs)


def create_pattern(nlp, doc, debug=False):
    pronoun_list = {
        "my",
        "you",
        "it",
        "its",
        "your",
        "i",
        "he",
        "she",
        "his",
        "her",
        "they",
        "them",
        "their",
        "our",
        "we",
    }
    # Filtering concepts consisting of all stop words and longer than four words.
    if (
        len(doc) >= 5
        or doc[0].text in pronoun_list
        or doc[-1].text in pronoun_list
        or all(
            [
                (
                    token.text in nltk_stopwords
                    or token.lemma_ in nltk_stopwords
                    or token.lemma_ in blacklist
                )
                for token in doc
            ]
        )
    ):
        if debug:
            return False, doc.text
        return None  # ignore this concept as pattern

    pattern = []
    for token in doc:  # a doc is a concept
        pattern.append({"LEMMA": token.lemma_})
    if debug:
        return True, doc.text
    return pattern


def lemmatize(nlp, concept):

    doc = nlp(concept.replace("_", " "))
    lcs = set()
    lcs.add("_".join([token.lemma_ for token in doc]))  # all lemma
    return lcs


def ground_qa_pair(qa_pair):
    global nlp, matcher
    s, a = qa_pair
    all_concepts = ground_mentioned_concepts(nlp, matcher, s, a)
    # print("all", all_concepts)
    answer_concepts = ground_mentioned_concepts(nlp, matcher, a)
    # print("ans c", answer_concepts)
    question_concepts = all_concepts - answer_concepts
    # print("ques c", question_concepts)
    if len(question_concepts) == 0:
        question_concepts = hard_ground(nlp, s, CPNET_VOCAB)  # not very possible
        # print("ques c new", question_concepts)

    if len(answer_concepts) == 0:
        answer_concepts = hard_ground(nlp, a, CPNET_VOCAB)  # some case
        # print("ans c new", answer_concepts)

    # question_concepts = question_concepts -  answer_concepts
    question_concepts = sorted(list(question_concepts))
    answer_concepts = sorted(list(answer_concepts))
    return {"sent": s, "ans": a, "qc": question_concepts, "ac": answer_concepts}


def ground_mentioned_concepts(nlp, matcher, s, ans=None):
    s = s.lower()
    doc = nlp(s)
    matches = matcher(doc)
    mentioned_concepts = set()
    span_to_concepts = {}

    if ans is not None:
        ans_matcher = Matcher(nlp.vocab)
        ans_matcher.add(
            ans, [[{"TEXT": token.text.lower()} for token in nlp.tokenizer.pipe(ans)]]
        )

        ans_match = ans_matcher(doc)
        ans_mentions = set()
        for _, ans_start, ans_end in ans_match:
            ans_mentions.add((ans_start, ans_end))

    for match_id, start, end in matches:
        if ans is not None:
            if (start, end) in ans_mentions:
                continue

        span = doc[start:end].text  # the matched span

        original_concept = nlp.vocab.strings[match_id]
        original_concept_set = set()
        original_concept_set.add(original_concept)

        if len(original_concept.split("_")) == 1:
            original_concept_set.update(lemmatize(nlp, nlp.vocab.strings[match_id]))
        if span not in span_to_concepts:
            span_to_concepts[span] = set()
        span_to_concepts[span].update(original_concept_set)

    for span, concepts in span_to_concepts.items():
        concepts_sorted = list(concepts)
        concepts_sorted.sort(key=len)
        shortest = concepts_sorted[0:3]

        for c in shortest:
            if c in blacklist:
                continue

            # a set with one string like: set("like_apples")
            lcs = lemmatize(nlp, c)
            intersect = lcs.intersection(shortest)
            if len(intersect) > 0:
                mentioned_concepts.add(list(intersect)[0])
            else:
                mentioned_concepts.add(c)

        exact_match = set(
            [
                concept
                for concept in concepts_sorted
                if concept.replace("_", " ").lower() == span.lower()
            ]
        )
        assert len(exact_match) < 2
        mentioned_concepts.update(exact_match)
    return mentioned_concepts


def hard_ground(nlp, sent, cpnet_vocab):
    sent = sent.lower()
    doc = nlp(sent)
    res = set()
    for t in doc:
        if t.lemma_ in cpnet_vocab:
            res.add(t.lemma_)
    sent = " ".join([t.text for t in doc])
    if sent in cpnet_vocab:
        res.add(sent)
    try:
        assert len(res) > 0
    except Exception:
        print(f"for {sent}, concept not found in hard grounding.")
    return res


def match_mentioned_concepts(sents, answers, num_processes):
    with Pool(num_processes) as p:
        res = list(tqdm(p.imap(ground_qa_pair, zip(sents, answers)), total=len(sents)))
    return res


# To-do: examine prune
def prune(data, cpnet_vocab):

    prune_data = []
    for item in tqdm(data):
        qc = item["qc"]
        prune_qc = []
        for c in qc:
            if c[-2:] == "er" and c[:-2] in qc:
                continue
            if c[-1:] == "e" and c[:-1] in qc:
                continue
            have_stop = False
            # remove all concepts having stopwords, including hard-grounded ones
            for t in c.split("_"):
                if t in nltk_stopwords:
                    have_stop = True
            if not have_stop and c in cpnet_vocab:
                prune_qc.append(c)

        ac = item["ac"]
        prune_ac = []
        for c in ac:
            if c[-2:] == "er" and c[:-2] in ac:
                continue
            if c[-1:] == "e" and c[:-1] in ac:
                continue
            all_stop = True
            for t in c.split("_"):
                if t not in nltk_stopwords:
                    all_stop = False
            if not all_stop and c in cpnet_vocab:
                prune_ac.append(c)

        try:
            assert len(prune_ac) > 0 and len(prune_qc) > 0
        except Exception as e:
            pass

        item["qc"] = prune_qc
        item["ac"] = prune_ac
        prune_data.append(item)
    return prune_data


def ground(statement, cpnet_vocab, _nlp, _matcher, num_processes=1, debug=False):
    global CPNET_VOCAB
    CPNET_VOCAB = [c.replace("_", " ") for c in cpnet_vocab]

    sents = []
    answers = []
    global matcher, nlp
    matcher = _matcher
    nlp = _nlp
    del _nlp, _matcher

    for sentence in statement["statements"]:
        sents.append(sentence["statement"])

    for answer in statement["choices"]:
        try:
            assert all([i != "_" for i in answer])
        except Exception:
            print(answer)
        answers.append(answer)

    res = match_mentioned_concepts(sents, answers, num_processes)
    res = prune(res, cpnet_vocab)
    print(f"grounding concepts finished ")
    return res
