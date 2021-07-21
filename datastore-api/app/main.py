from fastapi import FastAPI
from .routers import datastores, documents, query, indices


app = FastAPI(title="SQuARE Datastore API")

app.include_router(datastores.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(indices.router)
