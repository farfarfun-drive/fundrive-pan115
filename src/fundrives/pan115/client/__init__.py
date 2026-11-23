#!/usr/bin/env python3

from __future__ import annotations

__all__ = ["check_response", "P115OpenClient", "P115Client"]
__doc__ = "115 客户端模块"

from typing import Any, Literal, overload

from ._common import (
    CLIENT_API_METHODS_MAP,
    CLIENT_METHOD_API_MAP,
    CRE_SET_COOKIE,
    MULTILINE,
    P115URL,
    SSOENT_TO_APP,
    URL,
    AsyncHTTPFileReader,
    AsyncIterable,
    AsyncLock,
    Awaitable,
    BaseCookie,
    Buffer,
    Callable,
    ClientRequestMixin,
    Cookie,
    CookieJar,
    Coroutine,
    CRE_AREA_DATA_search,
    CRE_COOKIES_UID_search,
    HTTPFileReader,
    Iterable,
    Iterator,
    KeyLowerDict,
    Lock,
    Mapping,
    Match,
    Morsel,
    MutableMapping,
    P115AccessTokenError,
    P115AuthenticationError,
    P115Cookies,
    P115DownloadFileNotFoundError,
    P115LoginError,
    P115OpenAppAuthLimitExceeded,
    P115OperationalError,
    P115OSError,
    P115Warning,
    Path,
    PathLike,
    PurePath,
    Sequence,
    SupportsGeturl,
    SupportsRead,
    UserString,
    _app_version,
    _default_code_challenge,
    _default_code_challenge_method,
    _default_code_verifier,
    _default_k_ec,
    _rsa_decrypt,
    b64encode,
    check_response,
    complete_url,
    content_maybe_decrypt,
    cookies_to_dict,
    date,
    datetime,
    dict_key_to_lower_merge,
    dict_update,
    digits,
    dumps,
    ecdh_aes_decrypt,
    ecdh_aes_encrypt,
    ecdh_encode_token,
    ensure_async,
    ensure_bytes,
    errno,
    expand_payload,
    fsdecode,
    get_first,
    get_request,
    get_status_code,
    isatty,
    isawaitable,
    itemgetter,
    iter_items,
    json_decrypt_loads,
    json_decrypt_parse,
    json_loads,
    json_maybe_decrypt_loads,
    json_maybe_decrypt_parse,
    json_parse,
    loads,
    locked_cacheproperty,
    make_upload_payload,
    make_url,
    md5,
    md5_secret_password,
    normalize_pickcode,
    parse_qsl,
    parse_upload_init_response,
    quote,
    re_compile,
    rsa_decrypt,
    rsa_encrypt,
    run_gen_step,
    sha1,
    share_extract_payload,
    throw,
    time,
    timedelta,
    to_bytes_view,
    to_id,
    to_pickcode,
    unquote,
    update_cookies,
    upload_file,
    urlencode,
    urlsplit,
    uuid4,
    warn,
)
from .account_mixin import _P115ClientAccountMixin
from .extra_mixin import _P115ClientExtraMixin
from .fs_mixin import _P115ClientFsMixin
from .open_client import P115OpenClient
from .share_mixin import _P115ClientShareMixin
from .transfer_mixin import _P115ClientTransferMixin


