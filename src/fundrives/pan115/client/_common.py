#!/usr/bin/env python3

from __future__ import annotations

__doc__ = "115 客户端模块"

from asyncio import Lock as AsyncLock
from base64 import b64encode
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
    MutableMapping,
    Sequence,
)
from datetime import date, datetime, timedelta
from hashlib import md5, sha1
from http.cookiejar import Cookie, CookieJar
from http.cookies import BaseCookie, Morsel
from inspect import isawaitable
from operator import itemgetter
from os import PathLike, fsdecode, isatty
from pathlib import Path, PurePath
from re import MULTILINE, Match
from re import compile as re_compile
from string import digits
from threading import Lock
from time import time
from typing import Any, Final, Literal, Self, cast, overload
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlsplit
from uuid import uuid4
from warnings import warn

from orjson import dumps, loads
from yarl import URL

from fundrives.pan115._http import (
    SupportsGeturl,
    cookies_to_dict,
    get_status_code,
    update_cookies,
)
from fundrives.pan115._http import (
    complete_url as make_url,
)
from fundrives.pan115._utils import (
    KeyLowerDict,
    dict_key_to_lower_merge,
    dict_update,
    ensure_bytes,
    errno,
    get_first,
    iter_items,
    locked_cacheproperty,
)
from fundrives.pan115._vendor.asynctools import ensure_async
from fundrives.pan115._vendor.filewrap import SupportsRead, to_bytes_view
from fundrives.pan115._vendor.httpfile import AsyncHTTPFileReader, HTTPFileReader
from fundrives.pan115._vendor.iterutils import run_gen_step
from fundrives.pan115._vendor.p115cipher import (
    ecdh_aes_decrypt,
    ecdh_aes_encrypt,
    ecdh_encode_token,
    make_upload_payload,
    rsa_decrypt,
    rsa_encrypt,
)
from fundrives.pan115._vendor.p115oss import upload_file
from fundrives.pan115._vendor.p115pickcode import to_id, to_pickcode

from ..const import (
    CLIENT_API_METHODS_MAP,
    CLIENT_METHOD_API_MAP,
    SSOENT_TO_APP,
)
from ..exception import (
    P115AccessTokenError,
    P115AuthenticationError,
    P115DownloadFileNotFoundError,
    P115LoginError,
    P115OpenAppAuthLimitExceeded,
    P115OperationalError,
    P115OSError,
    P115Warning,
    throw,
)
from ..type import P115URL, P115Cookies
from ..util import complete_url, normalize_pickcode, share_extract_payload

CRE_SET_COOKIE: Final = re_compile(r"[0-9a-f]{32}=[0-9a-f]{32}.*")
CRE_COOKIES_UID_search: Final = re_compile(r"(?<=\bUID=)[^\s;]+").search
CRE_AREA_DATA_search: Final = re_compile(r"(?<=n=)\{[\s\S]+?\}(?=;)").search

_default_k_ec = {"k_ec": ecdh_encode_token(0).decode()}
_default_code_verifier = "0" * 64
_default_code_challenge = b64encode(md5(b"0" * 64).digest()).decode()
_default_code_challenge_method = "md5"
_app_version = "36.2.28"


def content_maybe_decrypt(content: Buffer, /) -> Buffer:
    data = to_bytes_view(content)
    if data[:1].tobytes() + data[-1:].tobytes() not in (b"{}", b"[]", b'""'):
        return ecdh_aes_decrypt(data)
    return content


def json_loads(content: Buffer, /):
    try:
        return loads(to_bytes_view(content))
    except Exception:
        throw(errno.ENODATA, bytes(content))


def json_decrypt_loads(content: Buffer, /):
    return json_loads(ecdh_aes_decrypt(content))


def json_maybe_decrypt_loads(content: Buffer, /):
    return json_loads(content_maybe_decrypt(content))


def json_parse(_, content: Buffer, /):
    return json_loads(content)


def json_decrypt_parse(_, content: Buffer, /):
    return json_decrypt_loads(content)


def json_maybe_decrypt_parse(_, content: Buffer, /):
    return json_maybe_decrypt_loads(content)


def get_request(
    url: str,
    method: str = "GET",
    payload: Any = None,
    headers: Any = None,
    ecdh_encrypt: bool = False,
    request: None | Callable = None,
    self: None | ClientRequestMixin = None,
    **request_kwargs,
) -> tuple[Callable, dict]:
    if self is not None:
        request_kwargs.update(
            url=url,
            method=method,
            payload=payload,
            headers=headers,
            ecdh_encrypt=ecdh_encrypt,
            request=request,
        )
        return self.request, request_kwargs
    if request is None:
        from fundrives.pan115._request import request
    request = cast(Callable, request)
    request_kwargs.update(url=url, method=method)
    is_open_api = URL(url).path.startswith("/open/")
    if is_open_api:
        ecdh_encrypt = False
    if payload is not None:
        request_kwargs.setdefault(
            "data" if method.upper() in ("POST", "PUT") else "params",
            payload,
        )
    params = request_kwargs.get("params")
    if isinstance(params, dict):
        params.setdefault("app_ver", _app_version)
    headers = request_kwargs["headers"] = dict_key_to_lower_merge(headers or ())
    headers["referer"] = headers.get("referer") or str(URL(url).origin())
    if ecdh_encrypt:
        url = request_kwargs["url"] = make_url(url, params=_default_k_ec)
        if data := request_kwargs.get("data"):
            if not isinstance(data, (Buffer, str, UserString)):
                data = urlencode(data)
            request_kwargs["data"] = ecdh_aes_encrypt(ensure_bytes(data) + b"&")
            headers["content-type"] = "application/x-www-form-urlencoded"
        request_kwargs.setdefault("parse", json_decrypt_parse)
    else:
        request_kwargs.setdefault("parse", json_parse)
    return request, request_kwargs


def md5_secret_password(
    password: None | int | str = "670b14728ad9902aecba32e22fa4f6bd", /
) -> str:
    if not password:
        return "670b14728ad9902aecba32e22fa4f6bd"
    if isinstance(password, str) and len(password) == 32:
        return password
    return md5(f"{password:>06}".encode("ascii")).hexdigest()


def parse_upload_init_response(_, content: bytes, /) -> dict:
    data = ecdh_aes_decrypt(content)
    if not isinstance(data, (bytes, bytearray)):
        data = to_bytes_view(data)
    return json_loads(data)


def expand_payload(
    payload: dict[str, Any] | Iterable[tuple[str, Any]],
    prefix: str = "",
    enum_seq: bool | int = False,
    seq_types: type | tuple[type, ...] = (tuple, list),
    map_types: type | tuple[type, ...] = dict,
) -> Iterable[tuple[str, Any]]:
    if prefix:
        prefix = f"{prefix}["
    for k, v in iter_items(payload):
        if prefix and not k.startswith(prefix):
            k = f"{prefix}{k}]"
        if isinstance(v, seq_types):
            v = cast(Sequence, v)
            if isinstance(enum_seq, bool):
                if enum_seq:
                    enum_seq = 0
                else:
                    for v2 in v:
                        yield from expand_payload(v2, f"{k}[]")
                    continue
                for i, v2 in enumerate(v, cast(int, enum_seq)):
                    yield from expand_payload(v2, f"{k}[{i}]")
        elif isinstance(v, map_types):
            v = cast(Mapping, v)
            k2: Any
            for k2, v2 in iter_items(v):
                yield from expand_payload(v2, f"{k}[{k2}]")
        else:
            yield k, v


