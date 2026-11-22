"""HTTP Cookie 管理与响应解析工具（替代 _vendor/cookietools.py 和 _vendor/http_response.py）。"""

from __future__ import annotations

from calendar import timegm
from codecs import lookup as codecs_lookup
from collections import UserString
from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Buffer,
    Callable,
    Container,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
)
from copy import copy
from datetime import datetime
from decimal import Decimal
from fractions import Fraction
from gzip import decompress as _decompress_gzip
from http.client import HTTPMessage
from http.cookiejar import Cookie, CookieJar
from http.cookies import BaseCookie, Morsel
from io import TextIOWrapper
from mimetypes import guess_extension, guess_type
from numbers import Integral, Real
from os import PathLike
from os.path import basename as os_basename
from posixpath import basename as posix_basename
from posixpath import commonpath
from re import IGNORECASE
from re import compile as re_compile
from string import punctuation
from time import gmtime, strftime, strptime, time
from typing import Any, Final, Protocol, TypedDict, cast, runtime_checkable
from urllib.parse import parse_qsl, quote, unquote, urlparse, urlsplit, urlunparse
from urllib.request import Request
from uuid import uuid4
from zlib import MAX_WBITS
from zlib import decompress as _zlib_decompress

from orjson import dumps as json_dumps
from orjson import loads as json_loads
from yarl import URL

from fundrives.pan115._utils import (
    dict_map,
    ensure_buffer,
    ensure_str,
    get,
    iter_items,
)
from fundrives.pan115._utils import (
    ensure_bytes as _ensure_bytes,
)
from fundrives.pan115._vendor.asynctools import async_map
from fundrives.pan115._vendor.filewrap import (
    SupportsRead,
    bio_chunk_async_iter,
    bio_chunk_iter,
)

__all__ = [
    "RequestArgs",
    "SupportsGeturl",
    "complete_url",
    "cookie_header_for_url",
    "cookies_dict_to_str",
    "cookies_str_to_dict",
    "cookies_to_dict",
    "cookies_to_str",
    "decompress_response",
    "extract_cookies",
    "get_charset",
    "get_content_length",
    "get_filename",
    "get_length",
    "get_mimetype",
    "get_range",
    "get_status_code",
    "get_total_length",
    "headers_get",
    "is_chunked",
    "is_range_request",
    "is_timeouterror",
    "normalize_request_args",
    "parse_response",
    "update_cookies",
]

Mapping.register(HTTPMessage)

_CRE_COOKIE_SEP_split: Final = re_compile(r";\s*").split
_CRE_CONTENT_RANGE_fullmatch: Final = re_compile(
    r"bytes\s+(?:\*|(?P<begin>[0-9]+)-(?P<end>[0-9]+))/(?:(?P<size>[0-9]+)|\*)"
).fullmatch
_CRE_HDR_CD_FNAME_search: Final = re_compile(
    "(?<=filename=\")[^\"]+|(?<=filename=')[^']+|(?<=filename=)[^'\"][^;]*"
).search
_CRE_HDR_CD_FNAME_STAR_search: Final = re_compile(
    r"(?<=filename\*=)(?P<charset>[^']*)''(?P<name>[^;]+)"
).search
_CRE_CHARSET_search: Final = re_compile(
    r"\bcharset\s*=(?P<charset>[^ ;]+)", IGNORECASE
).search


# ---------------------------------------------------------------------------
# Cookie 转换与存取（替代 _vendor/cookietools.py）
# ---------------------------------------------------------------------------


def _cookie_match_domain(url_domain: str, cookie_domain: str | None = None) -> bool:
    if not cookie_domain:
        return True
    dom = cookie_domain.lstrip(".")
    return url_domain == dom or url_domain.endswith("." + dom)


def _cookie_match_path(url_path: str, cookie_path: str | None = None) -> bool:
    if not cookie_path:
        return True
    cp = cookie_path.rstrip("/")
    return url_path == cp or url_path.startswith(cp + "/")


