from abc import (
    ABC,
    abstractmethod,
)
from enum import Enum
from json import JSONDecodeError
from logging import getLogger
from typing import Any

from fastapi import (
    HTTPException,
    status,
)
from fastapi.security import HTTPAuthorizationCredentials
from httpx import (
    AsyncClient,
    ConnectError,
    ConnectTimeout,
    HTTPStatusError,
    Limits,
    ReadTimeout,
)
from opentelemetry.propagate import inject

logger = getLogger(__name__)


class MethodRequest(Enum):
    GET = "get"
    POST = "post"
    PATCH = "patch"
    PUT = "put"
    DELETE = "delete"


class BaseHTTPRequester(ABC):
    def __init__(
        self,
        token: HTTPAuthorizationCredentials | None = None,
        *,
        additional_headers: dict | None = None,
    ) -> None:
        self._http_client = self.__get_client(token, additional_headers)

    def __get_client(
        self,
        token: HTTPAuthorizationCredentials | None = None,
        additional_headers: dict | None = None,
    ) -> AsyncClient:
        headers: dict["str", Any] = {}

        # inject trace info
        inject(headers)

        if token:
            headers.update({"Authorization": f"{token.scheme} {token.credentials}"})
        if additional_headers:
            headers.update(additional_headers)
        return AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=30,
            verify=False,
            limits=Limits(
                max_connections=100,
                max_keepalive_connections=20,
                keepalive_expiry=1800,
            ),
        )

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    async def get_all(self, router: str, api_version: int = 1, **kwargs):
        url = f"/v{api_version}/{router}/"
        return await self._send_request(url, **kwargs)

    async def get_by_id(self, item_id: int, router: str, api_version: int = 1, **kwargs):
        url = f"/v{api_version}/{router}/{item_id}/"
        return await self._send_request(url, **kwargs)

    async def patch_by_id(
        self,
        item_id: int,
        router: str,
        api_version: int = 1,
        path: str = None,
        params: dict = None,
        file_upload: dict = None,
    ):
        url = f"/v{api_version}/{router}/{item_id}/{path}/"
        return await self._send_request(
            url=url,
            method=MethodRequest.PATCH,
            params=params,
            files=file_upload,
        )

    async def delete_by_id(
        self,
        item_id: int,
        router: str,
        api_version: int = 1,
    ):
        url = f"/v{api_version}/{router}/{item_id}/"
        return await self._send_request(
            url=url,
            method=MethodRequest.DELETE,
        )

    async def _send_request(
        self,
        url: str,
        *,
        method: MethodRequest = MethodRequest.GET,
        params: dict | None = None,
        files: dict | None = None,
        additional_headers: dict | None = None,
        data: dict[str, Any] | list[dict[str, Any]] | None = None,
        _exception_detail: str | None = None,
    ):
        request_attr: dict[str, Any] = {"url": url, "method": method.value}
        if params:
            request_attr["params"] = params
        if data:
            request_attr["json"] = data
        if files:
            request_attr["files"] = files
        if additional_headers:
            request_attr["headers"] = additional_headers
        try:
            request = self._http_client.build_request(**request_attr)
            response = await self._http_client.send(request)
            response.raise_for_status()
            if response.status_code == status.HTTP_204_NO_CONTENT:
                return
            return response.json()
        except (ConnectError, ConnectTimeout, ReadTimeout):
            logger.error(f"Connection with {self.base_url}{url} is broken")
            detail = "Error when sending a request to another microservices"
            if _exception_detail:
                detail = _exception_detail
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail,
            )
        except HTTPStatusError:
            detail = "Error when sending a request to another microservices"
            if _exception_detail:
                detail = _exception_detail
            elif response.status_code < status.HTTP_500_INTERNAL_SERVER_ERROR and isinstance(
                response.json(),
                dict,
            ):
                detail = response.json().get("detail")

            raise HTTPException(
                status_code=response.status_code,  # type: ignore[union-attr]
                detail=detail,
            )
        except JSONDecodeError as e:
            logger.error(f"{url}", e.args)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="error reading the response",
            )
