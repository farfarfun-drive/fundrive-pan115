"""基于 httpx 的同步/异步 HTTP 请求适配层（替代 urllib3_future_request）。"""

from collections import UserString
from collections.abc import (
    AsyncIterable,
    Awaitable,
    Buffer,
    Callable,
    Coroutine,
    Iterable,
    Iterator,
    Mapping,
)
from http.client import HTTPMessage
from http.cookiejar import CookieJar
from http.cookies import BaseCookie
from inspect import isawaitable
from os import PathLike
from types import EllipsisType
from typing import IO, Any, Literal, cast, overload
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import Request
from warnings import warn

import httpx
from yarl import URL

from fundrives.pan115._http import (
    SupportsGeturl,
    cookie_header_for_url,
    cookies_dict_to_str,
    cookies_str_to_dict,
    extract_cookies,
    normalize_request_args,
    parse_response,
)
from fundrives.pan115._utils import dict_merge
from fundrives.pan115._vendor.filewrap import SupportsRead

__all__ = ["request_sync", "request_async", "request"]

type string = Buffer | str | UserString


class _CookieExtractAdapter:
    """为 http.cookiejar.CookieJar.extract_cookies 提供标准 info() 视图。"""

    def __init__(self, headers: httpx.Headers) -> None:
        self._msg = HTTPMessage()
        for k, v in headers.multi_items():
            self._msg.add_header(k, v)

    def info(self) -> HTTPMessage:
        return self._msg


class _SyncResponse:
    """兼容 urllib3 HTTPResponse 常用属性的同步响应包装器。"""

    def __init__(
        self,
        raw: httpx.Response,
        *,
        session: httpx.Client,
        cookies: CookieJar,
        method: str,
        url: str,
    ) -> None:
        self._raw = raw
        self.session = session
        self.cookies = cookies
        self.method = method
        self.url = url
        self._iter: Iterator[bytes] | None = None
        self._buf = bytearray()

    @property
    def status(self) -> int:
        return self._raw.status_code

    @property
    def status_code(self) -> int:
        return self._raw.status_code

    @property
    def reason(self) -> str:
        return self._raw.reason_phrase

    @property
    def headers(self) -> httpx.Headers:
        return self._raw.headers

    @property
    def closed(self) -> bool:
        return self._raw.is_closed

    @property
    def is_closed(self) -> bool:
        return self._raw.is_closed

    @property
    def data(self) -> bytes:
        content = self._raw.read()
        self._raw.close()
        return content

    def info(self) -> HTTPMessage:
        return _CookieExtractAdapter(self._raw.headers).info()

    def get_redirect_location(self) -> str | Literal[False]:
        if self._raw.is_redirect and "location" in self._raw.headers:
            return self._raw.headers["location"]
        return False

    def read(self, amt: int | None = None) -> bytes:
        if amt is None or amt < 0:
            if self._iter is None:
                self._iter = self._raw.iter_bytes()
            for chunk in self._iter:
                self._buf.extend(chunk)
            out = bytes(self._buf)
            self._buf.clear()
            return out
        if amt == 0:
            return b""
        if self._iter is None:
            self._iter = self._raw.iter_bytes()
        while len(self._buf) < amt:
            try:
                self._buf.extend(next(self._iter))
            except StopIteration:
                break
        out = bytes(self._buf[:amt])
        del self._buf[:amt]
        return out

    def readline(self, limit: int = -1) -> bytes:
        if self._iter is None:
            self._iter = self._raw.iter_bytes()
        while True:
            idx = self._buf.find(b"\n")
            if idx != -1:
                end = idx + 1 if limit < 0 else min(idx + 1, limit)
                out = bytes(self._buf[:end])
                del self._buf[:end]
                return out
            if 0 <= limit <= len(self._buf):
                out = bytes(self._buf[:limit])
                del self._buf[:limit]
                return out
            try:
                self._buf.extend(next(self._iter))
            except StopIteration:
                out = bytes(self._buf)
                self._buf.clear()
                return out

    def stream(self, amt: int = 65536) -> Iterator[bytes]:
        yield from self._raw.iter_bytes(chunk_size=amt)

    def drain_conn(self) -> None:
        self._raw.close()

    def close(self) -> None:
        self._raw.close()

    def __enter__(self) -> "_SyncResponse":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __iter__(self) -> Iterator[bytes]:
        return self._raw.iter_bytes()