def _parse_expires(expires: Any) -> float | None:
    if isinstance(expires, datetime):
        return expires.timestamp()
    if isinstance(expires, (int, float)):
        return float(expires)
    if isinstance(expires, str) and expires:
        fmt = (
            "%a, %d-%b-%y %H:%M:%S GMT"
            if len(expires) < 29
            else "%a, %d-%b-%Y %H:%M:%S GMT"
        )
        try:
            return float(timegm(strptime(expires, fmt)))
        except ValueError:
            return None
    return None


def _create_cookie(name: str, value: Any, **kwargs: Any) -> Cookie:
    if isinstance(value, str):
        pass
    elif isinstance(value, Cookie):
        if not kwargs:
            ck = copy(value)
            if name:
                ck.name = name
            return ck
        kwargs = {**value.__dict__, **kwargs}
        kwargs.setdefault("rest", kwargs.pop("_rest", {"HttpOnly": None}))
        value = value.value or ""
    elif isinstance(value, Morsel):
        kwargs = {
            **value,
            "rest": {
                "HttpOnly": value.get("httponly"),
                "SameSite": value.get("samesite"),
                "Max-Age": value.get("max-age"),
            },
            **kwargs,
        }
        value = value.value
    else:
        kwargs = {**value, **kwargs}
        value = kwargs.get("value", "")

    name = name or cast(str, kwargs["name"])
    if not name:
        raise ValueError(f"please provide a name for value {value!r}")

    if exp := kwargs.get("expires"):
        parsed = _parse_expires(exp)
        if parsed is not None:
            kwargs["expires"] = int(parsed)
    elif max_age := str(kwargs.get("max-age") or "").strip(" ,"):
        try:
            age = int(max_age)
        except ValueError as err:
            raise TypeError(f"max-age: {max_age!r} must be integer") from err
        if age >= 0:
            kwargs["expires"] = int(time()) + age

    result: dict[str, Any] = {
        "version": 0,
        "name": name,
        "value": value,
        "port": None,
        "domain": "",
        "path": "/",
        "secure": False,
        "expires": None,
        "discard": True,
        "comment": None,
        "comment_url": None,
        "rest": {"HttpOnly": None},
        "rfc2109": False,
    }
    result.update((k, v) for k, v in kwargs.items() if k in result and v)
    result["port_specified"] = bool(result["port"])
    result["domain_specified"] = bool(result["domain"])
    result["domain_initial_dot"] = result["domain"].startswith(".")
    result["path_specified"] = bool(result["path"])
    return Cookie(**result)


def _create_morsel(name: str, value: Any, **kwargs: Any) -> Morsel[Any]:
    morsel: Morsel[Any]
    if isinstance(value, str):
        morsel = Morsel()
        morsel.set(name, value, value)
    elif isinstance(value, Morsel):
        morsel = copy(value)
        if name:
            morsel._key = name  # type: ignore[attr-defined]
        if not kwargs:
            return morsel
    else:
        if isinstance(value, Cookie):
            kwargs = {**value.__dict__, **kwargs}
            kwargs.setdefault("rest", kwargs.pop("_rest", {"HttpOnly": None}))
        else:
            kwargs = {**value, **kwargs}
        name = name or cast(str, kwargs["name"])
        if not name:
            raise ValueError(f"please provide a name for value {value!r}")
        raw_val = cast(str, kwargs.get("value") or "")
        morsel = Morsel()
        morsel.set(name, raw_val, raw_val)

    if exp := kwargs.get("expires"):
        if isinstance(exp, datetime):
            morsel["expires"] = exp.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
        elif isinstance(exp, (int, float)):
            morsel["expires"] = strftime("%a, %d-%b-%Y %H:%M:%S GMT", gmtime(exp))
    morsel.setdefault("expires", kwargs.get("expires") or "")
    morsel.setdefault("path", kwargs.get("path") or "")
    morsel.setdefault("comment", kwargs.get("comment") or "")
    morsel.setdefault("domain", kwargs.get("domain") or "")
    morsel.setdefault("secure", kwargs.get("secure"))
    morsel.setdefault("version", kwargs.get("version"))
    rest = kwargs.pop("rest", None) or {}
    morsel.setdefault("httponly", rest.get("HttpOnly"))
    morsel.setdefault("max-age", rest.get("Max-Age", ""))
    morsel.setdefault("samesite", rest.get("SameSite", ""))
    return morsel


