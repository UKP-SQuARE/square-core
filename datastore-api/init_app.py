import asyncio

from vespa.package import Document, QueryField, QueryProfile, QueryProfileType, QueryTypeField, Schema, Field

from app.core.db import db
from app.core.generate_package import generate_and_upload_package


async def recreate_db():
    await db.client.drop_database("square_datastores")
    await db.add_schema(
        Schema("wiki", Document(fields=[Field("id", "long"), Field("title", "string"), Field("text", "string")]))
    )
    await db.add_schema(
        Schema("news", Document(fields=[Field("id", "long"), Field("title", "string"), Field("text", "string")]))
    )
    # Query profile types
    root_query_profile_type = QueryProfileType(
        fields=[
            QueryTypeField(name="ranking.features.query(query_embedding)", type="tensor<float>(x[769])"),
            QueryTypeField(name="datastore_name", type="string"),
        ]
    )
    await db.add_query_profile_type(root_query_profile_type)
    # Query profiles
    bm25_query_profile = QueryProfile(
        fields=[
            QueryField(name="rankings.profile", value="bm25"),
            QueryField(name="yql", value="select * from sources %{datastore_name} where userQuery();"),
        ]
    )
    await db.add_query_profile(bm25_query_profile)
    # dense_query_profile = QueryProfile(fields=[
    #     QueryField(name="rankings.profile", value="dense-retrieval"),
    #     QueryField(name="yql", value="select * from sources %{datastore_name} where ([{\"targetNumHits\":100, \"hnsw.exploreAdditionalHits\":100}]nearestNeighbor(text_embedding,query_embedding)) or userQuery();"),
    # ])
    # dense_query_profile.name = "dense-retrieval"
    # await db.add_query_profile(dense_query_profile)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(recreate_db())
    loop.run_until_complete(generate_and_upload_package(allow_content_removal=True))
