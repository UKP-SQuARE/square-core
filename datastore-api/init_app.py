import asyncio

from vespa.package import Document, Field, QueryProfile, QueryProfileType, Schema, FieldSet, QueryTypeField

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
                    Field("title", "string", indexing=["summary", "index"], index="enable-bm25"),
                    Field("text", "string", indexing=["summary", "index"], index="enable-bm25"),
                    Field("id", "long", indexing=["summary", "attribute"]),
                ]
            ),
            # TODO add this dataset creation via API
            fieldsets=[FieldSet(name="default", fields=["title", "text"])],
        )
    )
    await db.add_index(
        Index(
            datastore_name="wiki",
            name="bm25",
            query_yql="select * from sources wiki where userQuery();",
            embedding_type=None,
            hnsw=None,
            first_phase_ranking="bm25(title) + bm25(text)",
            second_phase_ranking=None,
        )
    )
    await db.add_index(
        Index(
            datastore_name="wiki",
            name="dpr",
            query_yql='select * from sources wiki where ([{"targetNumHits":100, "hnsw.exploreAdditionalHits":100}]nearestNeighbor(dpr_embedding,query_embedding)) or userQuery();',
            doc_encoder_model="facebook/dpr-ctx_encoder-single-nq-base",
            query_encoder_model="facebook/dpr-question_encoder-single-nq-base",
            embedding_type="tensor<float>(x[769])",
            hnsw={"distance_metric": "euclidean", "max_links_per_node": 16, "neighbors_to_explore_at_insert": 500},
            first_phase_ranking="closeness(dpr_embedding)",
            second_phase_ranking=None,
        )
    )

    # TODO: Apparently, we need to specify type of the query embedding here. But this doens't support different sizes.
    await db.add_query_profile_type(QueryProfileType(fields=[
        QueryTypeField("ranking.features.query(query_embedding)", "tensor<float>(x[769])")
    ]))
    await db.add_query_profile(QueryProfile())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(recreate_db())
    loop.run_until_complete(generate_and_upload_package(allow_content_removal=True))