def _to_cookie(cookie: Any, /, name: str = "", **kwargs: Any) -> Cookie:
    if isinstance(cookie, str):
        if not name:
            raise ValueError(f"please provide a name for value {cookie!r}")
        return _create_cookie(name, cookie, **kwargs)
    if isinstance(cookie, Morsel):
        return _create_cookie(cookie.key, cookie, **kwargs)
    if isinstance(cookie, Cookie):
        ck = copy(cookie)
        if name:
            ck.name = name
        return ck
    if isinstance(cookie, Mapping):
        return _create_cookie(name, cookie, **kwargs)
    return _create_cookie(
        name or getattr(cookie, "name", ""), cookie.__dict__, **kwargs
    )


def _to_morsel(cookie: Any, /, name: str = "", **kwargs: Any) -> Morsel[Any]:
    if isinstance(cookie, str):
        if not name:
            raise ValueError(f"please provide a name for value {cookie!r}")
        return _create_morsel(name, cookie, **kwargs)
    if isinstance(cookie, Morsel):
        m = copy(cookie)
        if name:
            m._key = name  # type: ignore[attr-defined]
        return m
    return _create_morsel(name, cookie, **kwargs)


def _normalize_predicate(
    predicate: None | str | Container[str] | Callable[[str, Any], bool],
) -> Callable[[str, Any], bool] | None:
    if predicate is None or callable(predicate):
        return predicate
    if isinstance(predicate, str):
        urlp = urlsplit(predicate)

        def _url_pred(_name: str, cookie: Any) -> bool:
            if isinstance(cookie, str):
                return True
            if (dom := getattr(cookie, "domain", "")) and not urlp.netloc.endswith(dom):
                return False
            path = getattr(cookie, "path", "")
            return not (path and commonpath((path, urlp.path or "/")) != path)

        return _url_pred
    return lambda name, _cookie: name in predicate


def _iter_cookie_pairs(
    cookies: Any,
    predicate: Callable[[str, Any], bool] | None = None,
) -> Iterator[tuple[str, str]]:
    if isinstance(cookies, str):
        for raw in _CRE_COOKIE_SEP_split(cookies):
            ck = raw.strip()
            if "=" in ck:
                k, v = ck.split("=", 1)
                if predicate is None or predicate(k, v):
                    yield k, v
        return
    if isinstance(cookies, CookieJar):
        for c in cookies:
            if c.value is not None and (predicate is None or predicate(c.name, c)):
                yield c.name, c.value
        return
    if isinstance(cookies, BaseCookie):
        for k, m in cookies.items():
            if predicate is None or predicate(k, m):
                yield k, m.value
        return
    if isinstance(cookies, Mapping):
        for k, v in iter_items(cookies):
            if predicate is None or predicate(k, v):
                val = v if isinstance(v, str) else v.value
                if val is not None:
                    yield k, val
        return
    for item in cookies:
        if isinstance(item, tuple):
            k, c = item[0], item[1]
        elif isinstance(item, Morsel):
            k, c = item.key, item
        else:
            k, c = getattr(item, "name", ""), item
        if k and (predicate is None or predicate(k, c)):
            val = c if isinstance(c, str) else getattr(c, "value", None)
            if val is not None:
                yield k, val


def cookies_to_dict(
    cookies: str | CookieJar | BaseCookie[Any] | Mapping[str, Any] | Iterable[Any],
    /,
    predicate: None | str | Container[str] | Callable[[str, Any], bool] = None,
) -> dict[str, str]:
    pred = _normalize_predicate(predicate)
    return dict(_iter_cookie_pairs(cookies, pred))


def cookies_to_str(
    cookies: str | CookieJar | BaseCookie[Any] | Mapping[str, Any] | Iterable[Any],
    /,
    predicate: None | str | Container[str] | Callable[[str, Any], bool] = None,
) -> str:
    if isinstance(cookies, str) and predicate is None:
        return cookies
    pred = _normalize_predicate(predicate)
    return "; ".join(f"{k}={v}" for k, v in _iter_cookie_pairs(cookies, pred) if k)