class _AsyncResponse:
    """兼容 urllib3 AsyncHTTPResponse 常用属性的异步响应包装器。"""

    def __init__(
        self,
        raw: httpx.Response,
        *,
        session: httpx.AsyncClient,
        cookies: CookieJar,
        method: str,
        url: str,
    ) -> None:
        self._raw = raw
        self.session = session
        self.cookies = cookies
        self.method = method
        self.url = url
        self._aiter: Any = None
        self._buf = bytearray()

    @property
    def status(self) -> int:
        return self._raw.status_code

    @property
    def status_code(self) -> int:
        return self._raw.status_code

    @property
    def reason(self) -> str:
        return self._raw.reason_phrase

    @property
    def headers(self) -> httpx.Headers:
        return self._raw.headers

    @property
    def closed(self) -> bool:
        return self._raw.is_closed

    @property
    def is_closed(self) -> bool:
        return self._raw.is_closed

    @property
    async def data(self) -> bytes:
        content = await self._raw.aread()
        await self._raw.aclose()
        return content

    def info(self) -> HTTPMessage:
        return _CookieExtractAdapter(self._raw.headers).info()

    def get_redirect_location(self) -> str | Literal[False]:
        if self._raw.is_redirect and "location" in self._raw.headers:
            return self._raw.headers["location"]
        return False

    async def read(self, amt: int | None = None) -> bytes:
        if amt is None or amt < 0:
            if self._aiter is None:
                self._aiter = self._raw.aiter_bytes()
            async for chunk in self._aiter:
                self._buf.extend(chunk)
            out = bytes(self._buf)
            self._buf.clear()
            return out
        if amt == 0:
            return b""
        if self._aiter is None:
            self._aiter = self._raw.aiter_bytes()
        while len(self._buf) < amt:
            try:
                self._buf.extend(await anext(self._aiter))
            except StopAsyncIteration:
                break
        out = bytes(self._buf[:amt])
        del self._buf[:amt]
        return out

    async def drain_conn(self) -> None:
        await self._raw.aclose()

    async def close(self) -> None:
        await self._raw.aclose()

    async def __aenter__(self) -> "_AsyncResponse":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def __aiter__(self):
        return self._raw.aiter_bytes()


_DEFAULT_LIMITS = httpx.Limits(max_connections=256, max_keepalive_connections=64)
_DEFAULT_POOL: httpx.Client | None = None
_DEFAULT_ASYNC_POOL: httpx.AsyncClient | None = None
_DEFAULT_COOKIES = CookieJar()


def _get_default_pool() -> httpx.Client:
    global _DEFAULT_POOL
    if _DEFAULT_POOL is None or _DEFAULT_POOL.is_closed:
        _DEFAULT_POOL = httpx.Client(limits=_DEFAULT_LIMITS, follow_redirects=False)
        _DEFAULT_POOL.cookies = _DEFAULT_COOKIES
    return _DEFAULT_POOL


def _get_default_async_pool() -> httpx.AsyncClient:
    global _DEFAULT_ASYNC_POOL
    if _DEFAULT_ASYNC_POOL is None or _DEFAULT_ASYNC_POOL.is_closed:
        _DEFAULT_ASYNC_POOL = httpx.AsyncClient(
            limits=_DEFAULT_LIMITS, follow_redirects=False
        )
        _DEFAULT_ASYNC_POOL.cookies = _DEFAULT_COOKIES
    return _DEFAULT_ASYNC_POOL


