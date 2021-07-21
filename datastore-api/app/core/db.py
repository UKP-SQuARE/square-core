import os
import shutil
from typing import List

import motor.motor_asyncio
from filelock import FileLock
from vespa.package import QueryProfile, QueryProfileType, Schema

from ..models.index import Index
from .vespa_package_utils import (
    hosts_to_text,
    query_profile_to_text,
    query_profile_type_to_text,
    services_to_text,
    validation_overrides_to_text,
)


class DatastoreDB:
    def __init__(self, mongo_db_string=None):
        mongo_db_string = mongo_db_string or os.environ["MONGODB_URL"]
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_db_string)
        self.db = self.client.square_datastores

    # Schemas

    async def get_schemas(self, limit=200) -> List[Schema]:
        schemas = await self.db.schemas.find().to_list(length=limit)
        for schema_dict in schemas:
            schema_dict.pop("_id")
        return [Schema.from_dict(schema_dict) for schema_dict in schemas]

    async def get_schema(self, schema_name: str) -> Schema:
        schema_dict = await self.db.schemas.find_one({"name": schema_name})
        if schema_dict is not None:
            schema_dict.pop("_id")
            return Schema.from_dict(schema_dict)
        else:
            return None

    async def add_schema(self, schema: Schema):
        result = await self.db.schemas.insert_one(schema.to_dict)
        return result.inserted_id

    async def update_schema(self, schema: Schema) -> bool:
        result = await self.db.schemas.update_one({"name": schema.name}, {"$set": schema.to_dict})
        return result.modified_count > 0

    async def delete_schema(self, schema_name: str) -> bool:
        result = await self.db.schemas.delete_one({"name": schema_name})
        return result.deleted_count > 0

    # Indices

    async def get_indices(self, datastore_name: str, limit=200) -> List[Index]:
        indices = await self.db.indices.find({"datastore_name": datastore_name}).to_list(length=limit)
        for index_dict in indices:
            index_dict.pop("_id")
        return [Index(**index_dict) for index_dict in indices]

    async def get_index(self, datastore_name: str, index_name: str) -> Index:
        index_dict = await self.db.indices.find_one({"datastore_name": datastore_name, "name": index_name})
        if index_dict is not None:
            index_dict.pop("_id")
            return Index(**index_dict)
        else:
            return None

    async def add_index(self, index: Index):
        result = await self.db.indices.insert_one(index.dict())
        return result.inserted_id

    async def update_index(self, index: Index):
        result = await self.db.indices.update_one(
            {"datastore_name": index.datastore_name, "name": index.name}, {"$set": index.dict()}
        )
        return result.modified_count > 0

    async def delete_index(self, datastore_name: str, index_name: str) -> bool:
        result = await self.db.indices.delete_one({"datastore_name": datastore_name, "name": index_name})
        return result.deleted_count > 0

    # # Query profiles

    async def get_query_profiles(self, limit=200) -> List[QueryProfile]:
        items = await self.db.query_profiles.find().to_list(length=limit)
        for item_dict in items:
            item_dict.pop("_id")
        return [QueryProfile.from_dict(item_dict) for item_dict in items]

    async def add_query_profile(self, query_profile: QueryProfile):
        result = await self.db.query_profiles.insert_one(query_profile.to_dict)
        return result.inserted_id

    async def delete_query_profile(self, query_profile_name: str) -> bool:
        result = await self.db.query_profiles.delete_one({"name": query_profile_name})
        return result.deleted_count > 0

    # Query profile types

    async def get_query_profile_types(self, limit=200) -> List[QueryProfileType]:
        items = await self.db.query_profile_types.find().to_list(length=limit)
        for item_dict in items:
            item_dict.pop("_id")
        return [QueryProfileType.from_dict(item_dict) for item_dict in items]

    async def add_query_profile_type(self, query_profile_type: QueryProfileType):
        result = await self.db.query_profile_types.insert_one(query_profile_type.to_dict)
        return result.inserted_id

    async def delete_query_profile_type(self, query_profile_type_name: str) -> bool:
        result = await self.db.query_profile_types.delete_one({"name": query_profile_type_name})
        return result.deleted_count > 0

    # Export

    async def export(self, folder: str, allow_content_removal: bool = False):
        lock_file = folder + ".lock"
        with FileLock(lock_file):
            # Delete the whole folder if it exists
            if os.path.exists(folder):
                shutil.rmtree(folder)

            # Create the root folder as well as all required subfolders
            os.makedirs(folder)
            os.makedirs(os.path.join(folder, "schemas"))
            os.makedirs(os.path.join(folder, "search", "query-profiles", "types"))

            # Get schemas, extend by indices & write to folder
            schemas = await self.get_schemas()
            for schema in schemas:
                indices = await self.get_indices(schema.name)
                for index in indices:
                    embedding_field = index.get_vespa_embedding_field()
                    if embedding_field is not None:
                        schema.add_fields(embedding_field)
                    schema.add_rank_profile(index.get_vespa_rank_profile())
                with open(os.path.join(folder, "schemas", schema.name + ".sd"), "w") as f:
                    f.write(schema.schema_to_text)
            # Write query profiles to folder
            query_profiles = await self.get_query_profiles()
            for query_profile in query_profiles:
                with open(os.path.join(folder, "search", "query-profiles", query_profile.name + ".xml"), "w") as f:
                    f.write(query_profile_to_text(query_profile))
            # Write query profile types to folder
            query_profile_types = await self.get_query_profile_types()
            for query_profile_type in query_profile_types:
                with open(
                    os.path.join(folder, "search", "query-profiles", "types", query_profile_type.name + ".xml"), "w"
                ) as f:
                    f.write(query_profile_type_to_text(query_profile_type))

            # Write hosts, services & validation overrides to folder
            with open(os.path.join(folder, "hosts.xml"), "w") as f:
                f.write(hosts_to_text())
            with open(os.path.join(folder, "services.xml"), "w") as f:
                f.write(services_to_text("square_datastore", schemas))
            if allow_content_removal:
                with open(os.path.join(folder, "validation-overrides.xml"), "w") as f:
                    f.write(validation_overrides_to_text())


db = DatastoreDB()