cookies_str_to_dict = cookies_to_dict
cookies_dict_to_str = cookies_to_str


def update_cookies[T: (BaseCookie[Any], CookieJar)](
    cookies1: T,
    cookies2: Any,
    /,
    **kwargs: Any,
) -> T:
    if isinstance(cookies1, BaseCookie):
        if isinstance(cookies2, BaseCookie):
            morsels: Iterable[tuple[str, Morsel[Any]]] = cookies2.items()
        elif isinstance(cookies2, CookieJar):
            morsels = ((c.name, _to_morsel(c, name=c.name, **kwargs)) for c in cookies2)
        elif isinstance(cookies2, Mapping):
            morsels = (
                (k, v if isinstance(v, Morsel) else _to_morsel(v, name=k, **kwargs))
                for k, v in iter_items(cookies2)
            )
        else:
            morsels = (
                (m.key, m)
                for m in (
                    c if isinstance(c, Morsel) else _to_morsel(c, **kwargs)
                    for c in cookies2
                )
            )
        cookies1.update(morsels)
    else:
        if isinstance(cookies2, BaseCookie):
            items: Iterable[Any] = cookies2.values()
        elif isinstance(cookies2, CookieJar):
            items = cookies2
        elif isinstance(cookies2, Mapping):
            items = (_to_cookie(v, name=k, **kwargs) for k, v in iter_items(cookies2))
        else:
            items = cookies2
        for c in items:
            cookies1.set_cookie(c if isinstance(c, Cookie) else _to_cookie(c, **kwargs))
    return cookies1


def extract_cookies[T: (BaseCookie[Any], CookieJar)](
    cookies: T,
    url: str,
    response: Any,
) -> T:
    if hasattr(response, "headers"):
        headers = response.headers
    elif hasattr(response, "getheaders"):
        headers = response.getheaders()
    elif hasattr(response, "cookies"):
        return update_cookies(cookies, response.cookies)
    elif isinstance(response, (CookieJar, BaseCookie)):
        return update_cookies(cookies, response)
    else:
        headers = response

    if isinstance(cookies, BaseCookie):
        for key, val in iter_items(headers):
            kl = key.lower()
            if kl in (b"set-cookie", b"set-cookie2"):
                cookies.load(str(val, "latin-1"))
            elif kl in ("set-cookie", "set-cookie2"):
                cookies.load(val)
    else:
        cookies.extract_cookies(response, Request(url))
    return cookies


def cookie_header_for_url(cookies: Any, url: str, /) -> dict[str, str]:
    if isinstance(cookies, CookieJar):
        req = Request(url)
        cookies.add_cookie_header(req)
        return cookies_to_dict(req.unredirected_hdrs.get("Cookie") or "")
    now = int(time())
    data: dict[str, str] = {}
    urlp = urlsplit(url)
    for name, cookie in iter_items(cookies):
        if isinstance(cookie, Cookie):
            if not _cookie_match_domain(urlp.netloc, cookie.domain):
                continue
            if not _cookie_match_path(urlp.path, cookie.path):
                continue
            if cookie.expires and int(cookie.expires) <= now:
                continue
            data[name] = cookie.value or ""
        elif isinstance(cookie, Morsel):
            if not _cookie_match_domain(urlp.netloc, cookie.get("domain")):
                continue
            if not _cookie_match_path(urlp.path, cookie.get("path")):
                continue
            exp = _parse_expires(cookie.get("expires"))
            if exp and exp <= now:
                continue
            data[name] = cookie.value
        else:
            data[name] = cookie
    return data


# ---------------------------------------------------------------------------
# HTTP 响应解析工具（替代 _vendor/http_response.py）
# ---------------------------------------------------------------------------


def get_status_code(response: Any, /) -> int:
    for attr in ("status", "code", "status_code"):
        if isinstance(status := getattr(response, attr, None), int):
            return status
    if inner := getattr(response, "response", None):
        return get_status_code(inner)
    return 0


def is_timeouterror(exc: BaseException) -> bool:
    exctype = type(exc)
    if issubclass(exctype, TimeoutError):
        return True
    return any("Timeout" in cls.__name__ for cls in exctype.mro())