class P115Client(
    _P115ClientFsMixin,
    _P115ClientTransferMixin,
    _P115ClientShareMixin,
    _P115ClientAccountMixin,
    _P115ClientExtraMixin,
    P115OpenClient,
):
    """115 的客户端对象

    .. note::
        目前允许 1 个用户同时登录多个开放平台应用（用 AppID 区别），也允许多次授权登录同 1 个应用

        同一个开放应用 id，最多同时有 3 个登入，如果有新的登录，则自动踢掉较早的那一个

        目前不允许短时间内再次用 ``refresh_token`` 刷新 ``access_token``，但你可以用登录的方式再次授权登录以获取 ``access_token``，即可不受频率限制

        1 个 ``refresh_token`` 只能使用 1 次，可获取新的 ``refresh_token`` 和 ``access_token``，如果请求刷新时，发送成功但读取失败，可能导致 ``refresh_token`` 报废，这时需要重新授权登录

    :param cookies: 115 的 cookies，要包含 ``UID``、``CID``、``KID`` 和 ``SEID`` 等

        - 如果是 None，则会要求人工扫二维码登录
        - 如果是 str，则要求是格式正确的 cookies 字符串，例如 "UID=...; CID=...; KID=...; SEID=..."
        - 如果是 bytes 或 os.PathLike，则视为路径，当更新 cookies 时，也会往此路径写入文件，格式要求同上面的 `str`
        - 如果是 collections.abc.Mapping，则是一堆 cookie 的名称到值的映射
        - 如果是 collections.abc.Iterable，则其中每一条都视为单个 cookie

    :param app: 重新登录时人工扫二维码后绑定的 `app` （或者叫 `device`），如果不指定，则根据 cookies 的 UID 字段来确定，如果不能确定，则用 "qandroid"
    :param app_id: 授权的 open 应用的 AppID
    :param console_qrcode: 在命令行输出二维码，否则在浏览器中打开

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

    def __init__(
        self,
        /,
        cookies: None
        | str
        | PathLike
        | Mapping[str, str]
        | Iterable[Mapping | Cookie | Morsel] = None,
        app: str = "",
        app_id: int = 0,
        console_qrcode: bool = True,
    ):
        self.init(
            cookies=cookies,
            app=app,
            app_id=app_id,
            console_qrcode=console_qrcode,
            instance=self,
        )

    def __repr__(self, /) -> str:
        cls = type(self)
        try:
            user_id = self.user_id
        except LookupError:
            user_id = 0
        return f"<{cls.__module__}.{cls.__qualname__}(user_id={user_id}, app={self.login_app()!r}, app_id={self.app_id}) at {hex(id(self))}>"

    @classmethod
    def from_path(
        cls,
        /,
        path: bytes | str | PathLike = Path("~/115-cookies.txt").expanduser(),
        app_id: int = 0,
    ) -> P115Client:
        if not isinstance(path, PurePath):
            path = Path(fsdecode(path))
        return cls(path, app_id=app_id)

    @locked_cacheproperty
    def user_key(self, /) -> str:
        from ..util import get_user_key, set_user_key

        try:
            return get_user_key(self.user_id)
        except KeyError:
            resp = self.upload_info()
            check_response(resp)
            return set_user_key(self.user_id, resp["userkey"])

    @overload
    def login_status(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> bool: ...

    @overload
    def login_status(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, bool]: ...

    def login_status(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> bool | Coroutine[Any, Any, bool]:
        """检查是否已登录

        GET https://my.115.com/?ct=guide&ac=status
        """
        api = complete_url(base_url=base_url, query={"ct": "guide", "ac": "status"})

        def parse(_, content: bytes, /) -> bool:
            try:
                return json_maybe_decrypt_loads(content)["state"]
            except:
                return False

        request_kwargs.setdefault("parse", parse)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def get_fs(
        self,
        arg: None = None,
        /,
        refresh: bool = False,
        id_to_readdir: None | int | dict[int, dict[int, MutableMapping]] = None,
    ) -> P115FileSystem: ...

    @overload
    def get_fs(
        self,
        arg: int,
        /,
        refresh: bool = False,
        id_to_readdir: None | int | dict[int, dict[int, MutableMapping]] = None,
    ) -> P115ZipFileSystem: ...

    @overload
    def get_fs(
        self,
        arg: str,
        /,
        refresh: bool = False,
        id_to_readdir: None | int | dict[int, dict[int, MutableMapping]] = None,
    ) -> P115ShareFileSystem: ...

    def get_fs(
        self,
        arg: None | int | str = None,
        /,
        refresh: bool = False,
        id_to_readdir: None | int | dict[int, dict[int, MutableMapping]] = None,
    ) -> P115FileSystemBase:
        if arg is None:
            return P115FileSystem(self, refresh=refresh, id_to_readdir=id_to_readdir)
        if isinstance(arg, int):
            return P115ZipFileSystem(
                self,
                self.to_pickcode(arg),
                refresh=refresh,
                id_to_readdir=id_to_readdir,
            )
        return P115ShareFileSystem(
            self, arg, refresh=refresh, id_to_readdir=id_to_readdir
        )


def _populate_client_api_maps() -> None:
    cre_search = re_compile(r"^ *((?:GET|POST|PUT|DELETE|PATCH) +.+)", MULTILINE).search
    for name in dir(P115Client):
        method = getattr(P115Client, name)
        if not (callable(method) and method.__doc__):
            continue
        if match := cre_search(method.__doc__):
            api = match[1]
            full_name = "P115Client." + name
            CLIENT_METHOD_API_MAP[full_name] = api
            CLIENT_API_METHODS_MAP.setdefault(api, []).append(full_name)


_populate_client_api_maps()


from ..fs import (
    P115FileSystem,
    P115FileSystemBase,
    P115ShareFileSystem,
    P115ZipFileSystem,
)