def _extract_httpx_kwargs(request_kwargs: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if "timeout" in request_kwargs:
        out["timeout"] = request_kwargs["timeout"]
    return out


def _prepare_sync_body(body: Any) -> Any:
    if body is None:
        return None
    if isinstance(body, (bytes, bytearray, memoryview)):
        return bytes(body)
    if isinstance(body, str):
        return body.encode("utf-8")
    if isinstance(body, SupportsRead):

        def _gen() -> Iterator[bytes]:
            while chunk := body.read(65536):
                yield bytes(chunk) if not isinstance(chunk, bytes) else chunk

        return _gen()
    return body


def _prepare_async_body(body: Any) -> Any:
    if body is None:
        return None
    if isinstance(body, (bytes, bytearray, memoryview)):
        return bytes(body)
    if isinstance(body, str):
        return body.encode("utf-8")
    if isinstance(body, AsyncIterable):
        return body
    if isinstance(body, SupportsRead):

        async def _agen():
            while True:
                chunk = body.read(65536)
                if isawaitable(chunk):
                    chunk = await chunk
                if not chunk:
                    break
                yield bytes(chunk) if not isinstance(chunk, bytes) else chunk

        return _agen()
    if isinstance(body, Iterable):

        async def _agen_iter():
            for chunk in body:
                yield bytes(chunk) if not isinstance(chunk, bytes) else chunk

        return _agen_iter()
    return body


def _prepare_request(
    url: string | SupportsGeturl | URL | Request,
    method: string,
    params: None | string | Mapping | Iterable[tuple[Any, Any]],
    data: Any,
    json: Any,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]],
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]],
) -> tuple[str, str, dict[str, str], Any, Any]:
    opened_file = None
    if isinstance(url, Request):
        req = url
        method_str = req.method or "GET"
        url_str = req.full_url
        body = req.data
        if isinstance(body, PathLike):
            opened_file = open(body, "rb")
            body = opened_file
        headers_ = {k.lower(): v for k, v in req.headers.items()}
    else:
        if isinstance(data, PathLike):
            opened_file = open(data, "rb")
            data = opened_file
        if isinstance(data, SupportsRead):
            request_args = normalize_request_args(
                method=method,
                url=url,
                params=params,
                headers=headers,
            )
            body = data
        else:
            request_args = normalize_request_args(
                method=method,
                url=url,
                params=params,
                data=data,
                files=files,
                json=json,
                headers=headers,
            )
            body = request_args["data"]
        method_str = request_args["method"]
        url_str = request_args["url"]
        headers_ = request_args["headers"]
        headers_.setdefault("connection", "keep-alive")
    return method_str, url_str, headers_, body, opened_file


