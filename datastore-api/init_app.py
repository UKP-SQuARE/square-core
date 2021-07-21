import asyncio

from vespa.package import Document, Field, QueryProfile, QueryProfileType, Schema

from app.core.db import db
from app.core.generate_package import generate_and_upload_package
from app.models.index import Index


async def recreate_db():
    await db.client.drop_database("square_datastores")
    await db.add_schema(
        Schema(
            "wiki",
            Document(
                fields=[
                    Field("id", "long"),
                    Field("title", "string", indexing=["index", "summary"], index="enable-bm25"),
                    Field("text", "string", indexing=["index", "summary"], index="enable-bm25"),
                ]
            ),
        )
    )
    await db.add_index(
        Index(
            datastore_name="wiki",
            name="bm25",
            query_yql="select * from sources %{datastore_name} where userQuery();",
            document_encoder="",
            embedding_type=None,
            hnsw=None,
            first_phase_ranking="bm25(title) + bm25(text)",
            second_phase_ranking=None,
        )
    )
    await db.add_index(
        Index(
            datastore_name="wiki",
            name="dense_retrieval",
            query_yql='select * from sources %{datastore_name} where ([{"targetNumHits":100, "hnsw.exploreAdditionalHits":100}]nearestNeighbor(text_embedding,query_embedding)) or userQuery();',
            document_encoder="",
            embedding_type="tensor<float>(x[769])",
            hnsw={"distance_metric": "euclidean", "max_links_per_node": 16, "neighbors_to_explore_at_insert": 500},
            first_phase_ranking="closeness(dense_retrieval)",
            second_phase_ranking=None,
        )
    )

    await db.add_query_profile_type(QueryProfileType())
    await db.add_query_profile(QueryProfile())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(recreate_db())
    loop.run_until_complete(generate_and_upload_package(allow_content_removal=True))