@overload
def check_response(resp: dict, /) -> dict: ...
@overload
def check_response(resp: Awaitable[dict], /) -> Coroutine[Any, Any, dict]: ...
def check_response(resp: dict | Awaitable[dict], /) -> dict | Coroutine[Any, Any, dict]:
    """检测 115 的某个接口的响应，如果成功则直接返回，否则根据具体情况抛出一个异常，基本上是 OSError 的实例"""

    def check(resp, /) -> dict:
        if not isinstance(resp, dict):
            raise P115OSError(errno.EIO, resp)
        if resp.get("state", True):
            return resp
        if code := get_first(
            resp,
            "errno",
            "errNo",
            "errcode",
            "errCode",
            "code",
            "msg_code",
            default=None,
        ):
            resp.setdefault("errno", code)
            if "error" not in resp:
                resp.setdefault(
                    "error",
                    get_first(resp, "msg", "error_msg", "message", default=None),
                )
            match code:
                # {"state": False, "error": "网盘单个文件夹限5万个文件，请清理后再添加！", "errno": 2}
                case 2:
                    raise P115OperationalError(errno.EIO, resp)
                # {"state": false, "errno": 99, "error": "请重新登录"}
                case 99:
                    raise P115LoginError(errno.EAUTH, resp)
                # {"state": false, "errno": 911, "error": "请验证账号"}
                case 911:
                    throw(errno.EAUTH, resp)
                # {"state": false, "errno": 1001, "error": "参数错误"}
                case 1001:
                    throw(errno.EINVAL, resp)
                # {"state": false, "errno": 10004, "error": "错误的链接"}
                case 10004:
                    throw(errno.EINVAL, resp)
                # {"state": false, "errno": 10014, "error": "云端目录不存在，请恢复后重新上传"}
                case 10014:
                    throw(errno.ENOENT, resp)
                # {"state": false, "errno": 20001, "error": "目录名称不能为空"}
                case 20001:
                    throw(errno.EINVAL, resp)
                # {"state": false, "errno": 20002, "error": "目录名称不能超出20个字。"}
                case 20002:
                    throw(errno.EINVAL, resp)
                # {"state": false, "errno": 20003, "error": "文件名不能包含以下任意字符之一 “ " < > ”。"}
                case 20003:
                    throw(errno.EINVAL, resp)
                # {"state": false, "errno": 20004, "error": "该目录名称已存在。"}
                case 20004:
                    throw(errno.EEXIST, resp)
                # {"state": false, "errno": 20009, "error": "父目录不存在。"}
                case 20009:
                    throw(errno.ENOENT, resp)
                # {"state": false, "errno": 20013, "error": "文件夹不存在或已删除。"}
                # {"state": false, "errno": 20018, "error": "文件不存在或已删除。"}
                # {"state": false, "errno": 31003, "error": "文件不存在或已删除。"}
                # {"state": false, "errno": 50015, "error": "文件不存在或已删除。"}
                # {"state": false, "errno": 70005, "error": "文件不存在或已删除"}
                # {"state": false, "errno": 70008, "error": "文件不存在或已删除"}
                # {"state": false, "errno": 90008, "error": "文件（夹）不存在或已经删除。"}
                # {"state": false, "errno": 430004, "error": "文件（夹）不存在或已删除。"}
                case 20013 | 20018 | 31003 | 50015 | 70005 | 70008 | 90008 | 430004:
                    if resp.get("is_download"):
                        raise P115DownloadFileNotFoundError(errno.ENOENT, resp)
                    throw(errno.ENOENT, resp)
                # {"state": false, "errno": 20020, "error": "后缀名不正确，请重新输入"}
                # {"state": false, "errno": 20021, "error": "后缀名不正确，请重新输入"}
                case 20020 | 20021:
                    throw(errno.EINVAL, resp)
                # {"state": false, "errno": 31001, "error": "所预览的文件不存在。"}
                case 31001:
                    throw(errno.ENOENT, resp)
                # {"state": false, "errno": 31004, "error": "文档未上传完整，请上传完成后再进行查看。"}
                case 31004:
                    throw(errno.ENOENT, resp)
                # {"state": false, "errno": 50003, "error": "很抱歉，该文件提取码不存在。"}
                case 50003:
                    throw(errno.ENOENT, resp)
                # {"state": false, "errno": 50028, "error": "文件大小超出限制，请使用115电脑端下载"}
                case 50028:
                    throw(errno.EFBIG, resp)
                # {"state": false, "errno": 50038, "error": "下载失败，含违规内容"}
                case 50038:
                    throw(errno.EACCES, resp)
                # {"state": false, "errno": 51011, "error": "不允许转存空文件夹"}
                case 51011:
                    raise P115OperationalError(errno.EPERM, resp)
                # {"state": false, "errno": 51012, "error": "已有文件正在解压中，请稍后再试"}
                case 51012:
                    throw(errno.EBUSY, resp)
                # {"state": false, "errno": 70004, "error": "文件上传不完整"}
                case 70004:
                    throw(errno.EISDIR, resp)
                # {"state": false, "errno": 91002, "error": "不能将文件复制到自身或其子目录下。"}
                case 91002:
                    throw(errno.ENOTSUP, resp)
                # {"state": false, "errno": 91004, "error": "操作的文件(夹)数量超过5万个"}
                case 91004:
                    throw(errno.ENOTSUP, resp)
                # {"state": false, "errno": 91005, "error": "空间不足，复制失败。"}
                case 91005:
                    throw(errno.ENOSPC, resp)
                # {"state": false, "errno": 231011, "error": "文件已删除，请勿重复操作"}
                case 231011:
                    throw(errno.ENOENT, resp)
                # {"state": false, "errno": 300104, "error": "文件超过200MB，暂不支持播放"}
                case 300104:
                    throw(errno.EFBIG, resp)
                # {"state": false, "errno": 300105, "error": "文件超过500MB，暂不支持添加到我听"}
                case 300105:
                    throw(errno.EFBIG, resp)
                # {"state": false, "errno": 320001, "error": "很抱歉,安全密钥不正确"}
                case 320001:
                    throw(errno.EINVAL, resp)
                # {"state": false, "errno": 590075, "error": "操作太频繁，请稍候再试"}
                case 590075:
                    throw(errno.EBUSY, resp)
                # {"state": false, "errno": 800001, "error": "目录不存在。"}
                case 800001:
                    throw(errno.ENOENT, resp)
                # {"state": false, "errno": 980006, "error": "404 Not Found"}
                case 980006:
                    throw(errno.ENOSYS, resp)
                # {"state": false, "errno": 990001, "error": "登陆超时，请重新登陆。"}
                case 990001:
                    # NOTE: 可能就是被下线了
                    throw(errno.EAUTH, resp)
                # {"state": false, "errno": 990002, "error": "参数错误。"}
                case 990002:
                    throw(errno.EINVAL, resp)
                # {"state": false, "errno": 990003, "error": "操作失败。"}
                case 990003:
                    raise P115OperationalError(errno.EIO, resp)
                # {"state": false, "errno": 990005, "error": "你的账号有类似任务正在处理，请稍后再试！"}
                case 990005:
                    throw(errno.EBUSY, resp)
                # {"state": false, "errno": 990009, "error": "删除[...]操作尚未执行完成，请稍后再试！"}
                # {"state": false, "errno": 990009, "error": "还原[...]操作尚未执行完成，请稍后再试！"}
                # {"state": false, "errno": 990009, "error": "复制[...]操作尚未执行完成，请稍后再试！"}
                # {"state": false, "errno": 990019, "error": "移动[...]操作尚未执行完成，请稍后再试！"}
                case 990009 | 990019:
                    throw(errno.EBUSY, resp)
                # {"state": false, "errno": 990023, "error": "操作的文件(夹)数量超过5万个"}
                case 990023:
                    throw(errno.ENOTSUP, resp)
                # {"state": false, "errno": 4100026, "error": "该文件分享链接不存在或已被删除"}
                case 4100026:
                    throw(errno.ENOENT, resp)
                # {"state": false, "errno": 4100030, "error": "接收文件过多"}
                case 4100030:
                    throw(errno.EIO, resp)
                # {"state": 0, "errno": 40100000, "error": "参数错误！"}
                # {"state": 0, "errno": 40100000, "error": "参数缺失"}
                case 40100000:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40101004, "error": "IP登录异常,请稍候再登录！"}
                case 40101004:
                    raise P115LoginError(errno.EAUTH, resp)
                # {"state": 0, "errno": 40101017, "error": "用户验证失败！"}
                case 40101017:
                    throw(errno.EAUTH, resp)
                # {"state": 0, "errno": 40101032, "error": "请重新登录"}
                case 40101032:
                    raise P115LoginError(errno.EAUTH, resp)
                #################################################################
                # Reference: https://www.yuque.com/115yun/open/rnq0cbz8tt7cu43i #
                #################################################################
                # {"state": 0, "errno": 40110000, "error": "请求异常需要重试"}
                case 40110000:
                    raise P115OperationalError(errno.EAGAIN, resp)
                # {"state": 0, "errno": 40140100, "error": "client_id 错误"}
                case 40140100:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140101, "error": "code_challenge 必填"}
                case 40140101:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140102, "error": "code_challenge_method 必须是 sha256、sha1、md5 之一"}
                case 40140102:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140103, "error": "sign 必填"}
                case 40140103:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140104, "error": "sign 签名失败"}
                case 40140104:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140105, "error": "生成二维码失败"}
                case 40140105:
                    raise P115OperationalError(errno.EIO, resp)
                # {"state": 0, "errno": 40140106, "error": "APP ID 无效"}
                case 40140106:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140107, "error": "应用不存在"}
                case 40140107:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140108, "error": "应用未审核通过"}
                case 40140108:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140109, "error": "应用已被停用"}
                case 40140109:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140110, "error": "应用已过期"}
                case 40140110:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140111, "error": "APP Secret 错误"}
                case 40140111:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140112, "error": "code_verifier 长度要求43~128位"}
                case 40140112:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140113, "error": "code_verifier 验证失败"}
                case 40140113:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140114, "error": "refresh_token 格式错误（防篡改）"}
                case 40140114:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140115, "error": "refresh_token 签名校验失败（防篡改）"}
                case 40140115:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140116, "error": "refresh_token 无效（已解除授权）"}
                case 40140116:
                    raise P115OperationalError(errno.EIO, resp)
                # {"state": 0, "errno": 40140117, "error": "access_token 刷新太频繁"}
                case 40140117:
                    throw(errno.EBUSY, resp)
                # {"state": 0, "errno": 40140118, "error": "开发者认证已过期"}
                case 40140118:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140119, "error": "refresh_token 已过期"}
                case 40140119:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140120, "error": "refresh_token 检验失败（防篡改）"}
                case 40140120:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140121, "error": "access_token 刷新失败"}
                case 40140121:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140122, "error": "超出授权应用个数上限"}
                case 40140122:
                    raise P115OpenAppAuthLimitExceeded(errno.EDQUOT, resp)
                # {"state": 0, "errno": 40140123, "error": "access_token 格式错误（防篡改）"}
                case 40140123:
                    raise P115AccessTokenError(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140124, "error": "access_token 签名校验失败（防篡改）"}
                case 40140124:
                    raise P115AccessTokenError(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140125, "error": "access_token 无效（已过期或者已解除授权）"}
                case 40140125:
                    raise P115AccessTokenError(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140126, "error": "access_token 校验失败（防篡改）"}
                case 40140126:
                    raise P115AccessTokenError(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140127, "error": "response_type 错误"}
                case 40140127:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140128, "error": "redirect_uri 缺少协议"}
                case 40140128:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140129, "error": "redirect_uri 缺少域名"}
                case 40140129:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140130, "error": "没有配置重定向域名"}
                case 40140130:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140131, "error": "redirect_uri 非法域名"}
                case 40140131:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140132, "error": "grant_type 错误"}
                case 40140132:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140133, "error": "client_secret 验证失败"}
                case 40140133:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140134, "error": "授权码 code 验证失败"}
                case 40140134:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140135, "error": "client_id 验证失败"}
                case 40140135:
                    throw(errno.EINVAL, resp)
                # {"state": 0, "errno": 40140136, "error": "redirect_uri 验证失败（防MITM）"}
                case 40140136:
                    throw(errno.EINVAL, resp)
        elif error := resp.get("error"):
            if "文件不存在" in error or "目录不存在" in error:
                throw(errno.ENOENT, resp)
            elif "目录名称已存在" in error:
                throw(errno.EEXIST, resp)
            elif error == "更新的数据为空":
                throw(errno.EINVAL, resp)
        throw(errno.EIO, resp)

    if isinstance(resp, dict):
        return check(resp)
    if isawaitable(resp):

        async def check_await() -> dict:
            return check(await resp)

        return check_await()
    throw(errno.EIO, resp)


