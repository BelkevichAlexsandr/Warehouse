import secrets
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, HTTPBasicCredentials, HTTPBasic
from httpx import AsyncClient, ConnectError, ConnectTimeout
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.utils.engine import Engine

token_auth_scheme = HTTPBearer()

security = HTTPBasic()


async def get_db() -> AsyncGenerator:
    db = AsyncSession(
        bind=Engine().get_engine(),
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    try:
        yield db
    finally:
        await db.close()


@asynccontextmanager
async def async_context_get_db() -> AsyncGenerator:
    db = AsyncSession(
        bind=Engine().get_engine(),
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    try:
        yield db
    finally:
        await db.close()


async def auth_secure(
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
) -> HTTPAuthorizationCredentials:
    if token:
        auth_service_data = {
            "endpoint_method": request.method.upper(),
            "endpoint_route": request.url.path.replace(
                settings.MS_ROUTE_MAP_ROOT_PATH,
                "",  # type: ignore[attr-defined]
            ),
        }
        headers = {"Authorization": f"{token.scheme} {token.credentials}"}
        async with AsyncClient(verify=False) as client:
            try:
                to_auth_service_response = await client.post(
                    f"{settings.MS_AUTH_DOMAIN}/v1/auth/endpoint_access/",  # type: ignore[attr-defined]
                    headers=headers,
                    json=auth_service_data,
                    timeout=3,
                )
            except (ConnectTimeout, ConnectError):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Connection error: auth-ms is unreachable",
                )
            if to_auth_service_response.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=to_auth_service_response.status_code,
                    detail=to_auth_service_response.json().get("detail"),
                )
        return token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Bearer token must be provided",
    )


async def auth_secure_user_data(
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
) -> dict[str, Any | HTTPAuthorizationCredentials]:
    if token:
        auth_service_data = {
            "endpoint_method": request.method.upper(),
            "endpoint_route": request.url.path.replace(
                settings.MS_ROUTE_MAP_ROOT_PATH,
                "",  # type: ignore[attr-defined]
            ),
        }
        if request.path_params:
            auth_service_data["path_params"] = request.path_params  # type: ignore[assignment]
        headers = {"Authorization": f"{token.scheme} {token.credentials}"}
        async with AsyncClient(verify=False) as client:
            try:
                to_auth_service_response = await client.post(
                    f"{settings.MS_AUTH_DOMAIN}/v1/auth/endpoint_access/",  # type: ignore[attr-defined]
                    headers=headers,
                    json=auth_service_data,
                    timeout=3,
                )
            except (ConnectTimeout, ConnectError):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Connection error: auth-ms is unreachable",
                )
            if to_auth_service_response.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=to_auth_service_response.status_code,
                    detail=to_auth_service_response.json().get("detail"),
                )
            employee_data = to_auth_service_response.json()
            employee_data["token"] = token
        return employee_data
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Bearer token must be provided",
    )


def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = bytes(settings.MS_WAREHOUSE_USER_NAME.encode("utf8"))
    is_correct_username = secrets.compare_digest(current_username_bytes, correct_username_bytes)
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = bytes(settings.MS_WAREHOUSE_USER_PASSWORD.encode("utf8"))
    is_correct_password = secrets.compare_digest(current_password_bytes, correct_password_bytes)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
