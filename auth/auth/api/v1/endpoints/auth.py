import sys
from typing import Annotated

from authlib.integrations.starlette_client import OAuth
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from loguru import logger
from starlette.requests import Request

from auth.api.deps import commit_and_close_session
from auth.core.commons import PaginateQueryParams
from auth.core.config import settings
from auth.core.containers import Container
from auth.schemas.login_event import LoginEvent
from auth.schemas.token import Token
from auth.schemas.user import RegUserIn
from auth.utils.check_jwt_token import CheckToken
from auth.utils.jwt_bearer import security_jwt

logger.add(
    "/var/log/auth/access-log.json",
    rotation="500 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

oauth = OAuth()

providers = {
    "google": {
        "client_id": settings.oauth_google_cid,
        "client_secret": settings.oauth_google_secret,
        "server_metadata_url": settings.oauth_google_discovery_url,
    }
    # Здесь можно добавить других провайдеров
}

for provider_name, provider_config in providers.items():
    oauth.register(
        name=provider_name,
        client_id=provider_config["client_id"],
        client_secret=provider_config["client_secret"],
        server_metadata_url=provider_config["server_metadata_url"],
        client_kwargs={"scope": "openid email profile"},
    )

router = APIRouter()


def get_x_request_id(request: Request):
    return request.headers.get("X-Request-Id", "N/A")


@router.get("/login/{provider}")
async def login_oauth(request: Request, provider: str):
    redirect_uri = settings.oauth_redirect_uri
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info(
        "Received login request for provider: %s", provider
    )
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)


@router.post("/login", response_model=Token)
@inject
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service=Depends(Provide[Container.auth_service]),
):
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info(
        "Received login request for user: %s", form_data.username
    )
    logger.info("Received login request for user: %s", form_data.username)
    return await auth_service.login(form_data=form_data, x_request_id=x_request_id)


@router.get("/login/callback/{provider}")
async def login_callback(
    request: Request,
    provider: str,
    auth_service=Depends(Provide[Container.auth_service]),
):
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info(
        "Received login callback request for provider: %s", provider
    )

    token = await oauth.create_client(provider).authorize_access_token(request)
    user = await oauth.create_client(provider).parse_id_token(request, token)
    access_token = auth_service.create_access_token(
        user.login, x_request_id=x_request_id
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/registration")
@inject
@commit_and_close_session
async def registration(
    request: Request,
    user: RegUserIn,
    auth_service=Depends(Provide[Container.auth_service]),
):
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info(
        "Received registration request for user: %s", user.login
    )

    return await auth_service.registration(user=user, x_request_id=x_request_id)


@router.post("/refresh", response_model=Token)
@inject
async def refresh(
    request: Request,
    access_token: Token,
    redis=Depends(Provide[Container.redis]),
    auth_service=Depends(Provide[Container.auth_service]),
):
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("Received refresh token request")

    return await auth_service.refresh_access_token(
        redis, access_token, x_request_id=x_request_id
    )


@router.get("/check_authorisation", response_model=CheckToken)
@inject
async def check_authorisation(
    request: Request,
    auth_service=Depends(Provide[Container.auth_service]),
    auth_data: str = Depends(security_jwt),
) -> CheckToken:
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("Received check authorization request")
    return await auth_service.check_authorisation(token=auth_data)


@router.post("/get_login_history", response_model=LoginEvent)
@inject
async def get_login_history(
    request: Request,
    commons: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
    user_login: str,
    auth_service=Depends(Provide[Container.auth_service]),
):
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info(
        "Received request to get login history for user: %s", user_login
    )

    return await auth_service.get_login_history(
        user_login, page=commons.page, page_size=commons.page_size
    )