@overload
def request_sync(
    url: string | SupportsGeturl | URL | Request,
    method: string = "GET",
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None,
    data: Any = None,
    json: Any = None,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None,
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None,
    follow_redirects: bool = True,
    raise_for_status: bool = True,
    stream: bool = True,
    cookies: None | CookieJar | BaseCookie = None,
    session: None | httpx.Client = None,
    *,
    parse: None | EllipsisType = None,
    **request_kwargs,
) -> _SyncResponse: ...
@overload
def request_sync(
    url: string | SupportsGeturl | URL | Request,
    method: string = "GET",
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None,
    data: Any = None,
    json: Any = None,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None,
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None,
    follow_redirects: bool = True,
    raise_for_status: bool = True,
    stream: bool = True,
    cookies: None | CookieJar | BaseCookie = None,
    session: None | httpx.Client = None,
    *,
    parse: Literal[False],
    **request_kwargs,
) -> bytes: ...
@overload
def request_sync(
    url: string | SupportsGeturl | URL | Request,
    method: string = "GET",
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None,
    data: Any = None,
    json: Any = None,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None,
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None,
    follow_redirects: bool = True,
    raise_for_status: bool = True,
    stream: bool = True,
    cookies: None | CookieJar | BaseCookie = None,
    session: None | httpx.Client = None,
    *,
    parse: Literal[True],
    **request_kwargs,
) -> bytes | str | dict | list | int | float | bool | None: ...
@overload
def request_sync[T](
    url: string | SupportsGeturl | URL | Request,
    method: string = "GET",
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None,
    data: Any = None,
    json: Any = None,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None,
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None,
    follow_redirects: bool = True,
    raise_for_status: bool = True,
    stream: bool = True,
    cookies: None | CookieJar | BaseCookie = None,
    session: None | httpx.Client = None,
    *,
    parse: Callable[[_SyncResponse, bytes], T],
    **request_kwargs,
) -> T: ...
def request_sync[T](
    url: string | SupportsGeturl | URL | Request,
    method: string = "GET",
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None,
    data: Any = None,
    json: Any = None,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None,
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None,
    follow_redirects: bool = True,
    raise_for_status: bool = True,
    stream: bool = True,
    cookies: None | CookieJar | BaseCookie = None,
    session: None | httpx.Client = None,
    *,
    parse: None | EllipsisType | bool | Callable[[_SyncResponse, bytes], T] = None,
    **request_kwargs,
) -> _SyncResponse | bytes | str | dict | list | int | float | bool | None | T:
    client = session if session is not None else _get_default_pool()
    method_str, url_str, headers_, body, opened_file = _prepare_request(
        url, method, params, data, json, files, headers
    )
    if cookies is None:
        cookies = getattr(client, "cookies", None)
    if isinstance(cookies, httpx.Cookies):
        cookies = cookies.jar
    cookies_dict = cookie_header_for_url(cookies, url_str) if cookies else {}
    if "cookie" in headers_:
        cookies_dict.update(cookies_str_to_dict(headers_["cookie"]))
    response_cookies = CookieJar()
    extra = _extract_httpx_kwargs(request_kwargs)
    try:
        while True:
            if response_cookies:
                cookies_dict.update(cookie_header_for_url(response_cookies, url_str))
            if cookies_dict:
                headers_["cookie"] = cookies_dict_to_str(cookies_dict)
            req = client.build_request(
                method=method_str,
                url=url_str,
                headers=headers_,
                content=_prepare_sync_body(body),
                **extra,
            )
            raw = client.send(req, stream=stream)
            response = _SyncResponse(
                raw,
                session=client,
                cookies=response_cookies,
                method=method_str,
                url=url_str,
            )
            adapter = _CookieExtractAdapter(raw.headers)
            if cookies is not None:
                extract_cookies(cookies, url_str, adapter)
            extract_cookies(response_cookies, url_str, adapter)
            status_code = response.status
            if redirect_location := (
                follow_redirects and response.get_redirect_location()
            ):
                dict_merge(
                    cookies_dict,
                    ((c.name, c.value) for c in response_cookies),
                )
                if cookies_dict:
                    headers_["cookie"] = cookies_dict_to_str(cookies_dict)
                url_str = urljoin(url_str, redirect_location)
                if body and status_code in (307, 308):
                    if isinstance(body, SupportsRead):
                        try:
                            body.seek(0)  # type: ignore
                        except Exception:
                            warn(f"unseekable-stream: {body!r}", stacklevel=2)
                    elif not isinstance(body, Buffer):
                        warn(
                            f"failed to resend request body: {body!r}, when {status_code} redirects",
                            stacklevel=2,
                        )
                else:
                    if status_code == 303:
                        method_str = "GET"
                    body = None
                response.drain_conn()
                continue
            if raise_for_status and status_code >= 400:
                _ = response.data
                raise HTTPError(
                    url_str,
                    status_code,
                    response.reason or "",
                    response.headers,  # type: ignore
                    cast(IO[bytes], response),
                )
            if parse is None:
                if method_str == "HEAD":
                    response.drain_conn()
                return response
            if parse is ...:
                response.close()
                return response
            content = response.data
            if isinstance(parse, bool):
                if not parse:
                    return content
                parse = cast(Callable, parse_response)
            return parse(response, content)
    finally:
        if opened_file is not None:
            opened_file.close()


