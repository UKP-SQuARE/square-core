import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from skill_manager import mongo_client
from skill_manager.routers.api import router

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router)


@app.on_event("startup")
def on_startup():
    mongo_client.connect()

@app.on_event("shutdown")
def on_startup():
    mongo_client.close()
