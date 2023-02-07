import json
from datetime import date
from queue import Queue

from value_class import ValueClass


class DataForSPARQL(object):
    def __init__(self, kb_path):
        kb = json.load(open(kb_path))
        self.concepts = kb["concepts"]
        self.entities = kb["entities"]

        # replace adjacent space and tab in name, which may cause errors when building sparql query
        for con_id, con_info in self.concepts.items():
            con_info["name"] = " ".join(con_info["name"].split())
        for ent_id, ent_info in self.entities.items():
            ent_info["name"] = " ".join(ent_info["name"].split())

        # get all attribute keys and predicates
        self.attribute_keys = set()
        self.predicates = set()
        self.key_type = {}
        for ent_id, ent_info in self.entities.items():
            for attr_info in ent_info["attributes"]:
                self.attribute_keys.add(attr_info["key"])
                self.key_type[attr_info["key"]] = attr_info["value"]["type"]
                for qk in attr_info["qualifiers"]:
                    self.attribute_keys.add(qk)
                    for qv in attr_info["qualifiers"][qk]:
                        self.key_type[qk] = qv["type"]
        for ent_id, ent_info in self.entities.items():
            for rel_info in ent_info["relations"]:
                self.predicates.add(rel_info["predicate"])
                for qk in rel_info["qualifiers"]:
                    self.attribute_keys.add(qk)
                    for qv in rel_info["qualifiers"][qk]:
                        self.key_type[qk] = qv["type"]
        self.attribute_keys = list(self.attribute_keys)
        self.predicates = list(self.predicates)
        # Note: key_type is one of string/quantity/date, but date means the key may have values of type year
        self.key_type = {
            k: v if v != "year" else "date" for k, v in self.key_type.items()
        }

        # parse values into ValueClass object
        for ent_id, ent_info in self.entities.items():
            for attr_info in ent_info["attributes"]:
                attr_info["value"] = self._parse_value(attr_info["value"])
                for qk, qvs in attr_info["qualifiers"].items():
                    attr_info["qualifiers"][qk] = [self._parse_value(qv) for qv in qvs]
        for ent_id, ent_info in self.entities.items():
            for rel_info in ent_info["relations"]:
                for qk, qvs in rel_info["qualifiers"].items():
                    rel_info["qualifiers"][qk] = [self._parse_value(qv) for qv in qvs]

    def _parse_value(self, value):
        if value["type"] == "date":
            x = value["value"]
            p1, p2 = x.find("/"), x.rfind("/")
            y, m, d = int(x[:p1]), int(x[p1 + 1 : p2]), int(x[p2 + 1 :])
            result = ValueClass("date", date(y, m, d))
        elif value["type"] == "year":
            result = ValueClass("year", value["value"])
        elif value["type"] == "string":
            result = ValueClass("string", value["value"])
        elif value["type"] == "quantity":
            result = ValueClass("quantity", value["value"], value["unit"])
        else:
            raise Exception("unsupport value type")
        return result

    def get_direct_concepts(self, ent_id):
        """
        return the direct concept id of given entity/concept
        """
        if ent_id in self.entities:
            return self.entities[ent_id]["instanceOf"]
        elif ent_id in self.concepts:
            return self.concepts[ent_id]["instanceOf"]
        else:
            raise Exception("unknown id")

    def get_all_concepts(self, ent_id):
        """
        return a concept id list
        """
        ancestors = []
        q = Queue()
        for c in self.get_direct_concepts(ent_id):
            q.put(c)
        while not q.empty():
            con_id = q.get()
            ancestors.append(con_id)
            for c in self.concepts[con_id]["instanceOf"]:
                q.put(c)

        return ancestors

    def get_name(self, ent_id):
        if ent_id in self.entities:
            return self.entities[ent_id]["name"]
        elif ent_id in self.concepts:
            return self.concepts[ent_id]["name"]
        else:
            return None

    def is_concept(self, ent_id):
        return ent_id in self.concepts

    def get_attribute_facts(self, ent_id, key=None, unit=None):
        if key:
            facts = []
            for attr_info in self.entities[ent_id]["attributes"]:
                if attr_info["key"] == key:
                    if unit:
                        if attr_info["value"].unit == unit:
                            facts.append(attr_info)
                    else:
                        facts.append(attr_info)
        else:
            facts = self.entities[ent_id]["attributes"]
        facts = [(f["key"], f["value"], f["qualifiers"]) for f in facts]
        return facts

    def get_relation_facts(self, ent_id):
        facts = self.entities[ent_id]["relations"]
        facts = [
            (f["predicate"], f["object"], f["direction"], f["qualifiers"])
            for f in facts
        ]
        return facts