@overload
async def request_async(
    url: string | SupportsGeturl | URL | Request,
    method: string = "GET",
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None,
    data: Any = None,
    json: Any = None,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None,
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None,
    follow_redirects: bool = True,
    raise_for_status: bool = True,
    stream: bool = True,
    cookies: None | CookieJar | BaseCookie = None,
    session: None | httpx.AsyncClient = None,
    *,
    parse: None | EllipsisType = None,
    **request_kwargs,
) -> _AsyncResponse: ...
@overload
async def request_async(
    url: string | SupportsGeturl | URL | Request,
    method: string = "GET",
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None,
    data: Any = None,
    json: Any = None,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None,
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None,
    follow_redirects: bool = True,
    raise_for_status: bool = True,
    stream: bool = True,
    cookies: None | CookieJar | BaseCookie = None,
    session: None | httpx.AsyncClient = None,
    *,
    parse: Literal[False],
    **request_kwargs,
) -> bytes: ...
@overload
async def request_async(
    url: string | SupportsGeturl | URL | Request,
    method: string = "GET",
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None,
    data: Any = None,
    json: Any = None,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None,
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None,
    follow_redirects: bool = True,
    raise_for_status: bool = True,
    stream: bool = True,
    cookies: None | CookieJar | BaseCookie = None,
    session: None | httpx.AsyncClient = None,
    *,
    parse: Literal[True],
    **request_kwargs,
) -> bytes | str | dict | list | int | float | bool | None: ...
@overload
async def request_async[T](
    url: string | SupportsGeturl | URL | Request,
    method: string = "GET",
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None,
    data: Any = None,
    json: Any = None,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None,
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None,
    follow_redirects: bool = True,
    raise_for_status: bool = True,
    stream: bool = True,
    cookies: None | CookieJar | BaseCookie = None,
    session: None | httpx.AsyncClient = None,
    *,
    parse: Callable[[_AsyncResponse, bytes], T]
    | Callable[[_AsyncResponse, bytes], Awaitable[T]],
    **request_kwargs,
) -> T: ...
async def request_async[T](
    url: string | SupportsGeturl | URL | Request,
    method: string = "GET",
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None,
    data: Any = None,
    json: Any = None,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None,
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None,
    follow_redirects: bool = True,
    raise_for_status: bool = True,
    stream: bool = True,
    cookies: None | CookieJar | BaseCookie = None,
    session: None | httpx.AsyncClient = None,
    *,
    parse: None
    | EllipsisType
    | bool
    | Callable[[_AsyncResponse, bytes], T]
    | Callable[[_AsyncResponse, bytes], Awaitable[T]] = None,
    **request_kwargs,
) -> _AsyncResponse | bytes | str | dict | list | int | float | bool | None | T:
    client = session if session is not None else _get_default_async_pool()
    method_str, url_str, headers_, body, opened_file = _prepare_request(
        url, method, params, data, json, files, headers
    )
    if cookies is None:
        cookies = getattr(client, "cookies", None)
    if isinstance(cookies, httpx.Cookies):
        cookies = cookies.jar
    cookies_dict = cookie_header_for_url(cookies, url_str) if cookies else {}
    if "cookie" in headers_:
        cookies_dict.update(cookies_str_to_dict(headers_["cookie"]))
    response_cookies = CookieJar()
    extra = _extract_httpx_kwargs(request_kwargs)
    try:
        while True:
            if response_cookies:
                cookies_dict.update(cookie_header_for_url(response_cookies, url_str))
            if cookies_dict:
                headers_["cookie"] = cookies_dict_to_str(cookies_dict)
            req = client.build_request(
                method=method_str,
                url=url_str,
                headers=headers_,
                content=_prepare_async_body(body),
                **extra,
            )
            raw = await client.send(req, stream=stream)
            response = _AsyncResponse(
                raw,
                session=client,
                cookies=response_cookies,
                method=method_str,
                url=url_str,
            )
            adapter = _CookieExtractAdapter(raw.headers)
            if cookies is not None:
                extract_cookies(cookies, url_str, adapter)
            extract_cookies(response_cookies, url_str, adapter)
            status_code = response.status
            if redirect_location := (
                follow_redirects and response.get_redirect_location()
            ):
                dict_merge(
                    cookies_dict,
                    ((c.name, c.value) for c in response_cookies),
                )
                if cookies_dict:
                    headers_["cookie"] = cookies_dict_to_str(cookies_dict)
                url_str = urljoin(url_str, redirect_location)
                if body and status_code in (307, 308):
                    if isinstance(body, SupportsRead):
                        try:
                            from fundrives.pan115._vendor.asynctools import ensure_async

                            await ensure_async(body.seek)(0)  # type: ignore
                        except Exception:
                            warn(f"unseekable-stream: {body!r}", stacklevel=2)
                    elif not isinstance(body, Buffer):
                        warn(
                            f"failed to resend request body: {body!r}, when {status_code} redirects",
                            stacklevel=2,
                        )
                else:
                    if status_code == 303:
                        method_str = "GET"
                    body = None
                await response.drain_conn()
                continue
            if raise_for_status and status_code >= 400:
                _ = await response.data
                raise HTTPError(
                    url_str,
                    status_code,
                    response.reason or "",
                    response.headers,  # type: ignore
                    cast(IO[bytes], response),
                )
            if parse is None:
                if method_str == "HEAD":
                    await response.drain_conn()
                return response
            if parse is ...:
                await response.close()
                return response
            content = await response.data
            if isinstance(parse, bool):
                if not parse:
                    return content
                parse = cast(Callable, parse_response)
            ret = parse(response, content)
            if isawaitable(ret):
                ret = await ret
            return ret
    finally:
        if opened_file is not None:
            opened_file.close()


