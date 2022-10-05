import re
from typing import List

BLANK_STR = "___"


# Identify the wh-word in the question and replace with a blank
def replace_wh_word_with_blank(question_str: str):
    # if "What is the name of the government building that houses the U.S. Congress?" in question_str:
    #     print()
    question_str = question_str.replace("What's", "What is")
    question_str = question_str.replace("whats", "what")
    question_str = question_str.replace("U.S.", "US")
    wh_word_offset_matches = []
    wh_words = ["which", "what", "where", "when", "how", "who", "why"]
    for wh in wh_words:
        # Some Turk-authored SciQ questions end with wh-word
        # E.g. The passing of traits from parents to offspring is done through what?

        if wh == "who" and "people who" in question_str:
            continue

        m = re.search(wh + r"\?[^\.]*[\. ]*$", question_str.lower())
        if m:
            wh_word_offset_matches = [(wh, m.start())]
            break
        else:
            # Otherwise, find the wh-word in the last sentence
            m = re.search(wh + r"[ ,][^\.]*[\. ]*$", question_str.lower())
            if m:
                wh_word_offset_matches.append((wh, m.start()))
            # else:
            #     wh_word_offset_matches.append((wh, question_str.index(wh)))

    # If a wh-word is found
    if len(wh_word_offset_matches):
        # Pick the first wh-word as the word to be replaced with BLANK
        # E.g. Which is most likely needed when describing the change in position of an object?
        wh_word_offset_matches.sort(key=lambda x: x[1])
        wh_word_found = wh_word_offset_matches[0][0]
        wh_word_start_offset = wh_word_offset_matches[0][1]
        # Replace the last question mark with period.
        question_str = re.sub(r"\?$", "", question_str.strip())
        # Introduce the blank in place of the wh-word
        fitb_question = (question_str[:wh_word_start_offset] + BLANK_STR +
                         question_str[wh_word_start_offset + len(wh_word_found):])
        # Drop "of the following" as it doesn't make sense in the absence of a multiple-choice
        # question. E.g. "Which of the following force ..." -> "___ force ..."
        final = fitb_question.replace(BLANK_STR + " of the following", BLANK_STR)
        final = final.replace(BLANK_STR + " of these", BLANK_STR)
        return final

    elif " them called?" in question_str:
        return question_str.replace(" them called?", " " + BLANK_STR + ".")
    elif " meaning he was not?" in question_str:
        return question_str.replace(" meaning he was not?", " he was not " + BLANK_STR + ".")
    elif " one of these?" in question_str:
        return question_str.replace(" one of these?", " " + BLANK_STR + ".")
    elif re.match(r".*[^\.\?] *$", question_str):
        # If no wh-word is found and the question ends without a period/question, introduce a
        # blank at the end. e.g. The gravitational force exerted by an object depends on its
        return question_str + " " + BLANK_STR
    else:
        # If all else fails, assume "this ?" indicates the blank. Used in Turk-authored questions
        # e.g. Virtually every task performed by living organisms requires this?
        return re.sub(r" this[ \?]", " ___ ", question_str)


def create_hypothesis(question: str, choice: str) -> str:
    """
    Create a hypothesis statement from the input fill-in-the-blank
    statement and answer choice.
    """
    fitb = replace_wh_word_with_blank(question)
    if not re.match(".*_+.*", fitb):
        # print("Can't create hypothesis from: '{}'. Appending {} !".format(question_text, BLANK_STR))
        # Strip space, period and question mark at the end of the question and add a blank
        fitb = re.sub(r"[\.\? ]*$", "", question.strip()) + " " + BLANK_STR

    if ". " + BLANK_STR in fitb or fitb.startswith(BLANK_STR):
        choice = choice[0].upper() + choice[1:]
    else:
        choice = choice.lower()
    # Remove period from the answer choice, if the question doesn't end with the blank
    if not fitb.endswith(BLANK_STR):
        choice = choice.rstrip(".")
    # Some questions already have blanks indicated with 2+ underscores
    try:
        hypothesis = re.sub("__+", choice, fitb)
        return hypothesis
    except:
        print(choice, fitb)


def convert_to_entailment(input: List):
    prepared_input = dict()
    prepared_input["question"] = input[0][0]
    prepared_input["choices"] = [inp[1] for inp in input]
    if "statements" not in prepared_input:
        prepared_input["statements"] = []
    for idx, inp in enumerate(input):
        statement = create_hypothesis(inp[0], inp[1])
        # Create the output dictionary from the input, premise and hypothesis statement
        prepared_input["statements"].append({"label": True if idx == 0 else False, "statement": statement})
    return prepared_input