class ClientRequestMixin:
    app_id: int = 0
    cookies_path: PurePath

    @locked_cacheproperty
    def cookies(self, /) -> CookieJar:
        """公用 cookiejar"""
        return CookieJar()

    @locked_cacheproperty
    def headers(self, /) -> KeyLowerDict[str, str]:
        """公用请求头"""
        return KeyLowerDict[str, str](
            {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "connection": "keep-alive",
                "user-agent": "Mozilla/5.0",
            }
        )

    @locked_cacheproperty
    def user_id(self, /) -> int:
        for cookie in self.cookies:
            if cookie.name == "UID":
                return int(cookie.value.partition("_")[0])
        from .open_client import P115OpenClient

        if isinstance(self, P115OpenClient):
            resp = check_response(self.user_info_open())
            return int(resp["data"]["user_id"])
        raise LookupError("can't get user_id")

    @locked_cacheproperty
    def request_lock(self, /) -> Lock:
        return Lock()

    @locked_cacheproperty
    def request_alock(self, /) -> AsyncLock:
        return AsyncLock()

    @property
    def cookies_str(self, /) -> P115Cookies:
        """所有名为 *ID 的 cookie 值"""
        return P115Cookies(self.cookies)

    def _read_cookies(self, encoding: str = "latin-1", /):
        if cookies_path := self.__dict__.get("cookies_path"):
            try:
                with cookies_path.open("rb") as f:
                    cookies = str(f.read(), encoding)
                if cookies:
                    update_cookies(self.cookies, cookies_to_dict(cookies))
            except OSError:
                pass

    def _write_cookies(self, encoding: str = "latin-1", /):
        if cookies_path := self.__dict__.get("cookies_path"):
            cookies_bytes = bytes(self.cookies_str, encoding)
            with cookies_path.open("wb") as f:
                f.write(cookies_bytes)

    def update_cookies(
        self,
        cookies: None
        | str
        | CookieJar
        | BaseCookie
        | Mapping[str, Any]
        | Iterable[Any]
        | ClientRequestMixin = None,
        /,
    ):
        """更新 cookies（如果为 None 则是清空）"""
        if isinstance(cookies, ClientRequestMixin):
            cookies = cookies.cookies
        if cookies is None:
            self.cookies.clear()
        else:
            if isinstance(cookies, str):
                cookies = cookies_to_dict(cookies.strip().rstrip(";"))
            if cookies:
                update_cookies(self.cookies, cookies)
                self._write_cookies()

    def request(
        self,
        /,
        url: str,
        method: str = "GET",
        payload: Any = None,
        *,
        check: bool = False,
        ecdh_encrypt: bool = False,
        request: None | Callable = None,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ):
        """执行网络请求

        :param url:     HTTP 的请求链接
        :param method:  HTTP 的请求方法
        :param payload: HTTP 的请求载体（``method`` 为 "POST" 或 "PUT" 时，视为 ``data``，否则视为 ``params``）
        :param ecdh_encrypt: 是否加密通信，如果是 open 接口则无效
        :param check: 是否检查响应
        :param request: HTTP 请求调用，如果为 None，则用默认设置
            如果传入调用，则必须至少能接受以下几个关键词参数（如果接收到了不用的参数，也要能自动忽略）：

            - url:     HTTP 的请求链接
            - method:  HTTP 的请求方法
            - params:  HTTP 的请求链接附加的查询参数
            - data:    HTTP 的请求体
            - json:    JSON 数据（往往未被序列化）作为请求体
            - files:   要用 multipart 上传的若干文件
            - headers: HTTP 的请求头
            - follow_redirects: 是否跟进重定向，默认值为 True
            - raise_for_status: 是否对响应码 >= 400 时抛出异常
            - cookies: 至少能接受 ``http.cookiejar.CookieJar`` 和 ``http.cookies.BaseCookie``，会因响应头的 "set-cookie" 而更新
            - parse:   解析 HTTP 响应的方法，默认会构建一个 Callable，会把响应的字节数据视为 JSON 进行反序列化解析

                - 如果为 None，则直接把响应对象返回
                - 如果为 ...(Ellipsis)，则把响应对象关闭后将其返回
                - 如果为 True，则根据响应头来确定把响应得到的字节数据解析成何种格式（反序列化），请求也会被自动关闭
                - 如果为 False，则直接返回响应得到的字节数据，请求也会被自动关闭
                - 如果为 Callable，则使用此调用来解析数据，接受 1-2 个位置参数，并把解析结果返回给 `request` 的调用者，请求也会被自动关闭
                    - 如果只接受 1 个位置参数，则把响应对象传给它
                    - 如果能接受 2 个位置参数，则把响应对象和响应得到的字节数据（响应体）传给它

        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 直接返回 `request` 执行请求后的返回值

        .. note::
            `request` 可以由不同的请求库来提供，下面是封装了一些模块

            1. `httpcore_request <https://pypi.org/project/httpcore_request/>`_，由 `httpcore <https://pypi.org/project/httpcore/>`_ 封装，支持同步和异步请求

                .. code:: python

                    from httpcore_request import request

            2. `httpx_request <https://pypi.org/project/httpx_request/>`_，由 `httpx <https://pypi.org/project/httpx/>`_ 封装，支持同步和异步请求

                .. code:: python

                    from httpx_request import request

            3. `http_client_request <https://pypi.org/project/http_client_request/>`_，由 `http.client <https://docs.python.org/3/library/http.client.html>`_ 封装，支持同步请求

                .. code:: python

                    from http_client_request import request

            4. `python-urlopen <https://pypi.org/project/python-urlopen/>`_，由 `urllib.request.urlopen <https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen>`_ 封装，支持同步请求

                .. code:: python

                    from urlopen import request

            5. `urllib3_request <https://pypi.org/project/urllib3_request/>`_，由 `urllib3 <https://pypi.org/project/urllib3/>`_ 封装，支持同步请求

                .. code:: python

                    from urllib3_request import request

            6. `requests_request <https://pypi.org/project/requests_request/>`_，由 `requests <https://pypi.org/project/requests/>`_ 封装，支持同步请求

                .. code:: python

                    from requests_request import request

            7. `aiohttp_client_request <https://pypi.org/project/aiohttp_client_request/>`_，由 `aiohttp <https://pypi.org/project/aiohttp/>`_ 封装，支持异步请求

                .. code:: python

                    from aiohttp_client_request import request

            8. `blacksheep_client_request <https://pypi.org/project/blacksheep_client_request/>`_，由 `blacksheep <https://pypi.org/project/blacksheep/>`_ 封装，支持异步请求

                .. code:: python

                    from blacksheep_client_request import request

            9. `asks_request <https://pypi.org/project/asks_request/>`_，由 `asks <https://pypi.org/project/asks/>`_ 封装，支持异步请求

                .. code:: python

                    from asks_request import request

            10. `pycurl_request <https://pypi.org/project/pycurl_request/>`_，由 `pycurl <https://pypi.org/project/pycurl/>`_ 封装，支持同步请求

                .. code:: python

                    from pycurl_request import request

            11. `curl_cffi_request <https://pypi.org/project/curl_cffi_request/>`_，由 `curl_cffi <https://pypi.org/project/curl_cffi/>`_ 封装，支持同步和异步请求

                .. code:: python

                    from curl_cffi_request import request

            12. `aiosonic_request <https://pypi.org/project/aiosonic_request/>`_，由 `aiosonic <https://pypi.org/project/aiosonic/>`_ 封装，支持异步请求

                .. code:: python

                    from aiosonic_request import request

            13. `tornado_client_request <https://pypi.org/project/tornado_client_request/>`_，由 `tornado <https://www.tornadoweb.org/en/latest/httpclient.html>`_ 封装，支持同步和异步请求

                .. code:: python

                    from tornado_client_request import request

            14. `urllib3_future_request <https://pypi.org/project/urllib3_future_request/>`_，由 `urllib3.future <https://urllib3future.readthedocs.io/en/latest/>`_ 封装，支持同步和异步请求

                .. code:: python

                    from fundrives.pan115._request import request

            15. `niquests_request <https://pypi.org/project/niquests_request/>`_，由 `niquests <https://niquests.readthedocs.io/en/latest/>`_ 封装，支持同步和异步请求

                .. code:: python

                    from niquests_request import request
        """
        headers = self.headers.copy()
        headers.update(request_kwargs.pop("headers", None) or ())
        request, request_kwargs = get_request(
            url=url,
            method=method,
            payload=payload,
            headers=headers,
            ecdh_encrypt=ecdh_encrypt,
            request=request,
            **request_kwargs,
        )
        headers = request_kwargs["headers"]
        if URL(url).path.startswith("/open/"):
            if "authorization" not in headers:
                from .open_client import P115OpenClient

                assert isinstance(self, P115OpenClient)

                def gen_step():
                    if async_:
                        lock: Lock | AsyncLock = self.request_alock
                    else:
                        lock = self.request_lock
                    if not hasattr(self, "access_token"):
                        yield lock.acquire()
                        try:
                            if not getattr(self, "access_token", None):
                                if getattr(self, "refresh_token", None):
                                    yield self.refresh_access_token(async_=async_)
                                elif hasattr(self, "login_another_open"):
                                    yield self.login_another_open(
                                        replace=True, async_=async_
                                    )
                                else:
                                    raise RuntimeError("can't get access token")
                        finally:
                            lock.release()
                    while True:
                        access_token = self.access_token
                        headers["authorization"] = "Bearer " + access_token
                        resp = yield request(async_=async_, **request_kwargs)
                        if resp.get("errno") != 40140125:
                            if check:
                                return check_response(resp)
                            return resp
                        yield lock.acquire()
                        try:
                            if access_token == self.access_token:
                                yield self.refresh_access_token(async_=async_)
                        finally:
                            lock.release()

                return run_gen_step(gen_step, async_)
        elif "cookie" not in headers:
            request_kwargs["cookies"] = self.cookies
        resp = request(async_=async_, **request_kwargs)
        if check:
            return check_response(resp)
        return resp

    def open(
        self,
        url: str,
        /,
        start: int | str = 0,
        urlopen: None | Callable = None,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ):
        """打开下载链接，返回响应对象

        :param url: 下载链接
        :param start: 开始索引，从 0 开始
        :param async_: 是否异步
        :param request_kwargs: 其它请求参数

        :return: 响应对象
        """
        headers = request_kwargs["headers"] = dict(request_kwargs.get("headers") or ())
        headers.setdefault("user-agent", "")
        if isinstance(start, str):
            if not start.startswith("bytes="):
                start = "bytes=" + start
        elif start >= 0:
            start = f"bytes={start}-"
        else:
            start = f"bytes={start}"
        headers["range"] = start
        if isinstance(url, P115URL):
            headers.update(url.get("headers") or ())
        if urlopen is None:
            from fundrives.pan115._request import (
                request as urlopen,
            )
        urlopen = cast(Callable, urlopen)
        return urlopen(url, async_=async_, **request_kwargs)

    ########## App API ##########

    @overload
    @staticmethod
    def app_area_list(
        base_url: str | Callable[[], str] = "https://cdnres.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def app_area_list(
        base_url: str | Callable[[], str] = "https://cdnres.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def app_area_list(
        base_url: str | Callable[[], str] = "https://cdnres.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取地区编码列表

        GET https://cdnres.115.com/my/m_r/setting_new/js/ylmf_area.js
        """
        api = complete_url("/my/m_r/setting_new/js/ylmf_area.js", base_url=base_url)

        def iter_area(data: dict, /) -> Iterator[tuple[int, str]]:
            for code, detail in data.items():
                if isinstance(code, str):
                    continue
                if isinstance(detail, dict):
                    yield code, detail["n"]
                    for key in ("c", "t"):
                        if key in detail and detail[key]:
                            yield from iter_area(detail[key])
                            break
                else:
                    yield code, detail

        def parse(_, content, /):
            data_str = cast(Match[str], CRE_AREA_DATA_search(content.decode("utf-8")))[
                0
            ]
            data = eval(data_str, {"n": "n", "c": "c", "t": "t", "l": "l"})
            return {"state": True, "data": list(iter_area(data))}

        request_kwargs.setdefault("parse", parse)
        request, request_kwargs = get_request(url=api, **request_kwargs)
        return request(async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def app_face_codes(
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def app_face_codes(
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def app_face_codes(
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取表情包

        GET https://my.115.com/api/face_code.js
        """
        api = complete_url("/api/face_code.js", base_url=base_url)

        def parse(_, content, /):
            return json_loads(content[25:-1])

        request_kwargs.setdefault("parse", parse)
        request, request_kwargs = get_request(url=api, **request_kwargs)
        return request(async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def app_publick_key(
        app: str = "web",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def app_publick_key(
        app: str = "web",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def app_publick_key(
        app: str = "web",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 RSA 加密公钥，用于某些情况下的加密

        GET https://passportapi.115.com/app/1.0/{app}/1.0/login/getKey

        .. note::
            返回的公钥是签名证书，并经过 BASE64 处理，可用下面步骤还原

            .. code:: python

                from base64 import b64decode
                from fundrives.pan115 import P115Client

                resp = P115Client.app_publick_key()
                perm = b64decode(resp["data"]["key"])

                # pip install pycryptodome
                from Crypto.PublicKey import RSA

                pubkey = RSA.import_key(perm)
                print(repr(pubkey))
        """
        api = complete_url(f"/app/1.0/{app}/1.0/login/getKey", base_url=base_url)
        request, request_kwargs = get_request(url=api, **request_kwargs)
        return request(async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def app_version_list(
        base_url: str | Callable[[], str] = "https://appversion.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def app_version_list(
        base_url: str | Callable[[], str] = "https://appversion.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def app_version_list(
        base_url: str | Callable[[], str] = "https://appversion.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取当前各平台最新版 115 app 下载链接

        GET https://appversion.115.com/1.0/web/1.0/api/chrome
        """
        api = complete_url("/1.0/web/1.0/api/chrome", base_url=base_url)
        request, request_kwargs = get_request(url=api, **request_kwargs)
        return request(async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def app_version_list2(
        base_url: str | Callable[[], str] = "https://appversion.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def app_version_list2(
        base_url: str | Callable[[], str] = "https://appversion.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def app_version_list2(
        base_url: str | Callable[[], str] = "https://appversion.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取当前各平台最新版 115 app 下载链接

        GET https://appversion.115.com/1.0/web/1.0/api/getMultiVer
        """
        api = complete_url("/1.0/web/1.0/api/getMultiVer", base_url=base_url)
        request, request_kwargs = get_request(url=api, **request_kwargs)
        return request(async_=async_, **request_kwargs)

    ########## Qrcode API ##########

    @overload
    @staticmethod
    def login_authorize_open(
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def login_authorize_open(
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def login_authorize_open(
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """授权码方式请求开放接口应用授权

        GET https://qrcodeapi.115.com/open/authorize

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/okr2cq0wywelscpe#EiOrD

        .. note::
            同一个开放应用 id，最多同时有 3 个登入，如果有新的登录，则自动踢掉较早的那一个

        :payload:
            - client_id: int | str 💡 AppID
            - redirect_uri: str 💡 授权成功后重定向到指定的地址并附上授权码 code，需要先到 https://open.115.com/ 应用管理应用域名设置
            - response_type: str = "code" 💡 授权模式，固定为 code，表示授权码模式
            - state: int | str = <default> 💡 随机值，会通过 redirect_uri 原样返回，可用于验证以防 MITM 和 CSRF
        """
        api = complete_url("/open/authorize", base_url=base_url)
        request_kwargs["follow_redirects"] = False

        def parse(resp, content, /):
            if get_status_code(resp) == 302:
                return {
                    "state": True,
                    "url": resp.headers["location"],
                    "data": dict(parse_qsl(urlsplit(resp.headers["location"]).query)),
                    "headers": dict(resp.headers),
                }
            return json_maybe_decrypt_loads(content)

        request_kwargs.setdefault("parse", parse)
        request, request_kwargs = get_request(
            url=api, params={"response_type": "code", **payload}, **request_kwargs
        )
        return request(async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def login_authorize_access_token_open(
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def login_authorize_access_token_open(
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def login_authorize_access_token_open(
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """用授权码获取开放接口应用的 access_token

        POST https://qrcodeapi.115.com/open/authCodeToToken

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/okr2cq0wywelscpe#JnDgl

        :payload:
            - client_id: int | str 💡 AppID
            - client_secret: str 💡 AppSecret
            - code: str 💡 授权码，/open/authCodeToToken 重定向地址里面
            - redirect_uri: str 💡 与 /open/authCodeToToken 传的 redirect_uri 一致，可用于验证以防 MITM 和 CSRF
            - grant_type: str = "authorization_code" 💡 授权类型，固定为 authorization_code，表示授权码类型
        """
        api = complete_url("/open/authCodeToToken", base_url=base_url)
        request, request_kwargs = get_request(
            url=api,
            method="POST",
            data={"grant_type": "authorization_code", **payload},
            **request_kwargs,
        )
        return request(async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def login_qrcode(
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> bytes: ...
    @overload
    @staticmethod
    def login_qrcode(
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, bytes]: ...
    @staticmethod
    def login_qrcode(
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> bytes | Coroutine[Any, Any, bytes]:
        """下载登录二维码图片

        GET https://qrcodeapi.115.com/api/1.0/{app}/1.0/qrcode

        :param uid: 二维码的 uid

        :return: 图片的二进制数据（PNG 图片）
        """
        api = complete_url(f"/api/1.0/{app}/1.0/qrcode", base_url=base_url)
        if isinstance(payload, str):
            payload = {"uid": payload}
        request_kwargs.setdefault("parse", False)
        request, request_kwargs = get_request(url=api, **request_kwargs)
        return request(async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def login_qrcode_access_token_open(
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def login_qrcode_access_token_open(
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def login_qrcode_access_token_open(
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """绑定扫码并获取开放平台应用的 access_token 和 refresh_token

        POST https://qrcodeapi.115.com/open/deviceCodeToToken

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/shtpzfhewv5nag11#QCCVQ

        :payload:
            - uid: str
            - code_verifier: str = <default> 💡 默认字符串是 64 个 "0"
        """
        api = complete_url("/open/deviceCodeToToken", base_url=base_url)
        if isinstance(payload, str):
            payload = {"uid": payload, "code_verifier": _default_code_verifier}
        request, request_kwargs = get_request(
            url=api, method="POST", data=payload, **request_kwargs
        )
        return request(async_=async_, **request_kwargs)

    @overload
    def login_qrcode_scan(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def login_qrcode_scan(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def login_qrcode_scan(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """扫描二维码，payload 数据取自 `login_qrcode_token` 接口响应

        GET https://qrcodeapi.115.com/api/2.0/prompt.php

        :payload:
            - uid: str
        """
        api = complete_url("/api/2.0/prompt.php", base_url=base_url)
        if isinstance(payload, str):
            payload = {"uid": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def login_qrcode_scan_cancel(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def login_qrcode_scan_cancel(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def login_qrcode_scan_cancel(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """取消扫描二维码，payload 数据取自 `login_qrcode_scan` 接口响应

        GET https://qrcodeapi.115.com/api/2.0/cancel.php

        :payload:
            - key: str
            - uid: str
            - client: int = 0
        """
        api = complete_url("/api/2.0/cancel.php", base_url=base_url)
        if isinstance(payload, str):
            payload = {"key": payload, "uid": payload, "client": 0}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def login_qrcode_scan_confirm(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def login_qrcode_scan_confirm(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def login_qrcode_scan_confirm(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """确认扫描二维码，payload 数据取自 `login_qrcode_scan` 接口响应

        GET https://qrcodeapi.115.com/api/2.0/slogin.php

        :payload:
            - key: str
            - uid: str
            - client: int = 0
        """
        api = complete_url("/api/2.0/slogin.php", base_url=base_url)
        if isinstance(payload, str):
            payload = {"key": payload, "uid": payload, "client": 0}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def login_qrcode_scan_result(
        uid: str,
        app: str = "alipaymini",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def login_qrcode_scan_result(
        uid: str,
        app: str = "alipaymini",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def login_qrcode_scan_result(
        uid: str,
        app: str = "alipaymini",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取扫码登录的结果，包含 cookie

        POST https://qrcodeapi.115.com/app/1.0/{app}/1.0/login/qrcode/

        .. note::
            如果报错“IP登录异常”，那么要到次日零点才能解禁（用 VPN 可以绕过），其中尤其是 `app="web"` 最容易遇到此问题

        :param uid: 扫码的 uid
        :param app: 绑定的 app
        :param request: 自定义请求函数
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 接口返回值
        """
        if app == "desktop":
            app = "web"
        elif app in ("windows", "mac", "linux"):
            app = "os_" + app
        elif app in ("ios", "qios", "ipad", "qipad"):
            headers = request_kwargs["headers"] = dict(
                request_kwargs.get("headers", ())
            )
            match app:
                case "ios":
                    headers["user-agent"] = "UPhone/1.0.0"
                case "qios":
                    headers["user-agent"] = "OfficePhone/1.0.0"
                case "ipad":
                    headers["user-agent"] = "UPad/1.0.0"
                case "qipad":
                    headers["user-agent"] = "OfficePad/1.0.0"
            app = "ios"
        api = complete_url(f"/app/1.0/{app}/1.0/login/qrcode/", base_url=base_url)
        request, request_kwargs = get_request(
            url=api, method="POST", data={"account": uid}, **request_kwargs
        )
        return request(async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def login_qrcode_scan_status(
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def login_qrcode_scan_status(
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def login_qrcode_scan_status(
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取二维码的状态（未扫描、已扫描、已登录、已取消、已过期等），payload 数据取自 `login_qrcode_token` 接口响应

        GET https://qrcodeapi.115.com/get/status/

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/shtpzfhewv5nag11#lAsp2

        :payload:
            - uid: str
            - time: int
            - sign: str
        """
        api = complete_url("/get/status/", base_url=base_url)
        request, request_kwargs = get_request(url=api, params=payload, **request_kwargs)
        return request(async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def login_qrcode_token(
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def login_qrcode_token(
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def login_qrcode_token(
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取登录二维码，扫码可用

        GET https://qrcodeapi.115.com/api/1.0/{app}/1.0/token/
        """
        api = complete_url(f"/api/1.0/{app}/1.0/token/", base_url=base_url)
        request, request_kwargs = get_request(url=api, **request_kwargs)
        return request(async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def login_qrcode_token_open(
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def login_qrcode_token_open(
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def login_qrcode_token_open(
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取开放平台的登录二维码，扫码可用，采用 PKCE (Proof Key for Code Exchange)

        POST https://qrcodeapi.115.com/open/authDeviceCode

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/shtpzfhewv5nag11#WzRhM

        .. tip::
            此接口也可用于检测 app_id 是否可用

        .. note::
            同一个开放应用 id，最多同时有 3 个登入，如果有新的登录，则自动踢掉较早的那一个

        .. note::
            code_challenge 默认用的字符串为 64 个 0，hash 算法为 md5

        .. tip::
            如果仅仅想要检查 AppID 是否有效，可以用如下的代码：

            .. code:: python

                from fundrives.pan115 import P115Client

                app_id = 100195125
                response = P115Client.login_qrcode_token_open(app_id)
                if response["code"]:
                    print("无效 AppID:", app_id, "因为:", response["error"])
                else:
                    print("有效 AppID:", app_id)

        .. tip::
            如果想要罗列出所有可用的 AppID，可以用如下的代码：

            .. code:: python

                from itertools import count
                from fundrives.pan115 import P115Client

                get_qrcode_token = P115Client.login_qrcode_token_open
                for app_id in count(100195125, 2):
                    response = get_qrcode_token(app_id)
                    if not response["code"]:
                        print(app_id)

        :payload:
            - client_id: int | str 💡 AppID
            - code_challenge: str = <default> 💡 PKCE 相关参数，计算方式如下

                .. code:: python

                    from base64 import b64encode
                    from hashlib import sha256
                    from secrets import token_bytes

                    # code_verifier 可以是 43~128 位随机字符串
                    code_verifier = token_bytes(64).hex()
                    code_challenge = b64encode(sha256(code_verifier.encode()).digest()).decode()

            - code_challenge_method: str = <default> 💡 计算 `code_challenge` 的 hash 算法，支持 "md5", "sha1", "sha256"
        """
        api = complete_url("/open/authDeviceCode", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {
                "client_id": payload,
                "code_challenge": _default_code_challenge,
                "code_challenge_method": _default_code_challenge_method,
            }
        request, request_kwargs = get_request(
            url=api, method="POST", data=payload, **request_kwargs
        )
        return request(async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def login_refresh_token_open(
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def login_refresh_token_open(
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def login_refresh_token_open(
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """用一个 refresh_token 去获取新的 access_token 和 refresh_token，然后原来的 refresh_token 作废

        POST https://qrcodeapi.115.com/open/refreshToken

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/shtpzfhewv5nag11#ve54x

            https://www.yuque.com/115yun/open/opnx8yezo4at2be6

        :payload:
            - refresh_token: str
        """
        api = complete_url("/open/refreshToken", base_url=base_url)
        if isinstance(payload, str):
            payload = {"refresh_token": payload}
        request, request_kwargs = get_request(
            url=api, method="POST", data=payload, **request_kwargs
        )
        return request(async_=async_, **request_kwargs)

    @overload
    @classmethod
    def login_with_qrcode(
        cls,
        /,
        app: None | str = "",
        console_qrcode: bool = True,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @classmethod
    def login_with_qrcode(
        cls,
        /,
        app: None | str = "",
        console_qrcode: bool = True,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @classmethod
    def login_with_qrcode(
        cls,
        /,
        app: None | str = "",
        console_qrcode: bool = True,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """二维码扫码登录

        .. hint::
            仅获取响应，如果需要更新此 `client` 的 `cookies`，请直接用 `login` 方法

        :param app: 扫二维码后绑定的 `app` （或者叫 `device`）
        :param console_qrcode: 在命令行输出二维码，否则在浏览器中打开
        :param base_url: 接口的基地址
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 响应信息，如果 `app` 为 None 或 ""，则返回二维码信息，否则返回绑定扫码后的信息（包含 cookies）

        -----

        :设备列表如下:

        +-------+----------+------------+----------------------+
        | No.   | ssoent   | app        | description          |
        +=======+==========+============+======================+
        | 01    | A1       | web        | 115生活_网页端       |
        +-------+----------+------------+----------------------+
        | --    | A1       | desktop    | 115浏览器            |
        +-------+----------+------------+----------------------+
        | --    | A2       | ?          | 未知: android        |
        +-------+----------+------------+----------------------+
        | --    | A3       | ?          | 未知: ios            |
        +-------+----------+------------+----------------------+
        | --    | A4       | ?          | 未知: ipad           |
        +-------+----------+------------+----------------------+
        | --    | B1       | ?          | 未知: android        |
        +-------+----------+------------+----------------------+
        | 02    | D1       | ios        | 115生活_苹果端       |
        +-------+----------+------------+----------------------+
        | 03    | D2       | bios       | 未知: ios            |
        +-------+----------+------------+----------------------+
        | 04    | D3       | 115ios     | 115_苹果端           |
        +-------+----------+------------+----------------------+
        | 05    | F1       | android    | 115生活_安卓端       |
        +-------+----------+------------+----------------------+
        | 06    | F2       | bandroid   | 未知: android        |
        +-------+----------+------------+----------------------+
        | 07    | F3       | 115android | 115_安卓端           |
        +-------+----------+------------+----------------------+
        | 08    | H1       | ipad       | 115生活_苹果平板端   |
        +-------+----------+------------+----------------------+
        | 09    | H2       | bipad      | 未知: ipad           |
        +-------+----------+------------+----------------------+
        | 10    | H3       | 115ipad    | 115_苹果平板端       |
        +-------+----------+------------+----------------------+
        | 11    | I1       | tv         | 115生活_安卓电视端   |
        +-------+----------+------------+----------------------+
        | 12    | I2       | apple_tv   | 115生活_苹果电视端   |
        +-------+----------+------------+----------------------+
        | 13    | M1       | qandriod   | 115管理_安卓端       |
        +-------+----------+------------+----------------------+
        | 14    | N1       | qios       | 115管理_苹果端       |
        +-------+----------+------------+----------------------+
        | 15    | O1       | qipad      | 115管理_苹果平板端   |
        +-------+----------+------------+----------------------+
        | 16    | P1       | os_windows | 115生活_Windows端    |
        +-------+----------+------------+----------------------+
        | 17    | P2       | os_mac     | 115生活_macOS端      |
        +-------+----------+------------+----------------------+
        | 18    | P3       | os_linux   | 115生活_Linux端      |
        +-------+----------+------------+----------------------+
        | 19    | R1       | wechatmini | 115生活_微信小程序端 |
        +-------+----------+------------+----------------------+
        | 20    | R2       | alipaymini | 115生活_支付宝小程序 |
        +-------+----------+------------+----------------------+
        | 21    | S1       | harmony    | 115_鸿蒙端           |
        +-------+----------+------------+----------------------+
        """

        def gen_step():
            nonlocal console_qrcode
            resp = yield cls.login_qrcode_token(
                async_=async_,
                base_url=base_url,
                **request_kwargs,
            )
            qrcode_token = resp["data"]
            login_uid = qrcode_token["uid"]
            qrcode = qrcode_token.pop("qrcode", "")
            if not qrcode:
                qrcode = "https://115.com/scan/dg-" + login_uid
            if not console_qrcode:
                try:
                    from fundrives.pan115._utils import (
                        startfile,
                        startfile_async,
                    )
                except ImportError:
                    console_qrcode = True
            if console_qrcode:
                from qrcode import QRCode  # type: ignore

                qr = QRCode(border=1)
                qr.add_data(qrcode)
                qr.print_ascii(tty=isatty(1))
            else:
                url = complete_url(
                    "/api/1.0/web/1.0/qrcode",
                    base_url=base_url,
                    query={"uid": login_uid},
                )
                if async_:
                    yield startfile_async(url)
                else:
                    startfile(url)
            while True:
                try:
                    resp = yield cls.login_qrcode_scan_status(
                        qrcode_token,
                        base_url=base_url,
                        async_=async_,
                        **request_kwargs,
                    )
                except Exception:
                    continue
                match resp["data"].get("status"):
                    case 0:
                        print("[status=0] qrcode: waiting")
                    case 1:
                        print("[status=1] qrcode: scanned")
                    case 2:
                        print("[status=2] qrcode: signed in")
                        break
                    case -1:
                        raise P115LoginError(errno.EAUTH, "[status=-1] qrcode: expired")
                    case -2:
                        raise P115LoginError(
                            errno.EAUTH, "[status=-2] qrcode: canceled"
                        )
                    case _:
                        raise P115LoginError(
                            errno.EAUTH, f"qrcode: aborted with {resp!r}"
                        )
            if app:
                return cls.login_qrcode_scan_result(
                    login_uid,
                    app=app,
                    base_url=base_url,
                    async_=async_,
                    **request_kwargs,
                )
            else:
                return qrcode_token

        return run_gen_step(gen_step, async_)

    @overload
    @classmethod
    def login_with_app_id(
        cls,
        /,
        app_id: int,
        console_qrcode: bool = True,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @classmethod
    def login_with_app_id(
        cls,
        /,
        app_id: int,
        console_qrcode: bool = True,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @classmethod
    def login_with_app_id(
        cls,
        /,
        app_id: int,
        console_qrcode: bool = True,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """二维码扫码登录开放平台

        :param console_qrcode: 在命令行输出二维码，否则在浏览器中打开
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 响应信息
        """

        def gen_step():
            nonlocal console_qrcode
            resp = yield cls.login_qrcode_token_open(
                app_id,
                base_url=base_url,
                async_=async_,
                **request_kwargs,
            )
            qrcode_token = resp["data"]
            login_uid = qrcode_token["uid"]
            qrcode = qrcode_token.pop("qrcode", "")
            if not qrcode:
                qrcode = "https://115.com/scan/dg-" + login_uid
            if not console_qrcode:
                try:
                    from fundrives.pan115._utils import (
                        startfile,
                        startfile_async,
                    )
                except ImportError:
                    console_qrcode = True
            if console_qrcode:
                from qrcode import QRCode  # type: ignore

                qr = QRCode(border=1)
                qr.add_data(qrcode)
                qr.print_ascii(tty=isatty(1))
            else:
                url = complete_url(
                    "/api/1.0/web/1.0/qrcode",
                    base_url=base_url,
                    query={"uid": login_uid},
                )
                if async_:
                    yield startfile_async(url)
                else:
                    startfile(url)
            while True:
                try:
                    resp = yield cls.login_qrcode_scan_status(
                        qrcode_token,
                        base_url=base_url,
                        async_=async_,
                        **request_kwargs,
                    )
                except Exception:
                    continue
                match resp["data"].get("status"):
                    case 0:
                        print("[status=0] qrcode: waiting")
                    case 1:
                        print("[status=1] qrcode: scanned")
                    case 2:
                        print("[status=2] qrcode: signed in")
                        break
                    case -1:
                        raise P115LoginError(errno.EAUTH, "[status=-1] qrcode: expired")
                    case -2:
                        raise P115LoginError(
                            errno.EAUTH, "[status=-2] qrcode: canceled"
                        )
                    case _:
                        raise P115LoginError(
                            errno.EAUTH, f"qrcode: aborted with {resp!r}"
                        )
            return cls.login_qrcode_access_token_open(
                login_uid,
                base_url=base_url,
                async_=async_,
                **request_kwargs,
            )

        return run_gen_step(gen_step, async_)

    ########## Upload API ##########

    @overload
    @staticmethod
    def upload_gettoken(
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def upload_gettoken(
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def upload_gettoken(
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取阿里云 OSS 的 token（上传凭证）

        GET https://uplb.115.com/3.0/gettoken.php
        """
        api = complete_url("/3.0/gettoken.php", base_url=base_url)
        request, request_kwargs = get_request(url=api, **request_kwargs)
        return request(async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def upload_url(
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    @staticmethod
    def upload_url(
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    @staticmethod
    def upload_url(
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取用于上传的一些 http 接口，此接口具有一定幂等性，请求一次，然后把响应记下来即可

        GET https://uplb.115.com/3.0/getuploadinfo.php

        :response:
            - endpoint: 此接口用于上传文件到阿里云 OSS
            - gettokenurl: 上传前需要用此接口获取 token
        """
        api = complete_url("/3.0/getuploadinfo.php", base_url=base_url)
        request, request_kwargs = get_request(url=api, **request_kwargs)
        return request(async_=async_, **request_kwargs)


import sys as _sys


def _rsa_decrypt(cipher: Any, /) -> bytes:
    client_pkg = _sys.modules.get("fundrives.pan115.client")
    fn = (
        getattr(client_pkg, "rsa_decrypt", rsa_decrypt)
        if client_pkg is not None
        else rsa_decrypt
    )
    return fn(cipher)
