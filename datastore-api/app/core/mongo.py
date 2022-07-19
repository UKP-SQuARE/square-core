import logging
import jwt
from pydantic import ValidationError
import pymongo
from fastapi import Request, HTTPException
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)


class MongoClient:
    """Wraps access to MongoDB for storing additional data, e.g. user-datastore binding."""

    def __init__(self, host: str, port: str, username: str, password: str, timeout: int):
        client_access = {
            'host': [f"{host}:{port}"],
            'username': username,
            'password': password,
            'serverSelectionTimeoutMS': timeout,
        }
        self.client = pymongo.MongoClient(**client_access)
        self.user_datastore_bindings = self.client.user_datastore.bindings
        self.item_keys = {
            'datastore': 'datastore_name', 
            'index': 'index_name'
        }

    def _binding_exists(self, user_id: str, item_value: str, item_type: str):
        assert item_type in self.item_keys
        found = self.user_datastore_bindings.find({
            'user_id': user_id,
            self.item_keys[item_type]: item_value
        })
        return len(list(found.limit(1))) > 0

    async def binding_exists(self, request: Request, item_value: str, item_type: str):
        user_id = await self._decode_user_id(request)
        return self._binding_exists(user_id, item_value, item_type)

    async def new_binding(self, request: Request, item_value: str, item_type: str):
        user_id = await self._decode_user_id(request)
        if self._binding_exists(user_id, item_value, item_type):
            item_key = self.item_keys[item_type]
            error_msg = f'Attempt to override an existing binding (user_id: {user_id}, {item_key}: {item_value})'
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

        self.user_datastore_bindings.insert_one({
            'user_id': user_id,
            self.item_keys[item_type]: item_value
        })
    
    async def delete_binding(self, request: Request, item_value: str, item_type: str):
        user_id = await self._decode_user_id(request)
        assert self._binding_exists(user_id, item_value, item_type), HTTPException(status_code=500, detail="Try deleting an non-existing binding")
        self.user_datastore_bindings.delete_one({
            'user_id': user_id,
            self.item_keys[item_type]: item_value
        })
    
    async def autonomous_access_checking(self, request: Request, item_value: str, item_type: str):
        # TODO: Give admin permission
        if not await self.binding_exists(request, item_value, item_type):
            raise HTTPException(status_code=403, detail='No permission')
    
    async def _decode_user_id(self, request: Request):
        http_bearer = HTTPBearer()
        auth_credentials: HTTPAuthorizationCredentials = await http_bearer(request)
        token = auth_credentials.credentials
        payload = jwt.decode(token, options=dict(verify_signature=False))
        user_id = payload["preferred_username"]
        return user_id