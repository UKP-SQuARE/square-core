import csv
import json

import requests

response = requests.get("https://square.ukp-lab.de/api/skill-manager/skill")
skills = response.json()

# with open("skills.json") as fh:
#     skills = json.load(fh)

model2url = {
    "bert-base-uncased": "https://huggingface.co/bert-base-uncased",
    "roberta-base": "https://huggingface.co/roberta-base",
    "bart-base": "https://huggingface.co/facebook/bart-base",
    "dpr": "https://huggingface.co/facebook/dpr-ctx_encoder-single-nq-base",
    "distilbert": "https://huggingface.co/sentence-transformers/msmarco-distilbert-base-tas-b",
    "BM25": "https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables",
}
rows = []
for skill in skills:
    if skill["default_skill_args"] is None:
        del skill["default_skill_args"]
    if skill.get("default_skill_args") is None or skill.get(
        "default_skill_args", {}
    ).get("datastore"):
        if skill["name"].lower().startswith("OpenSQuAD".lower()):
            base_model = "bert-base-uncased"
            adapter = "https://huggingface.co/AdapterHub/bert-base-uncased-pf-squad_v2"
            retrieval_model = "dpr"
            datastore = "Wikipedia"
        elif skill["name"].lower().startswith("OpenBioASQ".lower()):
            base_model = "bert-base-uncased"
            adapter = "https://huggingface.co/AdapterHub/bert-base-uncased-pf-squad_v2"
            retrieval_model = "BM25"
            datastore = "Pubmed"
        # elif skill.get("default_skill_args", {}).get("datastore"):
        #     datastore = skill["default_skill_args"]["datastore"]
        #     retrieval_model = skill["default_skill_args"].get("index", "BM25")
        else:
            print(skill)
            continue
        retrieval_model_md = f"[{retrieval_model}]({model2url[retrieval_model]})"
        retrieval_dataset = f" {datastore}"
    else:
        base_model = skill["default_skill_args"]["base_model"]
        adapter = skill["default_skill_args"]["adapter"]
        retrieval_model_md = ""
        retrieval_dataset = ""

    if "pf-" in adapter:
        idx = adapter.find("pf-") + 3
    else:
        idx = adapter.find("/") + 1
    adapter_dataset = adapter[idx:]

    code_link = f"https://github.com/UKP-SQuARE/square-core/blob/master/skills/{skill['url'][skill['url'].find('//')+2:]}/skill.py"
    code_link_md = f"[code]({code_link})"
    reader_model_md = f"[{base_model}]({model2url[base_model]})"
    reader_adapter_md = f"[{adapter_dataset}](https://huggingface.co/{adapter})"

    rows.append(
        [
            skill["name"],
            retrieval_model_md,
            retrieval_dataset,
            reader_model_md,
            reader_adapter_md,
            skill["skill_type"],
            code_link_md,
        ]
    )

rows = sorted(rows, key=lambda s: s[0])
with open("skills.csv", "w") as fh:
    writer = csv.writer(fh)
    writer.writerow(
        [
            "Name",
            "Retrieval Model",
            "Datastore",
            "Reader Model",
            "Reader Adapter",
            "Type",
            "Code",
        ]
    )
    writer.writerows(rows)


def csv_to_md(csv_file_path, type_del=","):
    # creating a file with .md extension for the output file
    output_file = csv_file_path.replace(".csv", ".md")

    # I used encoding UTF-8 as we won't have to worry about errors while decoding contents of a csv file
    csv_dict = csv.DictReader(open(csv_file_path, encoding="UTF-8"), delimiter=type_del)

    # storing the content of csv file in a list_of_rows. Each row is a dict.
    list_of_rows = [dict_row for dict_row in csv_dict]

    # For Headers of the csv file.
    headers = list(list_of_rows[0].keys())

    # The below code block makes md_string as per the required format of a markdown file.
    md_string = " | "
    for header in headers:
        md_string += header + " |"

    md_string += "\n |"
    for i in range(len(headers)):
        md_string += "--- | "

    md_string += "\n"
    for row in list_of_rows:
        md_string += " | "
        for header in headers:
            md_string += row[header] + " | "
        md_string += "\n"

    # writing md_string to the output_file
    file = open(output_file, "w", encoding="UTF-8")
    file.write(md_string)
    file.close()


csv_to_md("skills.csv")