def headers_get(
    response: Any,
    /,
    key: bytes | str,
    default: Any = None,
    parse: Any = None,
) -> Any:
    if hasattr(response, "getheaders"):
        headers = response.getheaders()
    elif hasattr(response, "headers"):
        headers = response.headers
    else:
        headers = response

    if isinstance(headers, Mapping):
        val = get(headers, key, default=None)
        if val is None:
            alt: bytes | str = (
                key.encode("latin-1") if isinstance(key, str) else key.decode("latin-1")
            )
            val = get(headers, alt, default=None)
            if val is None:
                return default
    else:
        key_l = key.lower()
        alt_l: bytes | str = (
            key_l.encode("latin-1")
            if isinstance(key_l, str)
            else key_l.decode("latin-1")
        )
        for k, v in headers:
            kl = k.lower()
            if kl in (key_l, alt_l):
                val = v
                break
        else:
            return default

    if parse is None:
        return val
    if callable(parse):
        return parse(val)
    if isinstance(parse, (bytes, str)):
        return val == parse
    if isinstance(parse, Mapping):
        return headers_get(parse, val, default)
    if isinstance(parse, Container):
        return val in parse
    return val


def get_filename(response: Any, /, default: str = "") -> str:
    if hdr_cd := headers_get(response, "content-disposition"):
        if match := _CRE_HDR_CD_FNAME_STAR_search(hdr_cd):
            return unquote(match["name"], match["charset"] or "utf-8")
        if match := _CRE_HDR_CD_FNAME_search(hdr_cd):
            return match[0]
    url = response.url
    if not isinstance(url, (bytearray, bytes, str)):
        url = str(url)
    urlp = urlsplit(url)
    for key, val in parse_qsl(urlp.query):
        if val and key.lower() in ("filename", "file_name"):
            return unquote(val)
    filename = posix_basename(unquote(urlp.path)) or default
    if filename:
        if guess_type(filename)[0]:
            return filename
        if hdr_ct := headers_get(response, "content-type"):
            ct = hdr_ct.partition(";")[0].strip()
            ext = (ct and guess_extension(ct)) or ""
            if ext and not filename.endswith(ext, 1):
                filename += ext
    return filename


def get_mimetype(content_type: str, /) -> str:
    return content_type.strip(" ;").partition(";")[0].strip()


def get_charset(content_type: str, /, default: str = "utf-8") -> str:
    if match := _CRE_CHARSET_search(content_type):
        try:
            return codecs_lookup(match["charset"]).name
        except LookupError:
            return match["charset"].strip()
    return default


def get_content_length(response: Any, /) -> int | None:
    if length := headers_get(response, "content-length"):
        return int(length)
    return None


def get_range(response: Any, /) -> tuple[int, int, int] | None:
    hdr_cr = headers_get(response, "content-range")
    if not hdr_cr:
        return None
    if match := _CRE_CONTENT_RANGE_fullmatch(hdr_cr):
        begin_s, end_s, size_s = match.groups()
        if begin_s:
            begin, end = int(begin_s), int(end_s)
            size = int(size_s) if size_s else end + 1
            return begin, end, size
        if size_s:
            size = int(size_s)
            return (0, 0, 0) if size == 0 else (0, size - 1, size)
    return None


def get_length(response: Any, /) -> int | None:
    if (length := get_content_length(response)) is not None:
        return length
    if rng := get_range(response):
        return rng[1] - rng[0] + 1
    return None


def get_total_length(response: Any, /) -> int | None:
    if rng := get_range(response):
        return rng[-1]
    return get_content_length(response)


def is_chunked(response: Any, /) -> bool:
    return bool(
        headers_get(response, "transfer-encoding", default=False, parse="chunked")
    )


def is_range_request(response: Any, /) -> bool:
    return bool(
        headers_get(response, "accept-ranges", parse="bytes")
        or headers_get(response, "content-range")
    )


def parse_response(response: Any, content: bytes, /) -> Any:
    content_type = headers_get(response, "content-type", default="")
    if not isinstance(content_type, str):
        content_type = str(content_type, "latin-1")
    mimetype = get_mimetype(content_type)
    charset = get_charset(content_type)
    if mimetype == "application/json":
        return json_loads(content if charset == "utf-8" else content.decode(charset))
    if content_type.startswith("text/"):
        return content.decode(charset)
    return content


