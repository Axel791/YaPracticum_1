from auth.api.v1 import api
from auth.api import deps
from auth.api.v1.endpoints import auth

from auth.core.config import settings
from auth.core.containers import Container

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


def create_app():
    container = Container()
    container.wire(modules=[deps, auth, ])

    fastapi_app = FastAPI(
        root_path='/auth',
        title=settings.PROJECT_SLUG,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )
    fastapi_app.container = container

    fastapi_app.include_router(api.api_router, prefix=settings.API_V1_STR)

    return fastapi_app


app = create_app()
