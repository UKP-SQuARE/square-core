from fastapi import FastAPI

import checklist_api

app = FastAPI()

app.include_router(checklist_api.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)  # for dev purposes