from api.routes.router import api_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import APP_NAME, APP_VERSION,API_PREFIX



def get_app() -> FastAPI:
    fast_app = FastAPI(title=APP_NAME,
                       version=APP_VERSION,
                    )
    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    fast_app.include_router(api_router, prefix=API_PREFIX)

    return fast_app

app = get_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)