@overload
def request[T](
    url: string | SupportsGeturl | URL | Request,
    method: string = "GET",
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None,
    data: Any = None,
    json: Any = None,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None,
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None,
    follow_redirects: bool = True,
    raise_for_status: bool = True,
    stream: bool = True,
    cookies: None | CookieJar | BaseCookie = None,
    *,
    parse: None | EllipsisType | bool | Callable[[_SyncResponse, bytes], T] = None,
    async_: Literal[False] = False,
    **request_kwargs,
) -> _SyncResponse | bytes | str | dict | list | int | float | bool | None | T: ...
@overload
def request[T](
    url: string | SupportsGeturl | URL | Request,
    method: string = "GET",
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None,
    data: Any = None,
    json: Any = None,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None,
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None,
    follow_redirects: bool = True,
    raise_for_status: bool = True,
    stream: bool = True,
    cookies: None | CookieJar | BaseCookie = None,
    *,
    parse: None
    | EllipsisType
    | bool
    | Callable[[_AsyncResponse, bytes], T]
    | Callable[[_AsyncResponse, bytes], Awaitable[T]] = None,
    async_: Literal[True],
    **request_kwargs,
) -> Coroutine[
    Any,
    Any,
    _AsyncResponse | bytes | str | dict | list | int | float | bool | None | T,
]: ...
def request[T](
    url: string | SupportsGeturl | URL | Request,
    method: string = "GET",
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None,
    data: Any = None,
    json: Any = None,
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None,
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None,
    follow_redirects: bool = True,
    raise_for_status: bool = True,
    stream: bool = True,
    cookies: None | CookieJar | BaseCookie = None,
    *,
    parse: None
    | EllipsisType
    | bool
    | Callable[[_SyncResponse, bytes], T]
    | Callable[[_AsyncResponse, bytes], T]
    | Callable[[_AsyncResponse, bytes], Awaitable[T]] = None,
    async_: Literal[False, True] = False,
    **request_kwargs,
) -> (
    _SyncResponse
    | bytes
    | str
    | dict
    | list
    | int
    | float
    | bool
    | None
    | T
    | Coroutine[
        Any,
        Any,
        _AsyncResponse | bytes | str | dict | list | int | float | bool | None | T,
    ]
):
    if async_:
        return request_async(  # type: ignore
            url=url,
            method=method,
            params=params,
            data=data,
            json=json,
            files=files,
            headers=headers,
            follow_redirects=follow_redirects,
            raise_for_status=raise_for_status,
            stream=stream,
            cookies=cookies,
            parse=parse,  # type: ignore
            **request_kwargs,
        )
    return request_sync(  # type: ignore
        url=url,
        method=method,
        params=params,
        data=data,
        json=json,
        files=files,
        headers=headers,
        follow_redirects=follow_redirects,
        raise_for_status=raise_for_status,
        stream=stream,
        cookies=cookies,
        parse=parse,  # type: ignore
        **request_kwargs,
    )
