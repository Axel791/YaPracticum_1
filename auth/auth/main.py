from aioredis import Redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from auth.api import deps
from auth.api.v1 import api
from auth.api.v1.endpoints import auth
from auth.core.config import settings
from auth.core.containers import Container
from auth.db import init_redis
from auth.middlewares.request_id_middleware import (RateLimitMiddleware,
                                                    RequestIdMiddleware)
from auth.utils.jaeger_tracer import configure_jaeger_tracer

if settings.enable_tracer:
    configure_jaeger_tracer()

import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

sentry_sdk.init(dsn=settings.sentry_dsn, integrations=[SentryAsgiMiddleware])


def create_app():
    container = Container()
    container.wire(
        modules=[
            deps,
            auth,
        ]
    )

    fastapi_app = FastAPI(
        root_path="/auth",
        title=settings.PROJECT_SLUG,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )
    fastapi_app.add_middleware(
        CORSMiddleware,
        SentryAsgiMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )
    fastapi_app.add_middleware(RequestIdMiddleware)
    fastapi_app.add_middleware(RateLimitMiddleware)

    fastapi_app.container = container

    fastapi_app.include_router(api.api_router, prefix=settings.API_V1_STR)

    return fastapi_app


app = create_app()

FastAPIInstrumentor.instrument_app(app)


@app.on_event("startup")
async def startup():
    init_redis.redis_for_rate_limiter = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB_FOR_RATE_LIMITER,
        decode_responses=True,
    )