def decompress_response(data: bytes, /, content_encoding: Any = None) -> bytes:
    if content_encoding and not isinstance(content_encoding, (bytes, str)):
        content_encoding = headers_get(content_encoding, "content-encoding")
    if not content_encoding:
        return data
    if not isinstance(content_encoding, str):
        content_encoding = str(content_encoding, "latin-1")
    match content_encoding:
        case "gzip":
            return _decompress_gzip(data)
        case "deflate":
            try:
                return _zlib_decompress(data)
            except Exception:
                return _zlib_decompress(data, -MAX_WBITS)
        case "br":
            from brotli import decompress as decompress_br  # type: ignore[import-not-found]

            return decompress_br(data)
        case "zstd":
            try:
                from compression.zstd import decompress as decompress_zstd  # type: ignore[import-not-found]
            except ImportError:
                from zstandard import decompress as decompress_zstd  # type: ignore[import-not-found]

            return decompress_zstd(data)
    return data


# ---------------------------------------------------------------------------
# URL 补全与 HTTP 请求参数规范化（替代 _vendor/http_request/）
# ---------------------------------------------------------------------------

_QUERY_KEY_TRANSTAB: Final = {k: f"%{k:02X}" for k in b"&="}
_CRE_URL_SCHEME_match: Final = re_compile(r"(?i:[a-z][a-z0-9.+-]*)://").match


class RequestArgs(TypedDict):
    method: str
    url: str
    data: None | Buffer | Iterable[Buffer] | AsyncIterable[Buffer]
    headers: dict[str, str]


@runtime_checkable
class SupportsGeturl[AnyStr: (bytes, str)](Protocol):
    def geturl(self) -> AnyStr: ...


def _json_default(o: Any, /) -> Any:
    if isinstance(o, Mapping):
        return dict(o)
    if isinstance(o, Buffer):
        return ensure_str(o)
    if isinstance(o, UserString):
        return str(o)
    if isinstance(o, Integral):
        return int(o)
    if isinstance(o, (Real, Fraction, Decimal)):
        try:
            return float(o)
        except Exception:
            return str(o)
    if isinstance(o, (Iterator, Sequence)):
        return list(o)
    return str(o)


def _urlencode(
    payload: Any,
    /,
    encoding: str = "utf-8",
    errors: str = "strict",
    ensure_ascii: bool = True,
) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, UserString):
        return str(payload)
    if isinstance(payload, Buffer):
        return str(payload, encoding, errors)

    parts: list[str] = []
    for i, (k, v) in enumerate(iter_items(payload)):
        if i:
            parts.append("&")
        k_str = str(k, encoding, errors) if isinstance(k, Buffer) else str(k)
        parts.append(
            quote(k_str) if ensure_ascii else k_str.translate(_QUERY_KEY_TRANSTAB)
        )
        parts.append("=")
        if v is True:
            parts.append("true")
            continue
        if v is False:
            parts.append("false")
            continue
        if v is None:
            parts.append("null")
            continue
        if isinstance(v, (str, UserString)):
            v_str = str(v)
        elif isinstance(v, Buffer):
            v_str = str(v, encoding, errors)
        elif isinstance(v, (Mapping, Iterable)):
            v_str = json_dumps(v, default=_json_default).decode("utf-8")
        else:
            v_str = str(v)
        parts.append(quote(v_str) if ensure_ascii else v_str.replace("&", "%26"))
    return "".join(parts)


def complete_url(url: str, /, default_port: int = 0, params: Any = None) -> str:
    if url.startswith("/"):
        url = "http://localhost" + url
    elif url.startswith("//"):
        url = "http:" + url
    elif url.startswith("://"):
        url = "http" + url
    if not (params or default_port):
        if not _CRE_URL_SCHEME_match(url):
            url = "http://" + url
        return url
    urlp = urlparse(url)
    repl: dict[str, str] = {}
    if not urlp.scheme:
        repl["scheme"] = "http"
    netloc = urlp.netloc or "localhost"
    if default_port and not urlp.port:
        netloc = netloc.removesuffix(":") + f":{default_port}"
    if netloc != urlp.netloc:
        repl["netloc"] = netloc
    if params and (qs := _urlencode(params)):
        repl["query"] = f"{urlp.query}&{qs}" if urlp.query else qs
    if not repl:
        return url
    return urlunparse(urlp._replace(**repl)).rstrip("/")


