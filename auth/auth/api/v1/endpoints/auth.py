from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from auth.api.deps import commit_and_close_session
from dependency_injector.wiring import inject, Provide
from auth.core.containers import Container
from auth.schemas.auth import Token, RegUserIn

router = APIRouter()


@router.post('/login', response_model=Token)
@inject
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service=Depends(Provide[Container.auth_service])
):
    return await auth_service.login(form_data=form_data)


@router.post('/registration')
@inject
@commit_and_close_session
async def registration(
        user: RegUserIn,
        auth_service=Depends(Provide[Container.auth_service])
):
    return await auth_service.registration(user=user)


@router.post('/refresh', response_model=Token)
@inject
async def refresh(
        access_token: Token,
        redis=Depends(Provide[Container.redis]),
        auth_service=Depends(Provide[Container.auth_service])
):
    return await auth_service.refresh_access_token(redis, access_token)
