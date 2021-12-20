"""
A simple CLI script to upload documents to the SQuARE Datastore API.
"""
import argparse
import json

import requests
import tqdm


class DatastoreAPIClient:
    def __init__(self, url, token, upload_batch_size=1000):
        self.url = url
        self.token = token
        self.upload_batch_size = upload_batch_size

    def _get_datastore_schema(self, datastore_name):
        headers = {"Authorization": self.token}
        response = requests.get(self.url + f"/datastores/{datastore_name}", headers=headers)
        response.raise_for_status()
        return response.json()

    def _get_id_field(self, schema):
        field = next((field for field in schema["fields"] if field["is_id"]), None)
        if field:
            return field["name"]
        else:
            return None

    def _post_documents(self, datastore_name, documents):
        headers = {"Authorization": self.token}
        response = requests.post(self.url + f"/datastores/{datastore_name}/documents", json=documents, headers=headers)
        response.raise_for_status()
        return response.json()

    def upload_tsv(self, datastore_name, tsv_file, max_documents=None, field_mappings=None, remove_fields=None):
        schema = self._get_datastore_schema(datastore_name)
        id_field = self._get_id_field(schema)
        batch = []

        if not max_documents:
            max_documents = sum(1 for line in tqdm.tqdm(open(tsv_file, "rb"), desc="Estimating upload"))
        with open(tsv_file, "r") as f:
            header = f.readline().strip().split("\t")
            if remove_fields:
                remove_indices = [header.index(field) for field in remove_fields]
                header = [field for field in header if field not in remove_fields]
            else:
                remove_indices = []
            if field_mappings:
                header = [field_mappings[h] if h in field_mappings else h for h in header]

            for i, line in enumerate(tqdm.tqdm(f, total=max_documents)):
                if i == max_documents:
                    break

                fields = []
                for i, field in enumerate(line.strip().split("\t")):
                    if i in remove_indices:
                        continue
                    fields.append(field)
                data = dict(zip(header, fields))
                # check id
                if id_field in data:
                    data[id_field] = int(data[id_field])
                else:
                    data[id_field] = i
                batch.append(data)

                if len(batch) == self.upload_batch_size:
                    self._post_documents(datastore_name, batch)
                    batch = []

            self._post_documents(datastore_name, batch)
            print(f"Successfully uploaded {i} documents.")

    def upload_jsonl(self, datastore_name, jsonl_file, max_documents=None, field_mappings=None, remove_fields=None):
        schema = self._get_datastore_schema(datastore_name)
        id_field = self._get_id_field(schema)
        batch = []

        if not max_documents:
            max_documents = sum(1 for line in tqdm.tqdm(open(jsonl_file, "rb"), desc="Estimating upload"))
        with open(jsonl_file, "r") as f:
            for i, line in enumerate(tqdm.tqdm(f, total=max_documents)):
                if i == max_documents:
                    break

                item = json.loads(line)
                if remove_fields:
                    for field in remove_fields:
                        item.pop(field, None)
                if field_mappings:
                    for k, v in list(item.items()):
                        if k in field_mappings:
                            item[field_mappings[k]] = v
                            del item[k]
                # check id
                if id_field in item:
                    item[id_field] = int(item[id_field])
                else:
                    item[id_field] = i
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
    parser.add_argument("--batch-size", type=int, default=1000, help="number of documents to upload in a batch")
    parser.add_argument("--max-documents", type=int, default=None, help="maximum number of documents to upload")
    parser.add_argument("--field-mappings", type=lambda x: x.split(";"), default="", help="Field mappings")
    parser.add_argument("--remove-fields", type=lambda x: x.split(";"), default="", help="Fields to remove")

    args = parser.parse_args()

    field_mappings = {}
    for mapping in args.field_mappings:
        if mapping:
            k, v = mapping.split(":")
            field_mappings[k] = v

    client = DatastoreAPIClient(args.url, args.token, args.batch_size)
    if args.file.lower().endswith(".tsv"):
        client.upload_tsv(
            args.datastore,
            args.file,
            args.max_documents,
            field_mappings=args.field_mappings,
            remove_fields=args.remove_fields,
        )
    elif args.file.lower().endswith(".jsonl"):
        client.upload_jsonl(
            args.datastore,
            args.file,
            args.max_documents,
            field_mappings=field_mappings,
            remove_fields=args.remove_fields,
        )
    else:
        raise ValueError("File must be a TSV or JSONL file.")


if __name__ == "__main__":
    main()