def _ensure_ascii_url(url: str, /) -> str:
    return url if url.isascii() else quote(url, safe=punctuation)


def _prepare_multipart_item(
    name: Any,
    value: Any,
    *,
    is_file: bool,
    suffix: bytes,
    ensure_value: Callable[[Any], Any],
    async_: bool,
) -> tuple[dict[bytes, bytes], Any]:
    headers: dict[bytes, bytes] = {
        b"content-disposition": (
            f'form-data; name="{quote(ensure_str(name))}"'.encode("ascii")
        )
    }
    filename = b""
    if isinstance(value, (list, tuple)):
        match value:
            case [val]:
                value = val
            case [fname, val]:
                filename, value = _ensure_bytes(fname), val
            case [fname, val, ftype]:
                filename, value = _ensure_bytes(fname), val
                if ftype:
                    headers[b"content-type"] = _ensure_bytes(ftype)
            case [fname, val, ftype, fhdrs, *_]:
                filename, value = _ensure_bytes(fname), val
                for k, v in iter_items(fhdrs):
                    headers[_ensure_bytes(k).lower()] = _ensure_bytes(v)
                if ftype:
                    headers[b"content-type"] = _ensure_bytes(ftype)

    if isinstance(value, (PathLike, SupportsRead)):
        is_file = True
        if isinstance(value, PathLike):
            fobj: Any = open(value, "rb")  # noqa: SIM115
        elif isinstance(value, TextIOWrapper):
            fobj = value.buffer
        else:
            fobj = value
        if not filename:
            filename = _ensure_bytes(os_basename(getattr(fobj, "name", b"") or b""))
        value = bio_chunk_async_iter(fobj) if async_ else bio_chunk_iter(fobj)
    elif isinstance(value, Buffer):
        pass
    elif isinstance(value, (str, UserString)):
        value = _ensure_bytes(value)
    elif async_ and isinstance(value, (Iterable, AsyncIterable)):
        value = async_map(ensure_value, value)
    elif isinstance(value, Iterable):
        value = map(ensure_value, value)
    else:
        value = ensure_value(value)

    if is_file:
        if filename:
            filename = quote(filename).encode("ascii")
            if suffix and not filename.endswith(suffix):
                filename += suffix
        else:
            filename = uuid4().hex.encode("ascii") + suffix
        if b"content-type" not in headers:
            guessed = guess_type(filename.decode("latin-1"))[0]
            headers[b"content-type"] = _ensure_bytes(
                guessed or b"application/octet-stream"
            )
        headers[b"content-disposition"] += b'; filename="' + filename + b'"'
    return headers, value


def _encode_multipart_data(
    data: Any = None,
    files: Any = None,
    *,
    ensure_bytes: bool = False,
    async_: bool = False,
) -> tuple[dict[str, str], Iterator[Buffer] | AsyncIterator[Buffer]]:
    ensure_val: Callable[[Any], Any] = _ensure_bytes if ensure_bytes else ensure_buffer
    boundary = uuid4().hex
    boundary_bytes = boundary.encode("ascii")
    boundary_line = b"--" + boundary_bytes + b"\r\n"
    header = {"content-type": "multipart/form-data; boundary=" + boundary}

    if async_:

        async def _agen() -> AsyncIterator[Buffer]:
            for src, is_file in ((data, False), (files, True)):
                if not src:
                    continue
                for name, raw_val in iter_items(src):
                    hdrs, val = _prepare_multipart_item(
                        name,
                        raw_val,
                        is_file=is_file,
                        suffix=b"",
                        ensure_value=ensure_val,
                        async_=True,
                    )
                    yield boundary_line
                    for k, v in hdrs.items():
                        yield k + b": " + v + b"\r\n"
                    yield b"\r\n"
                    if isinstance(val, Buffer):
                        yield val
                    elif isinstance(val, AsyncIterable):
                        async for chunk in val:
                            yield chunk
                    else:
                        for chunk in val:
                            yield chunk
                    yield b"\r\n"
            yield b"--" + boundary_bytes + b"--\r\n"

        return header, _agen()

    def _gen() -> Iterator[Buffer]:
        for src, is_file in ((data, False), (files, True)):
            if not src:
                continue
            for name, raw_val in iter_items(src):
                hdrs, val = _prepare_multipart_item(
                    name,
                    raw_val,
                    is_file=is_file,
                    suffix=b"",
                    ensure_value=ensure_val,
                    async_=False,
                )
                yield boundary_line
                for k, v in hdrs.items():
                    yield k + b": " + v + b"\r\n"
                yield b"\r\n"
                if isinstance(val, Buffer):
                    yield val
                else:
                    yield from val
                yield b"\r\n"
        yield b"--" + boundary_bytes + b"--\r\n"

    return header, _gen()


