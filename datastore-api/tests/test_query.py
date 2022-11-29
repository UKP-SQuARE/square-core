import asyncio
from unittest.mock import patch

import pytest
from app.core.faiss import FaissClient
from app.core.model_api import ModelAPIClient
from app.models.query import QueryResult
from requests_mock import Mocker


class TestQuery:
    @pytest.fixture
    def query_result(self, query_document):
        return QueryResult(score=0, document=query_document, id=query_document.id)

    def test_search_bm25(self, client, datastore_name, query_document, query_result):
        response = client.get(
            "/datastores/{}/search".format(datastore_name),
            params={"query": "quack"},
        )
        assert response.status_code == 200
        assert response.json()[0]["document"] == query_result.document.__root__

    def test_search_dpr(
        self,
        requests_mock: Mocker,
        client,
        datastore_name,
        dpr_index,
        query_document,
        query_result,
    ):
        requests_mock.real_http = True
        requests_mock.post(
            f"{FaissClient.build_faiss_url(datastore_name, dpr_index.name)}/search",
            json=[
                {query_document["id"]: -5}
            ],  # use an impossible score to test that this return value is used
        )
        model_api_return = {
            "model_outputs": {
                "embeddings": "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"
            }
        }
        with patch.object(ModelAPIClient, "predict") as mock_predict:
            f = asyncio.Future()
            f.set_result(model_api_return)
            mock_predict.return_value = f
            response = client.get(
                "/datastores/{}/search".format(datastore_name),
                params={"index_name": "dpr", "query": "quack"},
            )
        assert response.status_code == 200
        assert response.json()[0]["document"] == query_result.document.__root__
        assert response.json()[0]["score"] == -5

    def test_search_not_found(self, client, datastore_name):
        response = client.get(
            "/datastores/{}/search".format(datastore_name),
            params={"query": "quack", "index_name": "unknown_index"},
        )
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_search_by_vector(
        self,
        requests_mock: Mocker,
        client,
        datastore_name,
        dpr_index,
        query_document,
        query_result,
    ):
        requests_mock.real_http = True
        requests_mock.post(
            f"{FaissClient.build_faiss_url(datastore_name, dpr_index.name)}/search",
            json=[
                {query_document["id"]: -5}
            ],  # use an impossible score to test that this return value is used
        )

        response = client.post(
            "/datastores/{}/search_by_vector".format(datastore_name),
            json={"index_name": dpr_index.name, "query_vector": [0] * 768},
        )
        assert response.status_code == 200
        assert response.json()[0]["document"] == query_result.document.__root__
        assert response.json()[0]["score"] == -5

    def test_score(self, client, datastore_name, query_document, query_result):
        response = client.get(
            "/datastores/{}/score".format(datastore_name),
            params={"query": "quack", "doc_id": query_document["id"]},
        )
        assert response.status_code == 200
        assert "document" in response.json()
        assert response.json()["document"] == query_result.document.__root__

    def test_score_dpr(
        self,
        requests_mock: Mocker,
        client,
        datastore_name,
        dpr_index,
        query_document,
        query_result,
    ):
        requests_mock.real_http = True
        requests_mock.post(
            f"{FaissClient.build_faiss_url(datastore_name, dpr_index.name)}/explain",
            json={
                "score": -5
            },  # use an impossible score to test that this return value is used
        )

        model_api_return = {
            "model_outputs": {
                "embeddings": "k05VTVBZAQB2AHsnZGVzY3InOiAnPGY0JywgJ2ZvcnRyYW5fb3JkZXInOiBGYWxzZSwgJ3NoYXBlJzogKDEsIDc2OCksIH0gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIArI1oW9hFirPiHlXb6Qx4A9hlMmPUJnjT48sZU8svW7PoI26b4tkGY9SxMgvkPpd76EDYW+dlm+Pi5AD75v/XS+sJWHPfH8qL6i8q2+R/TIPkbmLT86lAI9XXbivjWh1L1kkQA+yO7JPXVgwL3MaW8+lN2hvvroyr6/cHy+xicuPf7lWjx8JnG+wqVRvn+BTT4GzTe+3gyiPtRIir7SmS8+qKqEvFiSQj4Ml/Y+/70svlzHzb24NAo+8RURP3jmxL7KqAa+wqWMvtowDL7MZfU81ixpvSCJK77A+bC+O051vqQZnT6Zzr6+2aqKPcOks74UFLM+YE0VvDLuLb5+Vho+WkYrvuCyND9bHo69IBgMP7PYAL9LQPM+NkIpPcKGNj98NmW+vFx2PtCQhT0YvjS+Po8hvbuqTD5WELC+oCA5PqRQ77xFO5A9+tK/Pi6g8j5yMR09UcYHv5MWtbx5w7u9HrtyvlUC+z5NhN8+WAgCPbVcVr427Le+049xvkC5mL7++wG+BChQvuz+3712Hvg83h0fPdi3kb6sl7C9uzQhP1/bYD4gN7Q+tDy6PB3Mrb5SS6Q+CfFUPy55VT6vq7w9dQNIPtGKjL1/mve+TDooPVb1b74KGRi/Z7ibPrhHUb764Ja+qUHSvq53cz4iNwg/BV7RPDzHzL6YXKm9DB+ZvvDHV75wPWK94O1tPP7L9T6goM26xG+avoJwnT0gJ+S7yy3evVcdnD4IPh6+QMYMPj7xMj7FA7o+iTpGviB2eT56nzA+sNJIvMnI2L6js70+doQzvUzI7Lww28++pGCNvjC7ED4ACEG/aJazvjSkkr4MwY6+K/6Yvf6Siz7osDQ+COIgPjwhsz0aRpO+aJS2vkKeXr2Mno+95byIvu7mQ74bQd69y1UevpRTob0pX3W+BcEKP5xHtb3mvya+PigMPjZ/rD7cBaG+2UofvSW+aj5xHiLA/u8ovTilzDubytY+Ebayvuz4vb7cQrw+Z8LvvgCZ2LogKAA8lqXYvuphkD0oPF++5VmrPnzpFz8GIdg+qDj3Pbu9uL2wuJS8ilNrvgB6kTzYl7O964fCPhmPRb6cZ/+9TPAEPgbdCz44o7W748fmPYav/z3UuA2/yMmzPvCl9j1TUBu/ihV4PvLNxr2zwEO935oMv0CBC7+UjJC+zsonPSASv76AdfW5bszZPZnvrL0iw8s+7vEoPjTQTj3xb9M9Kls2PgfliT7hRHu+EeRzPnwqJj7ccPu+lQJVPdD2PL43BT++POyhvijGgL5YCLa+PJEjPtg7sr2Qktg7cLmEPRCsrL590wW+ikbBPioFnb4uhT6++7oDvdBK1z5ycjo/bKyhvQ4zAD/cSza+Rt0ZP0CH5Dxolzk+ocUQPkmxyD44eF0+uxWDP1BF9Lytgw2/zIOqvkKJBD/aMKk+XxiHvREVlj5H1zg+sJilOxAYO75yLvQ+A3o8PrNwBb/Q9LA+POINPho4Gz6UP3G8gxlsvimUbj4cVnS/vbM2PpxOQD9AtJK+3hQnvotEjD88HS2+0LTNPJ/8lb4Aig8+8Ou5vrAr0by6K2i9V5SIPt4Hkj7cwI697wD0PRh1wbtSgui9gaaTPjP6Rj7+YwY++4GIv60+VL5Wp9m9s1kZv9pMbMCQBpU9IOuJPLZuO774/A0/QsXnPpryeb6q/yq+9oCNvqciUz4x3SC+GPepvlxU3T3Vb4E+PNgvPtghKL4lUCC/a9wnPlsxDb4MwhE+CJIrPpKf1r2Pmhg+SxGNvsOVhz6bgbS9/k1Kv3JnNT0Rl4s9bwOCvh3UAr7wmBy/QLttu5o7ET6k72m+392NvsAEGb7XSSI+BeAXP62lyD37FT++E2u5PtxaFz5WLpS9+SmtPgy+Tj7HDpi9fmKBvvoQsz502vY83L4ovbJf172TIX6+XeMnvssgHT4lq5u+JfUyPvE/RD8C06S+9qJhvXClsT45/ge+s+CovgqsA74A2nS+etsEvrwKEb81BgE/Yil1PnhtHbxIPsA78vmqvhI6AL45aRC/7ElZPjhRAb33K/K+GHOevqwzXz1ZW6E+ZEUBPq7ojb6WG5O+A1UsPmS8tL6Y/F6/8oIEv4GHuL5oGzq9ommgvkqr7z2ZQsG+sGKGvKAm6b6JwNS+VekfvnwWH700G0w+Opi9vQx6JD+Ajag7fjc/vTcoqT6AueK9PAd0PPRWez50z9e9/1HnPYF8YD4QvII+qKkvvp6uIL4iqi292pAqPZW3CL92R0k+5O/fvUwmhT5iBRS/KET6vbc96T6cp2Q+AfubvoajaL4SCKe92qsOPkJlUD5u2Qy/uchlvqiGA7+adIK+Nja9PjBfZD64QXi+gce6PnwlMr6jKq++wviMvcD43L4putk+Qe9qPuQpOb3EriA/8+6pPsdqVr6a7JA+6JiVPnKKnb5wygE+hClevcTXX77lPiy/yCosvndAHz5Oeca9W0vivtGZzz4+ECQ+n78nPngyNT1jBw4+61iFvkS1Lz0cqJW+ePOSvIQwYD0z/N8+MrBMPuDGQD0qeZ8+zgtPPrSMFT6wsLs7RyMVvtr6nL6mamK+teu4veL9fD0kUmg9eFcOPybj6D3af3M+pjyRPnht8r5UZ6o8ZsfPvtMjlr2cnYU9yPPMPgsKTL+v8fO+W+uYPoACkzyktFQ9ojERvmYkvr09IBc+nDUpP8ODj76vrRI/miTyPbWKtr6KWdo99nZTPne7+z6ijo08cK0tPBib8b7spaY+AYC7PbtZBb5vLgC+uBSAvTgAjL7cMrM+e5mlvoqRBL2uPwC+4LEXvW7wSj60lSW/FSHXPgCW5jtCRYM9UY3Hvqwh2b08XZm+GnHKPpxqO758jCs9Zyy2PU6cOb/lEb0+XxwOvvAwf7yZlQS/M3ftPm/1gb3BpCy+S6W9Pq4xm77FJc498KcNPpdLL73Ga5i9pLmqPAjHQz47IJM/ZDoTPlB91Tx0WFs+JSWRvUzKnr7SxJi+thYlvqwOnz6XLfG+4sV1vQ7jYD5B1+C+t5zvvUXEnj5WYwg+IuZNPhBKjb4iTEY9xJbKPdAc/T0sKU29No2mPV8EqT5bYxA+NKvCPSN76z5w1mW8NAPaPviq5b1sKyu+1Uh0PjyIG79AFOw7F/zMPmUFpr7srne+y/I6P+7KVL7gkxg+3k1MPXALrD5JHCM+QKxyPPWhET9DjW8+Eho5PVZcZ76alio+VjuIvuKiGz9QKFK+mfMHveL2Fb/osPC9ZwA8Px57Jb7PSJY88KdWvMauuL6SQkI+3dDKvtQyHj4t4Lq+VEYdPTPUZz1emAI9K/qhvp1iwr4lHW09yp0ev6UnAj/SK9w+4tYPPm91A7+nsgM+qYWRPl9Ber5Nb08+/HPmvchN/r2mnFc+jowPPeQESr4w60O+r/fAvWrGFL4omqy+WMa+vrPO0z7SyqQ+MOquO4TbkDzAF0U/grLuPoaSK78AP+o+G8cMvs45SD3sfck9FKuqPviwXz4OGAo/JmW6PdK/Hr40W+i8Bam5PjO/Xj7eUlw8bTWSPjCenD6Wzxq+v/u2PR3Gjb3MSlk+leimvjg2h76ALUQ7sKu1PiY0S751kAe/YdZxPm7+kbzEdZu8+MxtPjuuhL6GViy9mDY5vvDGeD4DNQo983scPwYjGL57GkC+TMOevGIQ372u1oW+p68+PipMsj6F//w+mO8BPpxu2L7Yhry+mqdAvjl3tz3FJvm9vDjDPuYUIr18Ajo+iHv7vdF3Fz93y+q9PHzOPtUqQD41f5Y+/+dMPvAAE79OesY+ze6cvCo7tD6gkA0+o4uNvshxY77jGEE+LjZtPqTjij7+NlO/4So9PqDgUb6uyIw8DvK0PvrPFr4w3/k7Bhxvvnn6mzxuO2e+n+A1vpi2SL5LE+e+QjK3vFhQiT6Ms+G8A6pMvQr9rb6iMPS+PhgqPqbzRT5jKhq+FS2uvTCIbj0MlUU+EnfIPZrEur6gyhS7xFCWvRxyE74olrk+2uMUv1t6gj6rwAU/wQGHPgAAsbpVdX++WPT9O3UI173S+029mN34vdRfTb94VbU+D5qAvoiFpjuxwzo/WPgRvvx3ZL0="
            }
        }
        with patch.object(ModelAPIClient, "predict") as mock_predict:
            f = asyncio.Future()
            f.set_result(model_api_return)
            mock_predict.return_value = f
            response = client.get(
                "/datastores/{}/score".format(datastore_name),
                params={
                    "index_name": "dpr",
                    "query": "quack",
                    "doc_id": query_document["id"],
                },
            )

        assert response.status_code == 200
        assert response.json()["document"] == query_result.document.__root__
        assert response.json()["score"] == -5

    def test_score_not_found(self, client, datastore_name):
        response = client.get(
            "/datastores/{}/score".format(datastore_name),
            params={"query": "quack", "doc_id": "99999"},
        )
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_bing_search_available(self, client, bing_search_datastore_name):
        response = client.get(
            f"/datastores/{bing_search_datastore_name}/search",
            params={"query": "quack", "top_k": 1},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1


    def test_unsupported_operation_for_bing_search(self, client, bing_search_datastore_name):
        response = client.get(
            f"/datastores/{bing_search_datastore_name}/search_by_vector",
        )
        assert response.status_code == 404

        response = client.get(
            f"/datastores/{bing_search_datastore_name}/score",
        )
        assert response.status_code == 404