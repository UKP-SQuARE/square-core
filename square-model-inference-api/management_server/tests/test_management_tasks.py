import unittest
from time import sleep
from unittest.mock import patch, MagicMock
import docker

from tasks.tasks import remove_model_task, remove_worker
client = docker.from_env()

class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


def start_dummy_container():
    container = client.containers.run("enhariharan/infinite-loop", detach=True)
    return [{"CONTAINER": container.id}]


class TestTasks(unittest.TestCase):

    def setUp(self) -> None:
        self.num_containers_before = len(client.containers.list())
        self.container = start_dummy_container()
        self.patcher1 = patch('mongo_access.MongoClass.get_model_container_ids')
        self.MockClass1 = self.patcher1.start()
        self.MockClass1.return_value = self.container

    def tearDown(self):
        self.patcher1.stop()

    @patch('mongo_access.MongoClass.server_info', return_value=True)
    @patch('mongo_access.MongoClass.remove_model_db', return_value=None, new_callable=AsyncMock)
    def test_remove_task(self, check1, check2):
        result = remove_model_task("test_identifier")
        self.assertTrue(check1.called)
        self.assertTrue(check2.called)
        self.assertTrue(result["success"])
        self.assertEqual(len(client.containers.list()), self.num_containers_before)

    @patch('mongo_access.MongoClass.remove_container', return_value=None, new_callable=AsyncMock)
    def test_remove_worker_task(self, check):
        result = remove_worker([c["CONTAINER"] for c in self.container])
        self.assertTrue(result["success"])
        self.assertEqual(len(client.containers.list()), self.num_containers_before)