def normalize_request_args(
    method: Any,
    url: Any,
    params: Any = None,
    data: Any = None,
    json: Any = None,
    files: Any = None,
    headers: Any = None,
    ensure_ascii: bool = True,
    ensure_bytes: bool = False,
    *,
    async_: bool = False,
) -> RequestArgs:
    ensure_val: Callable[[Any], Any] = _ensure_bytes if ensure_bytes else ensure_buffer
    method_str = ensure_str(method).upper()
    if isinstance(url, SupportsGeturl):
        url = url.geturl()
    elif isinstance(url, URL):
        url = str(url)
    url_str = complete_url(ensure_str(url), params=params)
    if ensure_ascii:
        url_str = _ensure_ascii_url(url_str)
    headers_ = dict_map(
        headers or (),
        key=lambda k: ensure_str(k).lower(),
        value=ensure_str,
    )
    content_type = headers_.get("content-type", "")
    charset = get_charset(content_type)
    mimetype = get_mimetype(content_type).lower()

    if files:
        mp_headers, data = _encode_multipart_data(
            data,
            files,
            ensure_bytes=ensure_bytes,
            async_=async_,
        )
        headers_.update(mp_headers)
    elif data is not None:
        if isinstance(data, Buffer):
            pass
        elif isinstance(data, SupportsRead):
            data = bio_chunk_async_iter(data) if async_ else bio_chunk_iter(data)
        elif isinstance(data, (str, UserString)):
            data = str(data).encode(charset)
        elif isinstance(data, AsyncIterable):
            data = async_map(ensure_val, data)
        elif isinstance(data, Iterator):
            data = async_map(ensure_val, data) if async_ else map(ensure_val, data)
        elif mimetype == "application/json":
            if charset == "utf-8":
                data = json_dumps(data, default=_json_default)
            else:
                from json import dumps as std_json_dumps

                data = std_json_dumps(data, default=_json_default).encode(charset)
        elif isinstance(data, (Mapping, Sequence)):
            if data:
                data = _urlencode(data, charset, ensure_ascii=ensure_ascii).encode(
                    charset
                )
                if mimetype != "application/x-www-form-urlencoded":
                    headers_["content-type"] = "application/x-www-form-urlencoded"
        else:
            data = str(data).encode(charset)
    elif json is not None:
        if isinstance(json, Buffer):
            data = json
        elif isinstance(json, SupportsRead):
            data = bio_chunk_async_iter(json) if async_ else bio_chunk_iter(json)
        elif isinstance(json, AsyncIterable):
            data = async_map(ensure_val, json)
        elif isinstance(json, Iterator):
            data = async_map(ensure_val, json) if async_ else map(ensure_val, json)
        elif charset == "utf-8":
            data = json_dumps(json, default=_json_default)
        else:
            from json import dumps as std_json_dumps

            data = std_json_dumps(json, default=_json_default).encode(charset)
        if mimetype != "application/json":
            headers_["content-type"] = "application/json; charset=" + charset
    elif mimetype == "application/json":
        data = b"null"
    return {"url": url_str, "method": method_str, "data": data, "headers": headers_}
