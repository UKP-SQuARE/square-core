import argparse
import json

import requests
import tqdm


class DatastoreAPIClient:
    def __init__(self, url, token, upload_batch_size=500):
        self.url = url
        self.token = token
        self.upload_batch_size = upload_batch_size

    def _post_documents(self, datastore_name, documents):
        headers = {"Authorization": self.token}
        response = requests.post(self.url + f"/datastores/{datastore_name}/documents", json=documents, headers=headers)
        response.raise_for_status()
        return response.json()

    def upload_tsv(self, datastore_name, tsv_file, max_documents=None):
        batch = []

        if not max_documents:
            max_documents = sum(1 for line in open(tsv_file, "r"))
        with open(tsv_file, "r") as f:
            header = f.readline().strip().split("\t")
            for i, line in enumerate(tqdm.tqdm(f, total=max_documents)):
                if i == max_documents:
                    break

                line = line.strip().split("\t")
                data = dict(zip(header, line))
                batch.append(data)

                if len(batch) == self.upload_batch_size:
                    self._post_documents(datastore_name, batch)
                    batch = []

            self._post_documents(datastore_name, batch)
            print(f"Successfully uploaded {i} documents.")

    def upload_jsonl(self, datastore_name, jsonl_file, max_documents=None, field_mappings=None):
        batch = []

        if not max_documents:
            max_documents = sum(1 for line in open(jsonl_file, "r"))
        with open(jsonl_file, "r") as f:
            for i, line in enumerate(tqdm.tqdm(f, total=max_documents)):
                if i == max_documents:
                    break

                item = json.loads(line)
                if field_mappings:
                    for k, v in item.items():
                        if k in field_mappings:
                            item[field_mappings[k]] = v
                            del item[k]
                batch.append(item)

                if len(batch) == self.upload_batch_size:
                    self._post_documents(datastore_name, batch)
                    batch = []

            self._post_documents(datastore_name, batch)
            print(f"Successfully uploaded {i} documents.")


def main():
    parser = argparse.ArgumentParser(description="Upload documents to the SQuARE Datastore API.")
    parser.add_argument("file", type=str, help="TSV or JSONL file to upload")
    parser.add_argument(
        "-u", "--url", type=str, default="http://localhost:7000", help="URL of the SQuARE Datastore API"
    )
    parser.add_argument("-t", "--token", type=str, help="API token for the SQuARE Datastore API")
    parser.add_argument("-s", "--datastore", type=str, help="name of the SQuARE Datastore to upload to")
    parser.add_argument("--batch-size", type=int, default=500, help="number of documents to upload in a batch")
    parser.add_argument("--max-documents", type=int, default=None, help="maximum number of documents to upload")
    parser.add_argument("--field-mappings", type=lambda x: x.split(";"), default="", help="Field mappings")

    args = parser.parse_args()

    field_mappings = {}
    for mapping in args.field_mappings:
        if mapping:
            k, v = mapping.split(":")
            field_mappings[k] = v

    client = DatastoreAPIClient(args.url, args.token, args.batch_size)
    if args.file.lower().endswith(".tsv"):
        client.upload_tsv(args.datastore, args.file, args.max_documents)
    elif args.file.lower().endswith(".jsonl"):
        client.upload_jsonl(args.datastore, args.file, args.max_documents, field_mappings=field_mappings)
    else:
        raise ValueError("File must be a TSV or JSONL file.")


if __name__ == "__main__":
    main()
