#!/usr/bin/env python3

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Self, cast, overload

if TYPE_CHECKING:
    from . import P115Client

from ._common import (
    URL,
    AsyncHTTPFileReader,
    AsyncIterable,
    Buffer,
    Callable,
    Cookie,
    Coroutine,
    HTTPFileReader,
    Iterable,
    Mapping,
    Morsel,
    P115AuthenticationError,
    Path,
    PathLike,
    PurePath,
    Sequence,
    SupportsGeturl,
    SupportsRead,
    _app_version,
    _rsa_decrypt,
    check_response,
    complete_url,
    date,
    datetime,
    dumps,
    expand_payload,
    fsdecode,
    json_loads,
    json_maybe_decrypt_loads,
    rsa_encrypt,
    run_gen_step,
    sha1,
    time,
    unquote,
    upload_file,
    urlsplit,
)


class _P115ClientExtraMixin:
    """媒体、相册、笔记、生活事件与扩展接口混入。"""

    @overload  # type: ignore
    @classmethod
    def init(
        cls,
        /,
        cookies: None
        | str
        | PathLike
        | Mapping[str, str]
        | Iterable[Mapping | Cookie | Morsel] = None,
        app: str = "",
        app_id: int = 0,
        console_qrcode: bool = True,
        instance: None | Self = None,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> P115Client: ...

    @overload
    @classmethod
    def init(
        cls,
        /,
        cookies: None
        | str
        | PathLike
        | Mapping[str, str]
        | Iterable[Mapping | Cookie | Morsel] = None,
        app: str = "",
        app_id: int = 0,
        console_qrcode: bool = True,
        instance: None | Self = None,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, P115Client]: ...

    @classmethod
    def init(
        cls,
        /,
        cookies: None
        | str
        | PathLike
        | Mapping[str, str]
        | Iterable[Mapping | Cookie | Morsel] = None,
        app: str = "",
        app_id: int = 0,
        console_qrcode: bool = True,
        instance: None | Self = None,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> P115Client | Coroutine[Any, Any, P115Client]:
        def gen_step():
            if instance is None:
                self = cls.__new__(cls)
            else:
                self = instance
            self.app_id = app_id
            if cookies is None:
                yield self.login(
                    app or "alipaymini",
                    console_qrcode=console_qrcode,
                    async_=async_,
                    **request_kwargs,
                )
            elif isinstance(cookies, PathLike):
                if isinstance(cookies, PurePath) and hasattr(cookies, "open"):
                    self.cookies_path = cookies
                else:
                    self.cookies_path = Path(fsdecode(cookies))
                self._read_cookies()
            elif cookies:
                self.update_cookies(cookies)
            return self

        return run_gen_step(gen_step, async_)

    @overload
    def login(
        self,
        /,
        app: None | str = None,
        console_qrcode: bool = True,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> Self: ...

    @overload
    def login(
        self,
        /,
        app: None | str = None,
        console_qrcode: bool = True,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, Self]: ...

    def login(
        self,
        /,
        app: None | str = None,
        console_qrcode: bool = True,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> Self | Coroutine[Any, Any, Self]:
        """扫码二维码登录，如果已登录则忽略

        :param app: 扫二维码后绑定的 `app` （或者叫 `device`），如果不指定，则根据 cookies 的 UID 字段来确定，如果不能确定，则用 "qandroid"
        :param console_qrcode: 在命令行输出二维码，否则在浏览器中打开
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 返回对象本身

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
            nonlocal app
            status = yield self.login_status(async_=async_, **request_kwargs)
            if status:
                return self
            if not app:
                app = yield self.login_app(async_=async_, **request_kwargs)
            if not app:
                app = "alipaymini"
            resp = yield self.login_with_qrcode(
                app,
                console_qrcode=console_qrcode,
                async_=async_,
                **request_kwargs,
            )
            while True:
                try:
                    check_response(resp)
                    break
                except P115AuthenticationError:
                    print("login error:", resp)
                    resp = yield self.login_with_qrcode(
                        app,
                        console_qrcode=console_qrcode,
                        async_=async_,
                        **request_kwargs,
                    )
            self.update_cookies(resp["data"]["cookie"])
            return self

        return run_gen_step(gen_step, async_)

    @overload
    def act_xys_adopt(
        self,
        payload: dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def act_xys_adopt(
        self,
        payload: dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def act_xys_adopt(
        self,
        payload: dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """采纳助愿

        POST https://act.115.com/api/1.0/{app}/1.0/act2024xys/adopt

        :payload:
            - did: str 💡 许愿的 id
            - aid: int | str 💡 助愿的 id
            - to_cid: int = <default> 💡 助愿中的分享链接转存到你的网盘中目录的 id
        """
        api = complete_url(f"/api/1.0/{app}/1.0/act2024xys/adopt", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def act_xys_aid_desire(
        self,
        payload: dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def act_xys_aid_desire(
        self,
        payload: dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def act_xys_aid_desire(
        self,
        payload: dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """创建助愿（如果提供 file_ids，则会创建一个分享链接）

        POST https://act.115.com/api/1.0/{app}/1.0/act2024xys/aid_desire

        :payload:
            - id: str 💡 许愿 id
            - content: str 💡 助愿文本，不少于 5 个字，不超过 500 个字
            - images: int | str = <default> 💡 图片文件在你的网盘的 id，多个用逗号 "," 隔开
            - file_ids: int | str = <default> 💡 文件在你的网盘的 id，多个用逗号 "," 隔开
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/act2024xys/aid_desire", base_url=base_url
        )
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def act_xys_aid_desire_del(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def act_xys_aid_desire_del(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def act_xys_aid_desire_del(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除助愿

        POST https://act.115.com/api/1.0/{app}/1.0/act2024xys/del_aid_desire

        :payload:
            - ids: int | str 💡 助愿的 id，多个用逗号 "," 隔开
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/act2024xys/del_aid_desire", base_url=base_url
        )
        if isinstance(payload, (int, str)):
            payload = {"ids": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def act_xys_desire_aid_list(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def act_xys_desire_aid_list(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def act_xys_desire_aid_list(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取许愿的助愿列表

        GET https://act.115.com/api/1.0/{app}/1.0/act2024xys/desire_aid_list

        :payload:
            - id: str         💡 许愿的 id
            - start: int = 0  💡 开始索引
            - page: int = 1   💡 第几页
            - limit: int = 10 💡 分页大小
            - sort: int | str = <default> 💡 排序
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/act2024xys/desire_aid_list", base_url=base_url
        )
        if isinstance(payload, str):
            payload = {"id": payload}
        payload = {"start": 0, "page": 1, "limit": 10, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def act_xys_get_act_info(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def act_xys_get_act_info(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def act_xys_get_act_info(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取许愿树活动的信息

        GET https://act.115.com/api/1.0/{app}/1.0/act2024xys/get_act_info
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/act2024xys/get_act_info", base_url=base_url
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def act_xys_get_desire_info(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def act_xys_get_desire_info(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def act_xys_get_desire_info(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取的许愿信息

        GET https://act.115.com/api/1.0/{app}/1.0/act2024xys/get_desire_info

        :payload:
            - id: str 💡 许愿的 id
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/act2024xys/get_desire_info", base_url=base_url
        )
        if isinstance(payload, str):
            payload = {"id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def act_xys_home_list(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def act_xys_home_list(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def act_xys_home_list(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """首页的许愿树（随机刷新 15 条）

        GET https://act.115.com/api/1.0/{app}/1.0/act2024xys/home_list
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/act2024xys/home_list", base_url=base_url
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def act_xys_my_aid_desire(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def act_xys_my_aid_desire(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def act_xys_my_aid_desire(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我的助愿列表

        GET https://act.115.com/api/1.0/{app}/1.0/act2024xys/my_aid_desire

        :payload:
            - type: 0 | 1 | 2 = 0 💡 类型

                - 0: 全部
                - 1: 进行中
                - 2: 已实现

            - start: int = 0  💡 开始索引
            - page: int = 1   💡 第几页
            - limit: int = 10 💡 分页大小
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/act2024xys/my_aid_desire", base_url=base_url
        )
        if isinstance(payload, (int, str)):
            payload = {"type": payload}
        payload = {"type": 0, "start": 0, "page": 1, "limit": 10, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def act_xys_my_desire(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def act_xys_my_desire(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def act_xys_my_desire(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我的许愿列表

        GET https://act.115.com/api/1.0/{app}/1.0/act2024xys/my_desire

        :payload:
            - type: 0 | 1 | 2 = 0 💡 类型

                - 0: 全部
                - 1: 进行中
                - 2: 已实现

            - start: int = 0  💡 开始索引
            - page: int = 1   💡 第几页
            - limit: int = 10 💡 分页大小
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/act2024xys/my_desire", base_url=base_url
        )
        if isinstance(payload, (int, str)):
            payload = {"type": payload}
        payload = {"type": 0, "start": 0, "page": 1, "limit": 10, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def act_xys_wish(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def act_xys_wish(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def act_xys_wish(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """创建许愿

        POST https://act.115.com/api/1.0/{app}/1.0/act2024xys/wish

        :payload:
            - content: str 💡 许愿文本，不少于 5 个字，不超过 500 个字
            - rewardSpace: int = 5 💡 奖励容量，单位是 GB
            - images: int | str = <default> 💡 图片文件在你的网盘的 id，多个用逗号 "," 隔开
        """
        api = complete_url(f"/api/1.0/{app}/1.0/act2024xys/wish", base_url=base_url)
        if isinstance(payload, str):
            payload = {"content": payload}
        payload.setdefault("rewardSpace", 5)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def act_xys_wish_del(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def act_xys_wish_del(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def act_xys_wish_del(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://act.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除许愿

        POST https://act.115.com/api/1.0/{app}/1.0/act2024xys/del_wish

        :payload:
            - ids: str 💡 许愿的 id，多个用逗号 "," 隔开
        """
        api = complete_url(f"/api/1.0/{app}/1.0/act2024xys/del_wish", base_url=base_url)
        if isinstance(payload, str):
            payload = {"ids": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def captcha_all(
        self,
        /,
        base_url: str | Callable[[], str] = "https://captchaapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> bytes: ...

    @overload
    def captcha_all(
        self,
        /,
        base_url: str | Callable[[], str] = "https://captchaapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, bytes]: ...

    def captcha_all(
        self,
        /,
        base_url: str | Callable[[], str] = "https://captchaapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> bytes | Coroutine[Any, Any, bytes]:
        """返回一张包含 10 个汉字的图片，包含验证码中 4 个汉字（有相应的编号，从 0 到 9，计数按照从左到右，从上到下的顺序）

        GET https://captchaapi.115.com/?ct=index&ac=code&t=all
        """
        api = complete_url(
            base_url=base_url, query={"ct": "index", "ac": "code", "t": "all"}
        )
        request_kwargs.setdefault("parse", False)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def captcha_code(
        self,
        /,
        base_url: str | Callable[[], str] = "https://captchaapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> bytes: ...

    @overload
    def captcha_code(
        self,
        /,
        base_url: str | Callable[[], str] = "https://captchaapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, bytes]: ...

    def captcha_code(
        self,
        /,
        base_url: str | Callable[[], str] = "https://captchaapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> bytes | Coroutine[Any, Any, bytes]:
        """更新验证码，并获取图片数据（含 4 个汉字）

        GET https://captchaapi.115.com/?ct=index&ac=code
        """
        api = complete_url(base_url=base_url, query={"ct": "index", "ac": "code"})
        request_kwargs.setdefault("parse", False)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def captcha_sign(
        self,
        /,
        base_url: str | Callable[[], str] = "https://captchaapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def captcha_sign(
        self,
        /,
        base_url: str | Callable[[], str] = "https://captchaapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def captcha_sign(
        self,
        /,
        base_url: str | Callable[[], str] = "https://captchaapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取验证码的签名字符串

        GET https://captchaapi.115.com/?ac=code&t=sign
        """
        api = complete_url(base_url=base_url, query={"ac": "code", "t": "sign"})
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def captcha_single(
        self,
        payload: dict | int = 0,
        /,
        base_url: str | Callable[[], str] = "https://captchaapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> bytes: ...

    @overload
    def captcha_single(
        self,
        payload: dict | int = 0,
        /,
        base_url: str | Callable[[], str] = "https://captchaapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, bytes]: ...

    def captcha_single(
        self,
        payload: dict | int = 0,
        /,
        base_url: str | Callable[[], str] = "https://captchaapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> bytes | Coroutine[Any, Any, bytes]:
        """10 个汉字单独的图片，包含验证码中 4 个汉字，编号从 0 到 9

        GET https://captchaapi.115.com/?ct=index&ac=code&t=single

        :payload:
            - id: int = 0
        """
        api = complete_url(
            base_url=base_url, query={"ct": "index", "ac": "code", "t": "single"}
        )
        if not isinstance(payload, dict):
            payload = {"id": payload}
        request_kwargs.setdefault("parse", False)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def captcha_verify(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def captcha_verify(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def captcha_verify(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """提交验证码

        POST https://webapi.115.com/user/captcha

        :payload:
            - code: int | str 💡 从 0 到 9 中选取 4 个数字的一种排列
            - sign: str = <default>     💡 来自 `captcha_sign` 接口的响应
            - ac: str = "security_code" 💡 默认就行，不要自行决定
            - type: str = "web"         💡 默认就行，不要自行决定
            - ctype: str = "web"        💡 需要和 type 相同
            - client: str = "web"       💡 需要和 type 相同
        """
        api = complete_url("/user/captcha", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"code": payload}
        payload = {
            "ac": "security_code",
            "type": "web",
            "ctype": "web",
            "client": "web",
            **payload,
        }

        def gen_step():
            if "sign" not in payload:
                resp = yield self.captcha_sign(async_=async_)
                payload["sign"] = resp["sign"]
            return self.request(
                url=api,
                method="POST",
                data=payload,
                async_=async_,
                **request_kwargs,
            )

        return run_gen_step(gen_step, async_)

    @overload
    def _clouddownload_web_request(
        self,
        payload: dict = {},
        /,
        action: str = "",
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def _clouddownload_web_request(
        self,
        payload: dict = {},
        /,
        action: str = "",
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def _clouddownload_web_request(
        self,
        payload: dict = {},
        /,
        action: str = "",
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        api = complete_url("/web/", base_url=base_url)
        if action:
            payload["ac"] = action
        if method.upper() == "POST":
            request_kwargs["data"] = payload
        else:
            request_kwargs["params"] = payload
        return self.request(
            url=api,
            method=method,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def _clouddownload_request(
        self,
        payload: dict = {},
        /,
        action: str = "",
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def _clouddownload_request(
        self,
        payload: dict = {},
        /,
        action: str = "",
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def _clouddownload_request(
        self,
        payload: dict = {},
        /,
        action: str = "",
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        api = complete_url("/", base_url=base_url)
        if action:
            payload["ac"] = action
        if method.upper() == "POST":
            request_kwargs["data"] = payload
            request_kwargs.setdefault("ecdh_encrypt", True)
        else:
            request_kwargs["params"] = payload
        return self.request(
            url=api,
            method=method,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def _clouddownload_lixianssp_request(
        self,
        payload: dict = {},
        /,
        action: str = "",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def _clouddownload_lixianssp_request(
        self,
        payload: dict = {},
        /,
        action: str = "",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def _clouddownload_lixianssp_request(
        self,
        payload: dict = {},
        /,
        action: str = "",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        api = complete_url("/lixianssp/", base_url=base_url)
        request_kwargs["method"] = "POST"
        for k, v in payload.items():
            payload[k] = str(v)
        if action:
            payload["ac"] = action
        app_ver = payload.setdefault("app_ver", _app_version)
        request_kwargs["headers"] = {
            **(request_kwargs.get("headers") or {}),
            "user-agent": f"Mozilla/5.0 115disk/{app_ver} 115Browser/{app_ver} 115wangpan_android/{app_ver}",
        }
        request_kwargs["ecdh_encrypt"] = False

        def parse(_, content: bytes, /) -> dict:
            json = json_maybe_decrypt_loads(content)
            if data := json.get("data"):
                try:
                    json["data"] = json_loads(_rsa_decrypt(data))
                except Exception:
                    pass
            return json

        request_kwargs.setdefault("parse", parse)
        return self.request(
            url=api,
            data={"data": rsa_encrypt(dumps(payload)).decode("ascii")},
            async_=async_,
            **request_kwargs,
        )

    @overload
    def diary_add(
        self,
        payload: str | dict | list,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def diary_add(
        self,
        payload: str | dict | list,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def diary_add(
        self,
        payload: str | dict | list,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """新建日记

        POST https://life.115.com/api/1.0/{app}/1.0/diary/add

        :payload:
            - form[content]: str 💡 内容
            - form[subject]: int | str = <default> 💡 标题
            - form[user_time]: int | float = <default> 💡 时间戳，单位是秒
            - form[weather]: int = <default> 💡 天气
            - form[mood]: int = <default> 💡 心情
            - form[moods]: int | str = <default> 💡 心情，多个用逗号 "," 隔开
            - form[tags][]: str = <default> 💡 标签
            - ...
            - form[tags][0]: str = <default> 💡 标签
            - ...
            - form[index_image] = <default> 💡 封面图片链接
            - form[address]: str = <default>           💡 地点
            - form[location]: str = <default>          💡 地名
            - form[longitude]: float | str = <default> 💡 经度
            - form[latitude]: float | str = <default>  💡 纬度
            - form[mid]: str = <default>               💡 位置编码
            - form[maps]: list[dict] = <default>       💡 多个地图位置
            - form[maps][0][address]: str = <default>
            - form[maps][0][location]: str = <default>
            - form[maps][0][latitude]: float | str = <default>
            - form[maps][0][longitude] float | str = <default>
            - form[maps][0][mid]: str = <default>
            - ...
        """
        api = complete_url(f"/api/1.0/{app}/1.0/diary/add", base_url)
        now = int(time())
        if isinstance(payload, str):
            payload = {"form[content]": payload, "form[user_time]": now}
        elif isinstance(payload, dict):
            payload = dict(expand_payload(payload, prefix="form", enum_seq=True))
            payload.setdefault("form[user_time]", now)
        elif isinstance(payload, list):
            payload = [
                ("form[user_time]", now),
                *expand_payload(payload, prefix="form"),
            ]
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def diary_del(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def diary_del(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def diary_del(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除日记

        POST https://life.115.com/api/1.0/{app}/1.0/diary/delete

        :payload:
            - diary_id: int | str 💡 日记 id
        """
        api = complete_url(f"/api/1.0/{app}/1.0/diary/delete", base_url)
        if isinstance(payload, (int, str)):
            payload = {"diary_id": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def diary_detail(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def diary_detail(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def diary_detail(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取日记详情

        GET https://life.115.com/api/1.0/{app}/1.0/diary/detail

        :payload:
            - diary_id: int | str 💡 日记 id
            - format: str = html
        """
        api = complete_url(f"/api/1.0/{app}/1.0/diary/detail", base_url)
        if isinstance(payload, (int, str)):
            payload = {"diary_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def diary_detail2(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def diary_detail2(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def diary_detail2(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取日记详情

        GET https://life.115.com/api/1.0/{app}/1.0/life/diarydetail

        :payload:
            - diary_id: int | str 💡 日记 id
            - format: str = html
        """
        api = complete_url(f"/api/1.0/{app}/1.0/life/diarydetail", base_url)
        if isinstance(payload, (int, str)):
            payload = {"diary_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def diary_edit(
        self,
        payload: dict | list,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def diary_edit(
        self,
        payload: dict | list,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def diary_edit(
        self,
        payload: dict | list,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """修改日记

        POST https://life.115.com/api/1.0/{app}/1.0/diary/edit

        :payload:
            - form[diary_id]: str 💡 日记 id
            - form[content]: str = <default> 💡 内容
            - form[subject]: int | str = <default> 💡 标题
            - form[user_time]: int | float = <default> 💡 时间戳，单位是秒
            - form[weather]: int = <default> 💡 天气
            - form[mood]: int = <default> 💡 心情
            - form[moods]: int | str = <default> 💡 心情，多个用逗号 "," 隔开
            - form[tags][]: str = <default> 💡 标签
            - ...
            - form[tags][0]: str = <default> 💡 标签
            - ...
            - form[index_image] = <default> 💡 封面图片链接
            - form[address]: str = <default>           💡 地点
            - form[location]: str = <default>          💡 地名
            - form[longitude]: float | str = <default> 💡 经度
            - form[latitude]: float | str = <default>  💡 纬度
            - form[mid]: str = <default>               💡 位置编码
            - form[maps]: list[dict] = <default>       💡 多个地图位置
            - form[maps][0][address]: str = <default>
            - form[maps][0][location]: str = <default>
            - form[maps][0][latitude]: float | str = <default>
            - form[maps][0][longitude] float | str = <default>
            - form[maps][0][mid]: str = <default>
            - ...
        """
        api = complete_url(f"/api/1.0/{app}/1.0/diary/edit", base_url)
        if isinstance(payload, dict):
            payload = dict(expand_payload(payload, prefix="form", enum_seq=True))
        elif isinstance(payload, list):
            payload = list(expand_payload(payload, prefix="form"))
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def diary_get_config(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def diary_get_config(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def diary_get_config(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取日记可选项（例如天气、心情等）的取值集合

        GET https://life.115.com/api/1.0/{app}/1.0/diary/get_diary_config
        """
        api = complete_url(f"/api/1.0/{app}/1.0/diary/get_diary_config", base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def diary_get_latest_tags(
        self,
        payload: int | str | dict = {},
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def diary_get_latest_tags(
        self,
        payload: int | str | dict = {},
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def diary_get_latest_tags(
        self,
        payload: int | str | dict = {},
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取最近使用过的标签列表

        GET https://life.115.com/api/1.0/{app}/1.0/diary/getlatesttags

        :payload:
            - q: str = "" 💡 筛选关键词
            - color: 0 | 1 = <default>
            - limit: int = <default> 💡 最多返回数量，⚠️ 这个参数似乎无效
        """
        api = complete_url(f"/api/1.0/{app}/1.0/diary/getlatesttags", base_url)
        if isinstance(payload, int):
            payload = {"limit": payload}
        elif isinstance(payload, str):
            payload = {"q": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def diary_get_tag_color(
        self,
        payload: str | list | tuple | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def diary_get_tag_color(
        self,
        payload: str | list | tuple | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def diary_get_tag_color(
        self,
        payload: str | list | tuple | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取标签的颜色

        POST https://life.115.com/api/1.0/{app}/1.0/diary/gettagcolor

        :payload:
            - tags: str 💡 标签文本
            - tags[]: str
            - ...
            - tags[0]: str
            - tags[1]: str
            - ...
        """
        api = complete_url(f"/api/1.0/{app}/1.0/diary/gettagcolor", base_url)
        if not isinstance(payload, dict):
            if isinstance(payload, (list, tuple)):
                payload = [
                    t if isinstance(t, (list, tuple)) else ("tags[]", str(t))
                    for t in payload
                ]
            else:
                payload = {"tags": str(payload)}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def diary_list(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def diary_list(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def diary_list(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取日记列表，此接口是对 `life_glist` 的封装

        :payload:
            - start: int = 0 💡 开始索引，从 0 开始
            - limit: int = <default> 💡 分页大小
            - only_public: 0 | 1 = <default>
            - msg_note: 0 | 1 = <default>
            - option: 0 | 1 = <default>
        """
        if isinstance(payload, int):
            payload = {"start": payload}
        else:
            payload = dict(payload)
        payload.setdefault("type", 5)
        return self.life_glist(
            payload, app=app, base_url=base_url, async_=async_, **request_kwargs
        )

    @overload
    def diary_search(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def diary_search(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def diary_search(
        self,
        payload: str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """搜索日记

        GET https://life.115.com/api/1.0/{app}/1.0/diary/search

        :payload:
            - q: str 💡 关键词
            - start: int = 0 💡 开始索引，从 0 开始
            - limit: int = <default> 💡 分页大小
            - display_list: 0 | 1 = <default>
        """
        api = complete_url(f"/api/1.0/{app}/1.0/diary/search", base_url)
        if isinstance(payload, str):
            payload = {"q": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def diary_settag(
        self,
        payload: dict | list,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def diary_settag(
        self,
        payload: dict | list,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def diary_settag(
        self,
        payload: dict | list,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置日记标签

        POST https://life.115.com/api/1.0/{app}/1.0/diary/settag

        :payload:
            - diary_id: int | str 💡 日记 id
            - tags: str
            - tags[]: str
            - ...
            - tags[0]: str
            - tags[1]: str
            - ...
        """
        api = complete_url(f"/api/1.0/{app}/1.0/diary/settag", base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def diary_settop(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def diary_settop(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def diary_settop(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """切换日记的置顶状态，此接口是对 `life_set_top` 的封装

        .. attention::
            这个接口会自动切换日记的置顶状态，但不支持手动指定是否置顶，只是在置顶和不置顶间来回切换。

        :payload:
            - relation_id: int | str 💡 日记 id
        """
        if isinstance(payload, (int, str)):
            payload = {"relation_id": payload}
        payload.setdefault("type", 5)
        return self.life_set_top(
            payload, app=app, base_url=base_url, async_=async_, **request_kwargs
        )

    @overload
    def _fs_edit_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        attr: str,
        default: Any = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def _fs_edit_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        attr: str,
        default: Any = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def _fs_edit_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        attr: str,
        default: Any = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量设置文件或目录（备注、标签、封面等），此接口是对 `fs_edit` 的封装"""
        if isinstance(payload, (int, str)):
            payload = [("fid", payload), (attr, default)]
        elif isinstance(payload, list):
            if not any(a[0] == attr for a in payload):
                payload.append((attr, default))
        elif isinstance(payload, dict):
            payload.setdefault(attr, default)
        else:
            payload = [("fid[]", fid) for fid in payload]
            payload.append((attr, default))
        return self.fs_edit(payload, base_url=base_url, async_=async_, **request_kwargs)

    @overload
    def _fs_edit_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        attr: str,
        default: Any = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def _fs_edit_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        attr: str,
        default: Any = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def _fs_edit_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        attr: str,
        default: Any = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量设置文件或目录（备注、标签、封面等），此接口是对 `fs_files_update_app` 的封装"""
        if isinstance(payload, (int, str)):
            payload = [("file_id", payload), (attr, default)]
        elif isinstance(payload, list):
            if not any(a[0] == attr for a in payload):
                payload.append((attr, default))
        elif isinstance(payload, dict):
            payload.setdefault(attr, default)
        else:
            payload = [(f"file_id[{i}]", fid) for i, fid in enumerate(payload)]
            payload.append((attr, default))
        return self.fs_files_update_app(
            payload,
            async_=async_,
            app=app,
            base_url=base_url,
            **request_kwargs,
        )

    @overload
    def life_batch_delete(
        self,
        payload: Iterable[dict] | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_batch_delete(
        self,
        payload: Iterable[dict] | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_batch_delete(
        self,
        payload: Iterable[dict] | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量删除操作历史：批量删除 115 生活事件列表

        POST https://life.115.com/api/1.0/{app}/1.0/life/life_batch_delete

        :payload:
            - delete_data: str 💡 JSON array，每条数据格式为 {"relation_id": str, "behavior_type": str}
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/life/life_batch_delete", base_url=base_url
        )
        if not isinstance(payload, dict):
            payload = {
                "delete_data": (b"[%s]" % b",".join(map(dumps, payload))).decode(
                    "utf-8"
                )
            }
        return self.request(
            url=api,
            method="POST",
            data=payload,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def life_behavior_detail(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_behavior_detail(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_behavior_detail(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 `P115Client.life_list` 操作记录明细

        GET https://webapi.115.com/behavior/detail

        .. attention::
            这个接口最多能拉取前 10_000 条数据，且响应速度也较差，请优先使用 ``P115Client.life_behavior_detail_app()``。
            但如果指定 ``type`` 或 ``date``，响应可能会快得多，但当涉及的总量较多时，速度依然会很慢，哪怕你只拉取其中的几条。

        .. caution::
            缺乏下面这些事件：

            - 从回收站还原文件或目录（但相应的删除事件会消失）

        :payload:
            - type: str = "" 💡 操作类型，若不指定则是全部

                - "upload_image_file": 1 💡 上传图片
                - "upload_file":       2 💡 上传文件或目录（不包括图片）
                - "star_image":        3 💡 给图片设置星标
                - "star_file":         4 💡 给文件或目录设置星标（不包括图片）
                - "move_image_file":   5 💡 移动图片
                - "move_file":         6 💡 移动文件或目录（不包括图片）
                - "browse_image":      7 💡 浏览图片
                - "browse_video":      8 💡 浏览视频
                - "browse_audio":      9 💡 浏览音频
                - "browse_document":  10 💡 浏览文档
                - "receive_files":    14 💡 接收文件
                - "new_folder":       17 💡 新增目录
                - "copy_folder":      18 💡 复制目录
                - "folder_label":     19 💡 目录设置标签
                - "folder_rename":    20 💡 目录改名
                - "delete_file":      22 💡 删除文件或目录
                - "copy_file":        23 💡 复制文件
                - "file_rename":      24 💡 文件改名

            - limit: int = 1_000         💡 最大值为 1_000
            - offset: int = 0
            - date: str = <default>      💡 日期，格式为 'YYYY-MM-DD'，指定拉取这一天的数据
        """
        api = complete_url("/behavior/detail", base_url=base_url)
        if isinstance(payload, str):
            payload = {"type": payload}
        payload = {"limit": 1_000, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def life_behavior_detail_app(
        self,
        payload: str | dict = "",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_behavior_detail_app(
        self,
        payload: str | dict = "",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_behavior_detail_app(
        self,
        payload: str | dict = "",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 `P115Client.life_list` 操作记录明细

        GET https://proapi.115.com/{app}/behavior/detail

        .. caution::
            缺乏下面这些事件：

            - 从回收站还原文件或目录（但相应的删除事件会消失）

        .. caution::
            此接口有被风控的风险，两次调用之间相隔 5 秒以上为宜，但即使风控，恢复起来也比较快

        :payload:
            - type: str = "" 💡 操作类型

                - "upload_image_file": 1 💡 上传图片
                - "upload_file":       2 💡 上传文件或目录（不包括图片）
                - "star_image":        3 💡 给图片设置星标
                - "star_file":         4 💡 给文件或目录设置星标（不包括图片）
                - "move_image_file":   5 💡 移动图片
                - "move_file":         6 💡 移动文件或目录（不包括图片）
                - "browse_image":      7 💡 浏览图片
                - "browse_video":      8 💡 浏览视频
                - "browse_audio":      9 💡 浏览音频
                - "browse_document":  10 💡 浏览文档
                - "receive_files":    14 💡 接收文件
                - "new_folder":       17 💡 新增目录
                - "copy_folder":      18 💡 复制目录
                - "folder_label":     19 💡 目录设置标签
                - "folder_rename":    20 💡 目录改名
                - "delete_file":      22 💡 删除文件或目录
                - "copy_file":        23 💡 复制文件
                - "file_rename":      24 💡 文件改名

            - limit: int = 1_000         💡 最大值为 1_000
            - offset: int = 0
            - date: str = <default>      💡 日期，格式为 'YYYY-MM-DD'，指定拉取这一天的数据
        """
        api = complete_url("/behavior/detail", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"type": payload}
        payload = {"limit": 1_000, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def life_behavior_doc_post_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_behavior_doc_post_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_behavior_doc_post_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """推送事件：浏览文档 "browse_document"

        POST https://proapi.115.com/{app}/files/doc_behavior

        :payload:
            - file_id: int | str
            - file_id[0]: int | str
            - file_id[1]: int | str
            - ...
        """
        api = complete_url("/files/doc_behavior", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        elif not isinstance(payload, dict):
            payload = {f"file_id[{i}]": fid for i, fid in enumerate(payload)}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def life_behavior_img_post_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_behavior_img_post_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_behavior_img_post_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """推送事件：浏览图片 "browse_image"

        POST https://proapi.115.com/{app}/files/img_behavior

        :payload:
            - file_id: int | str
            - file_id[0]: int | str
            - file_id[1]: int | str
            - ...
        """
        api = complete_url("/files/img_behavior", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        elif not isinstance(payload, dict):
            payload = {f"file_id[{i}]": fid for i, fid in enumerate(payload)}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def life_calendar_getoption(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_calendar_getoption(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_calendar_getoption(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 115 生活的开关设置

        GET https://life.115.com/api/1.0/{app}/1.0/calendar/getoption

        .. hint::
            app 可以是任意字符串，服务器并不做检查。其他可用 app="web" 的接口可能皆是如此
        """
        api = complete_url(f"/api/1.0/{app}/1.0/calendar/getoption", base_url=base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def life_calendar_getoption2(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_calendar_getoption2(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_calendar_getoption2(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 115 生活的开关设置

        GET https://life.115.com/api/1.0/{app}/1.0/calendar/recent_operations_getoption
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/calendar/recent_operations_getoption",
            base_url=base_url,
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def life_calendar_setoption(
        self,
        payload: Literal[0, 1] | dict = 1,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_calendar_setoption(
        self,
        payload: Literal[0, 1] | dict = 1,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_calendar_setoption(
        self,
        payload: Literal[0, 1] | dict = 1,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置 115 生活的开关选项

        POST https://life.115.com/api/1.0/{app}/1.0/calendar/setoption

        :payload:
            - locus: 0 | 1 = 1     💡 开启或关闭最近记录
            - open_life: 0 | 1 = 1 💡 显示或关闭
            - birthday: 0 | 1 = <default>
            - holiday: 0 | 1 = <default>
            - lunar: 0 | 1 = <default>
            - view: 0 | 1 = <default>
            - diary: 0 | 1 = <default>
            - del_notice_item: 0 | 1 = <default>
            - first_week: 0 | 1 = <default>
        """
        api = complete_url(f"/api/1.0/{app}/1.0/calendar/setoption", base_url=base_url)
        if isinstance(payload, dict):
            payload = {"locus": 1, "open_life": 1, **payload}
        else:
            payload = {"locus": 1, "open_life": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def life_calendar_setoption2(
        self,
        payload: Literal[0, 1] | dict = 1,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_calendar_setoption2(
        self,
        payload: Literal[0, 1] | dict = 1,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_calendar_setoption2(
        self,
        payload: Literal[0, 1] | dict = 1,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置 115 生活的开关选项

        POST https://life.115.com/api/1.0/{app}/1.0/calendar/recent_operations_setoption

        :payload:
            - locus: 0 | 1 = 1     💡 开启或关闭最近记录
            - open_life: 0 | 1 = 1 💡 显示或关闭
            - birthday: 0 | 1 = <default>
            - holiday: 0 | 1 = <default>
            - lunar: 0 | 1 = <default>
            - view: 0 | 1 = <default>
            - diary: 0 | 1 = <default>
            - del_notice_item: 0 | 1 = <default>
            - first_week: 0 | 1 = <default>
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/calendar/recent_operations_setoption",
            base_url=base_url,
        )
        if isinstance(payload, dict):
            payload = {"locus": 1, "open_life": 1, **payload}
        else:
            payload = {"locus": 1, "open_life": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def life_cdlist(
        self,
        payload: int | dict = {},
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_cdlist(
        self,
        payload: int | dict = {},
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_cdlist(
        self,
        payload: int | dict = {},
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取节假日等

        GET https://life.115.com/api/1.0/{app}/1.0/life/cdlist

        :payload:
            - start_time: int = <default>    💡 开始时间戳，单位是秒，默认为当年第一天零点
            - end_time: int = <default>      💡 开始时间戳，单位是秒，默认为次年第一天零点前一秒
            - holiday: 0 | 1 = <default>     💡 是否显示节假日
            - only_public: 0 | 1 = <default>
        """
        api = complete_url(f"/api/1.0/{app}/1.0/life/cdlist", base_url)
        if isinstance(payload, int):
            payload = {"end_time": payload}
        else:
            payload = dict(payload)
        if "start_time" not in payload:
            this_year = date.today().year
            payload["start_time"] = int(datetime(this_year, 1, 1).timestamp())
        if "end_time" not in payload:
            this_year = datetime.fromtimestamp(int(payload["start_time"])).year
            payload["end_time"] = int(datetime(this_year + 1, 1, 1).timestamp()) - 1
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def life_get_pic_url(
        self,
        payload: str | tuple[str, ...] | dict | list,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_get_pic_url(
        self,
        payload: str | tuple[str, ...] | dict | list,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_get_pic_url(
        self,
        payload: str | tuple[str, ...] | dict | list,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量获取图片的预览图链接

        POST https://life.115.com/api/1.0/{app}/1.0/imgload/get_pic_url

        .. hint::
            这个接口获取的链接似乎长久有效，而且支持任何文件（只要有人上传过），但限制文件大小在 50 MB 以内

        .. tip::
            在获得的链接最后加上一个 ``&i=1``，就可以获取原始尺寸（但不一定是原图）

        :payload:
            - rs: str 💡 图片的 sha1 （必须大写）或者 f"{oss_bucket}_{oss_object}"（由 `upload_file_image` 接口的响应获得），后者跳转次数更少、响应更快
            - rs[]: str
            - ...
            - rs[0]: str
            - rs[1]: str
            - ...
            - module: int = <default>
            - file_names[]: str = <default>
            - ...
            - type[]: int = <default>
            - ...
        """
        api = complete_url(f"/api/1.0/{app}/1.0/imgload/get_pic_url", base_url=base_url)
        if isinstance(payload, str):
            payload = {"rs": payload}
        elif isinstance(payload, tuple):
            payload = [("rs[]", s) for s in payload]
        return self.request(
            url=api,
            method="POST",
            data=payload,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def life_get_pic_url2(
        self,
        payload: str | tuple[str, ...] | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://q.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_get_pic_url2(
        self,
        payload: str | tuple[str, ...] | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://q.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_get_pic_url2(
        self,
        payload: str | tuple[str, ...] | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://q.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量获取图片的预览图链接

        POST https://q.115.com/ajax_request/get_pic_url

        .. hint::
            这个接口获取的链接似乎长久有效，而且支持任何文件（只要有人上传过），但限制文件大小在 50 MB 以内

        .. tip::
            在获得的链接最后加上一个 ``&i=1``，就可以获取原始尺寸（但不一定是原图）

        :payload:
            - rs: str 💡 图片的 sha1 （必须大写）或者 f"{oss_bucket}_{oss_object}"（由 `upload_file_image` 接口的响应获得），后者跳转次数更少、响应更快
            - rs[]: str
            - ...
            - rs[0]: str
            - rs[1]: str
            - ...
            - module: int = <default>
            - file_names[]: str = <default>
            - ...
            - type[]: int = <default>
            - ...
        """
        api = complete_url("/ajax_request/get_pic_url", base_url=base_url)
        if isinstance(payload, str):
            payload = {"rs": payload}
        elif isinstance(payload, tuple):
            payload = [("rs[]", s) for s in payload]
        return self.request(
            url=api,
            method="POST",
            data=payload,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def life_clear_history(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_clear_history(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_clear_history(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """清空操作历史：清空 115 生活事件列表

        POST https://life.115.com/api/1.0/{app}/1.0/life/life_clear_history

        :payload:
            - tab_type: 0 | 1 = <default>
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/life/life_clear_history", base_url=base_url
        )
        if isinstance(payload, int):
            payload = {"tab_type": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def life_glist(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_glist(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_glist(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取备忘（记录/笔记/记事）、日记或日程的列表

        GET https://life.115.com/api/1.0/{app}/1.0/life/glist

        .. note::
            返回数据列表中，每一条都有个 `"type"` 字段，这个和请求参数里面的 `"type"` 含义并不同

            - 2: 备忘
            - 3: 日程
            - 4: 瞬间
            - 5: 日记

        :payload:
            - start: int = 0 💡 开始索引，从 0 开始
            - limit: int = <default> 💡 分页大小
            - type: int = 8 💡 分类：1,6:瞬间 2:日记+日程 3:备忘 4,7:瞬间+备忘 5:日记 8:所有（日记+备忘+日程）
            - only_public: 0 | 1 = <default>
            - msg_note: 0 | 1 = <default>
            - option: 0 | 1 = <default>
        """
        api = complete_url(f"/api/1.0/{app}/1.0/life/glist", base_url)
        if isinstance(payload, int):
            payload = {"start": payload}
        else:
            payload = dict(payload)
        payload.setdefault("type", 8)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def life_has_data(
        self,
        payload: int | dict = {},
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_has_data(
        self,
        payload: int | dict = {},
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_has_data(
        self,
        payload: int | dict = {},
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取有数据的那几天零点的时间戳

        GET https://life.115.com/api/1.0/{app}/1.0/life/life_has_data

        :payload:
            - end_time: int = <default>
            - show_note_cal: 0 | 1 = <default>
            - start_time: int = <default>
        """
        api = complete_url(f"/api/1.0/{app}/1.0/life/life_has_data", base_url=base_url)
        if isinstance(payload, int):
            payload = {"start_time": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def life_list(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_list(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_list(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列登录和增删改操作记录（最新几条）

        GET https://life.115.com/api/1.0/{app}/1.0/life/life_list

        .. note::
            为了实现分页拉取，需要指定 last_data 参数。只要上次返回的数据不为空，就会有这个值，直接使用即可

        .. attention::
            此接口正在被 `P115Client.life_recent_operations` 取代

        .. hint::
            引用：https://cdnres.115.com/life/m_r/web/static_v11.0/homepage/lifetime.js

            - 'upload_file'          => '上传文件'   💡 上传文件(非图片) 文件类
            - 'upload_image_file'    => '上传图片'   💡 上传文件(图片)   文件类
            - 'backup_album'         => '备份相册'   💡 备份相册         文件类
            - 'sync_communication'   => '同步通讯录' 💡 同步通讯录       文件类
            - 'receive_files'        => '接收文件'   💡 接收文件         文件类
            - 'star_file'            => '星标文件'   💡 星标文件         文件类
            - 'radar_sharing'        => '雷达分享'   💡 雷达分享         文件类
            - 'file_search'          => '文件搜索'   💡 文件搜索         文件类
            - 'move_file'            => '移动文件'   💡 移动文件(非图片) 文件类
            - 'move_image_file'      => '移动图片'   💡 移动文件(图片)   文件类
            - 'browse_document'      => '浏览文档'   💡 浏览文档         信息预览类
            - 'browse_video'         => '浏览视频'   💡 浏览视频         信息预览类
            - 'browse_audio'         => '浏览音频'   💡 浏览音频         信息预览类
            - 'browse_image'         => '浏览图片'   💡 浏览图片         信息预览类
            - 'publish_record'       => '发布记录'   💡 发布记录         信息发布类
            - 'publish_calendar'     => '发布日程'   💡 发布日程         信息发布类
            - 'publish_home'         => '发布传说'   💡 发布传说         信息发布类
            - 'account_security'     => '账号安全'   💡 账号安全         账号安全类

            一些筛选条件::

                - 全部：type=0
                - 上传文件：type=1&file_behavior_type=1
                - 浏览文件：type=1&file_behavior_type=2
                - 星标文件：type=1&file_behavior_type=3
                - 移动文件：type=1&file_behavior_type=4
                - 目录：type=1&file_behavior_type=5
                - 备份：type=1&file_behavior_type=6
                - 删除文件：type=1&file_behavior_type=7
                - 账号安全：type=2
                - 通讯录：type=3
                - 其他：type=99

            一些类型分类::

                .. code:: python

                    {
                        'file':['upload_file', 'upload_image_file', 'backup_album', 'sync_communication',
                                'receive_files', 'star_file', 'radar_sharing', 'file_search', 'move_file',
                                'move_image_file', 'star_image', 'del_photo_image', 'del_similar_image',
                                'generate_smart_albums', 'new_person_albums', 'del_person_albums',
                                'generate_photo_story', 'share_photo', 'folder_rename', 'folder_label',
                                'new_folder', 'copy_folder', 'delete_file'],
                        'review':['browse_video', 'browse_document', 'browse_audio', 'browse_image'],
                        'edit':['publish_record', 'publish_calendar', 'publish_home'],
                        'safe':['account_security'],
                        'cloud':[],
                        'share': ['share_contact']
                    }

        :payload:
            - start: int = 0
            - limit: int = 1_000
            - check_num: int = <default> 💡 选中记录数
            - del_data: str = <default> 💡 JSON array，删除时传给接口数据
            - end_time: int = <default> 💡 结束时间戳
            - file_behavior_type: int | str = <default> 💡 筛选类型，有多个则用逗号 ',' 隔开

                - 💡 0: 所有
                - 💡 1: 上传
                - 💡 2: 浏览
                - 💡 3: 星标
                - 💡 4: 移动
                - 💡 5: 标签
                - 💡 6: <UNKNOWN>
                - 💡 7: 删除

            - isPullData: 'true' | 'false' = <default> 💡 是否下拉加载数据
            - isShow: 0 | 1 = <default> 💡 是否显示
            - last_data: str = <default> 💡 JSON object, e.g. '{"last_time":1700000000,"last_count":1,"total_count":200}'
            - mode: str = <default> 💡 操作模式

                - 💡 "show" 展示列表模式
                - 💡 "select": 批量操作模式

            - selectedRecords: str = <default> 💡 JSON array，选中记录 id 数组
            - show_note_cal: 0 | 1 = <default>
            - show_type: int = 0 💡 筛选类型，有多个则用逗号 ',' 隔开

                - 💡 0: 所有
                - 💡 1: 增、删、改、移动、上传、接收、设置标签等文件系统操作
                - 💡 2: 浏览文件
                - 💡 3: <UNKNOWN>
                - 💡 4: account_security

            - start_time: int = <default> 💡 开始时间戳
            - tab_type: int = <default>
            - total_count: int = <default> 💡 列表所有项数
            - type: int = <default> 💡 类型
        """
        if app in ("", "desktop", "chrome", "aps"):
            app = "web"
        api = complete_url(f"/api/1.0/{app}/1.0/life/life_list", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"start": payload}
        payload = {"limit": 1_000, "show_type": 0, "start": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def life_recent_browse(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_recent_browse(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_recent_browse(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取最近浏览记录

        GET https://life.115.com/api/1.0/{app}/1.0/life/recent_browse

        :payload:
            - start: int = 0
            - limit: int = 1000
        """
        api = complete_url(f"/api/1.0/{app}/1.0/life/recent_browse", base_url=base_url)
        if isinstance(payload, int):
            payload = {"start": payload}
        payload.setdefault("limit", 1000)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def life_recent_operation_items(
        self,
        payload: str | dict = "browse_document",
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_recent_operation_items(
        self,
        payload: str | dict = "browse_document",
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_recent_operation_items(
        self,
        payload: str | dict = "browse_document",
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取最近操作记录详细

        GET https://life.115.com/api/1.0/{app}/1.0/life/recent_operation_items

        .. caution::
            这个接口目前必须传 ``behavior_type`` 和 ``date``，而且支持的 ``behavior_type`` 仅限浏览、移动、复制、重命名

        .. caution::
            谨慎，此接口明显是半成品，几乎和 `P115Client.life_behavior_detail` 一样慢，但能力却似乎远远不如

        :payload:
            - behavior_type: str 💡 操作类型（尾部带🚫的表示暂不可用）

                - "upload_image_file": 1 💡 上传图片🚫
                - "upload_file":       2 💡 上传文件或目录（不包括图片）🚫
                - "star_image":        3 💡 给图片设置星标🚫
                - "star_file":         4 💡 给文件或目录设置星标（不包括图片）🚫
                - "move_image_file":   5 💡 移动图片
                - "move_file":         6 💡 移动文件或目录（不包括图片）
                - "browse_image":      7 💡 浏览图片
                - "browse_video":      8 💡 浏览视频
                - "browse_audio":      9 💡 浏览音频
                - "browse_document":  10 💡 浏览文档
                - "receive_files":    14 💡 接收文件🚫
                - "new_folder":       17 💡 新增目录🚫
                - "copy_folder":      18 💡 复制目录
                - "folder_label":     19 💡 目录设置标签🚫
                - "folder_rename":    20 💡 目录改名
                - "delete_file":      22 💡 删除文件或目录🚫
                - "copy_file":        23 💡 复制文件
                - "file_rename":      24 💡 文件改名

            - date: str 💡 日期，格式为 'YYYY-MM-DD'，指定拉取这一天的数据
            - start: int = 0
            - limit: int = 100 💡 最大值为 100
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/life/recent_operation_items", base_url=base_url
        )
        if isinstance(payload, str):
            payload = {"behavior_type": payload}
        payload = {"limit": 100, "date": str(date.today()), **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def life_recent_operations(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_recent_operations(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_recent_operations(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取最近操作记录

        GET https://life.115.com/api/1.0/{app}/1.0/life/recent_operations

        :payload:
            - start: int = 0
            - limit: int = 1_000
            - start_time: int = <default>
            - end_time: int = <default>
            - last_data: str = <default> 💡 需要经过 JSON序列化，格式为：{"last_time": int, "last_count": int, "total_count": int}
            - operation_type: 0 | 1 | 2 | 3 = 0 💡 操作类型

                - 0: 全部
                - 1: 浏览
                - 2: 移动复制
                - 3: 重命名
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/life/recent_operations", base_url=base_url
        )
        if isinstance(payload, int):
            payload = {"start": payload}
        payload.setdefault("limit", 1_000)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def life_recent_operations_clear(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_recent_operations_clear(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_recent_operations_clear(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """清空最近操作记录

        GET https://life.115.com/api/1.0/{app}/1.0/life/recent_operations_clear

        :payload:
            - tab_type: int = 0
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/life/recent_operations_clear", base_url=base_url
        )
        if isinstance(payload, int):
            payload = {"tab_type": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def life_recent_operations_del(
        self,
        payload: Iterable[dict] | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_recent_operations_del(
        self,
        payload: Iterable[dict] | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_recent_operations_del(
        self,
        payload: Iterable[dict] | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量删除最近操作记录

        GET https://life.115.com/api/1.0/{app}/1.0/life/recent_operations_del

        :payload:
            - delete_data: str 💡 JSON array，每条数据格式为 {"relation_id": str, "behavior_type": str}
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/life/recent_operations_del", base_url=base_url
        )
        if not isinstance(payload, dict):
            payload = {
                "delete_data": (b"[%s]" % b",".join(map(dumps, payload))).decode(
                    "utf-8"
                )
            }
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def life_set_top(
        self,
        payload: dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def life_set_top(
        self,
        payload: dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def life_set_top(
        self,
        payload: dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://life.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """切换备忘（记录/笔记/记事）、日记或日程的置顶状态

        GET https://life.115.com/api/1.0/{app}/1.0/life/set_top

        .. attention::
            这个接口会自动切换记录的置顶状态，但不支持手动指定是否置顶，只是在置顶和不置顶间来回切换。

        :payload:
            - relation_id: int | str 💡 备忘、日程或日记的 id
            - type: int 💡 分类：2:备忘 3:日程 4:瞬间 5:日记
        """
        api = complete_url(f"/api/1.0/{app}/1.0/life/set_top", base_url)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def msg_contacts_ls(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://pmsg.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def msg_contacts_ls(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://pmsg.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def msg_contacts_ls(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://pmsg.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取提示消息

        GET https://pmsg.115.com/api/1.0/app/1.0/contact/ls

        :payload:
            - limit: int = 115
            - skip: int = 0
            - t: 0 | 1 = 1
        """
        api = complete_url("/api/1.0/app/1.0/contact/ls", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"skip": payload}
        payload = {"limit": 115, "t": 1, "skip": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def msg_contacts_notice(
        self,
        /,
        base_url: str | Callable[[], str] = "https://msg.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def msg_contacts_notice(
        self,
        /,
        base_url: str | Callable[[], str] = "https://msg.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def msg_contacts_notice(
        self,
        /,
        base_url: str | Callable[[], str] = "https://msg.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取提示消息

        GET https://msg.115.com/?ct=contacts&ac=notice&client=web
        """
        api = complete_url(
            base_url=base_url, query={"ct": "contacts", "ac": "notice", "client": "web"}
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def msg_get_websocket_host(
        self,
        /,
        base_url: str | Callable[[], str] = "https://msg.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def msg_get_websocket_host(
        self,
        /,
        base_url: str | Callable[[], str] = "https://msg.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def msg_get_websocket_host(
        self,
        /,
        base_url: str | Callable[[], str] = "https://msg.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 websocket 链接

        GET https://msg.115.com/?ct=im&ac=get_websocket_host

        .. note::
            用返回数据构造链接，可由此监听 websocket 消息，但目前来看，最多也就实时获得一个【删除】事件

            `wss://{server}/?uid={user_id}&session={session_id}&client_version=100&client_type=5&sequence_id=0&source=web&device_id=0000000000000000000000000000000000000000`
        """
        api = complete_url(
            base_url=base_url, query={"ct": "im", "ac": "get_websocket_host"}
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def multimedia_collection_listen(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_collection_listen(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_collection_listen(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听：自建听单（合集）列表

        GET https://webapi.115.com/multimedia/collection_listen

        .. todo::
            暂不清楚 `sort` 字段各个取值的含义

        :payload:
            - channel_id: int = 1 💡 频道 id，已知：1:音乐 5:视频
            - limit: int = 32
            - offset: int = 0
            - sort: int = <default> 💡 排序依据
            - asc: 0 | 1 = <default> 💡 是否升序排列
        """
        api = complete_url("/multimedia/collection_listen", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload = {"channel_id": 1, "limit": 32, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def multimedia_collection_listen_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_collection_listen_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_collection_listen_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听：设置听单（合集）

        POST https://webapi.115.com/multimedia/collection_listen

        :payload:
            - multimedia_id: int 💡 专辑（详情） id
            - channel_id: int = <default> 💡 频道 id，已知：1:音乐 5:视频
            - collection: 0 | 1 = 1 💡 是否设为合集：0:取消 1:设置（设为合集后，该内容将出现在【自建听单】列表中）
        """
        api = complete_url("/multimedia/collection_listen", base_url=base_url)
        if isinstance(payload, int):
            payload = {"multimedia_id": payload}
        payload = {"collection": 1, **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def multimedia_collection_watch(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_collection_watch(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_collection_watch(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我看：自建合集列表

        GET https://webapi.115.com/multimedia/collection_watch

        .. todo::
            暂不清楚 `sort` 字段各个取值的含义

        :payload:
            - channel_id: int = 5 💡 频道 id，已知：1:音乐 5:视频
            - limit: int = 32
            - offset: int = 0
            - sort: int = <default> 💡 排序依据
            - asc: 0 | 1 = <default> 💡 是否升序排列
        """
        api = complete_url("/multimedia/collection_watch", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload = {"channel_id": 5, "limit": 32, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def multimedia_collection_watch_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_collection_watch_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_collection_watch_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我看：设置合集

        POST https://webapi.115.com/multimedia/collection_watch

        :payload:
            - multimedia_id: int 💡 专辑（详情） id
            - channel_id: int = 5 💡 频道 id，已知：1:音乐 5:视频
            - collection: 0 | 1 = 1 💡 是否设为合集：0:取消 1:设置（设为合集后，该内容将出现在自建合集列表中）
        """
        api = complete_url("/multimedia/collection_watch", base_url=base_url)
        if isinstance(payload, int):
            payload = {"multimedia_id": payload}
        payload = {"channel_id": 5, "collection": 1, **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def multimedia_cover_auto(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_cover_auto(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_cover_auto(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听&我看：自动生成（专辑）封面

        POST https://webapi.115.com/multimedia/cover

        :payload:
            - channel_id: int = 1 💡 频道 id，已知：1:音乐 5:视频
            - ids: int | str 💡 专辑 id，多个用逗号 "," 隔开
            - overwrite: 0 | 1 = 0 💡 是否覆盖
        """
        api = complete_url("/multimedia/cover", base_url=base_url)
        if not isinstance(payload, dict):
            payload = {"ids": payload}
        payload.setdefault("channel_id", 1)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def multimedia_cover_check(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_cover_check(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_cover_check(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听&我看：查看（专辑）封面是否存在

        GET https://webapi.115.com/multimedia/cover_check

        :payload:
            - channel_id: int = 1 💡 频道 id，已知：1:音乐 5:视频
            - ids: int | str 💡 专辑 id，多个用逗号 "," 隔开
        """
        api = complete_url("/multimedia/cover_check", base_url=base_url)
        if not isinstance(payload, dict):
            payload = {"ids": payload}
        payload.setdefault("channel_id", 1)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def multimedia_listen(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_listen(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_listen(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听：专辑（详情）列表 或 专辑（详情）的基本信息和文件列表

        GET https://webapi.115.com/multimedia/listen

        .. note::
            - 指定 `multimedia_id`，则罗列此专辑（详情）的基本信息和文件列表
            - 指定 `parent_id`，则罗列关联此 id 的专辑（详情）列表
            - 都不指定，则罗列所有专辑（详情）列表

        .. todo::
            暂不清楚 `sort` 字段各个取值的含义

        .. todo::
            暂不清楚 `date` 字段的格式要求

        .. todo::
            应该还可以选择【维度】和【时间区间】，但是目前 115 的网页版还未完成此功能

        .. note::
            一个 multimedia_id 对应的专辑被称为详情，如果它还关联到其它 multimedia_id，也就是它们的 parent_id，或者被主动【设为合集】，称为合集

        :payload:
            - channel_id: int = 1 💡 频道 id，已知：1:音乐 5:视频
            - parent_id: int = <default> 💡 关联的专辑（详情） id
            - multimedia_id: int = <default> 💡 专辑（详情） id
            - limit: int = <default> 💡 最多返回数量
            - offset: int = <default> 💡 索引偏移，索引从 0 开始计算
            - sort: int = <default> 💡 排序依据
            - asc: 0 | 1 = <default> 💡 是否升序排列
            - visit_type: int = <default> 💡 已知：0:全部 1:已听 2:未听
            - type_id: int = <default> 💡 分类 id
            - related_name: str = <default> 💡 相关人员名称
            - collection: 0 | 1 = <default> 💡 内容类型：<default>:全部 0:属性 1:合集
            - date: str = <default> 💡 日期、月份或者年份
        """
        api = complete_url("/multimedia/listen", base_url=base_url)
        if isinstance(payload, int):
            payload = {"multimedia_id": payload}
        payload = {"channel_id": 1, "limit": 32, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def multimedia_listen_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_listen_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_listen_update(
        self,
        payload: dict | list,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听：更新专辑（详情）

        POST https://webapi.115.com/multimedia/listen

        :payload:
            - multimedia_id: int 💡 专辑（详情） id
            - channel_id: int = 1 💡 频道 id，已知：1:音乐 5:视频
            - parent_id: int = <default> 💡 关联的专辑（详情） id（作为当前专辑（详情）的上级）
            - custom_sort: int = <default> 💡 自定义排序
            - title: str = <default> 💡 标题
            - description: str = <default> 💡 简介
            - cover: str = <default> 💡 封面图片的提取码
            - country: str = <default> 💡 国家/地区
            - language: str = <default> 💡 语言，多个用逗号 "," 隔开
            - release_date: str = <default> 💡 发行日期，格式为 YYYY-MM-DD
            - type_id: int | str = <default> 💡 类型 id
            - type_id[]: int | str
            - ...
            - type_id[0]: int | str
            - type_id[1]: int | str
            - ...
            - related_id[][{related_id}]: str 💡 相关人员，是 id 到 名字 的映射关系
            - ...
            - rating[1]: int | float | str = <default> 💡 评分：豆瓣
            - rating[2]: int | float | str = <default> 💡 评分：猫眼
            - rating[3]: int | float | str = <default> 💡 评分：烂番茄
            - rating[4]: int | float | str = <default> 💡 评分：优酷
            - rating[5]: int | float | str = <default> 💡 评分：115
            - rating[6]: int | float | str = <default> 💡 评分：IMDB
            - extra_info: str = <default> 💡 附加信息，是一个 JSON object 序列化为字符串，初始值为 '{"version":"","timbre":"","track":"","scene":""}'
            - is_delete: 0 | 1 = <default> 💡 是否删除
        """
        api = complete_url("/multimedia/listen", base_url=base_url)
        if isinstance(payload, dict):
            payload.setdefault("channel_id", 1)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def multimedia_watch(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_watch(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_watch(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我看：专辑（详情）列表 或 专辑（详情）的基本信息和文件列表

        GET https://webapi.115.com/multimedia/watch

        .. note::
            - 指定 `multimedia_id`，则罗列此专辑（详情）的基本信息和文件列表
            - 指定 `parent_id`，则罗列关联此 id 的专辑（详情）列表
            - 都不指定，则罗列所有专辑（详情）列表

        .. todo::
            暂不清楚 `sort` 字段各个取值的含义

        .. todo::
            暂不清楚 `date` 字段的格式要求

        .. todo::
            应该还可以选择【维度】和【时间区间】，但是目前 115 的网页版还未完成此功能

        .. note::
            一个 multimedia_id 对应的专辑被称为详情，如果它还关联到其它 multimedia_id，也就是它们的 parent_id，或者被主动【设为合集】，称为合集

        :payload:
            - channel_id: int = 5 💡 频道 id，已知：1:音乐 5:视频
            - parent_id: int = <default> 💡 关联的专辑（详情） id
            - multimedia_id: int = <default> 💡 专辑（详情） id
            - limit: int = <default> 💡 最多返回数量
            - offset: int = <default> 💡 索引偏移，索引从 0 开始计算
            - sort: int = <default> 💡 排序依据
            - asc: 0 | 1 = <default> 💡 是否升序排列
            - visit_type: int = <default> 💡 已知：0:全部 1:已看 2:未看
            - type_id: int = <default> 💡 分类 id
            - related_name: str = <default> 💡 相关人员名称
            - collection: 0 | 1 = <default> 💡 内容类型：<default>:全部 0:详情 1:合集
            - date: str = <default> 💡 日期、月份或者年份
            - keyword: str = <default> 💡 搜索关键词
        """
        api = complete_url("/multimedia/watch", base_url=base_url)
        if isinstance(payload, int):
            payload = {"multimedia_id": payload}
        payload = {"channel_id": 5, "limit": 32, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def multimedia_watch_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_watch_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_watch_update(
        self,
        payload: dict | list,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我看：更新专辑（详情）

        POST https://webapi.115.com/multimedia/watch

        :payload:
            - multimedia_id: int 💡 专辑（详情） id
            - channel_id: int = 5 💡 频道 id，已知：1:音乐 5:视频
            - parent_id: int = <default> 💡 关联的专辑（详情） id（作为当前专辑（详情）的上级）
            - custom_sort: int = <default> 💡 自定义排序
            - title: str = <default> 💡 标题
            - description: str = <default> 💡 简介
            - cover: str = <default> 💡 封面图片的提取码
            - country: str = <default> 💡 国家/地区
            - language: str = <default> 💡 语言，多个用逗号 "," 隔开
            - release_date: str = <default> 💡 发行日期，格式为 YYYY-MM-DD
            - type_id: int | str = <default> 💡 类型 id
            - type_id[]: int | str
            - ...
            - type_id[0]: int | str
            - type_id[1]: int | str
            - ...
            - related_id[][{related_id}]: str 💡 相关人员，是 id 到 名字 的映射关系
            - ...
            - rating[1]: int | float | str = <default> 💡 评分：豆瓣
            - rating[2]: int | float | str = <default> 💡 评分：猫眼
            - rating[3]: int | float | str = <default> 💡 评分：烂番茄
            - rating[4]: int | float | str = <default> 💡 评分：优酷
            - rating[5]: int | float | str = <default> 💡 评分：115
            - rating[6]: int | float | str = <default> 💡 评分：IMDB
            - extra_info: str = <default> 💡 附加信息，是一个 JSON object 序列化为字符串，初始值为 '{"version":"","timbre":"","track":"","scene":""}'
            - is_delete: 0 | 1 = <default> 💡 是否删除
        """
        api = complete_url("/multimedia/watch", base_url=base_url)
        if isinstance(payload, dict):
            payload.setdefault("channel_id", 5)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def multimedia_recent_listen(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_recent_listen(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_recent_listen(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听：【最近在听】列表

        GET https://webapi.115.com/multimedia/recent_listen

        :payload:
            - channel_id: int = 1 💡 频道 id，已知：1:音乐 5:视频
            - limit: int = 32
            - offset: int = 0
        """
        api = complete_url("/multimedia/recent_listen", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload = {"channel_id": 1, "limit": 32, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def multimedia_recent_listen_update(
        self,
        payload: dict = {},
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_recent_listen_update(
        self,
        payload: dict = {},
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_recent_listen_update(
        self,
        payload: dict = {},
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听：更新【最近在听】

        POST https://webapi.115.com/multimedia/recent_listen

        .. note::
            目前仅支持 clear 操作，即 清空所有记录

        :payload:
            - channel_id: int = 1 💡 频道 id，已知：1:音乐 5:视频
            - action: str = "clear"
        """
        api = complete_url("/multimedia/recent_listen", base_url=base_url)
        payload = {"channel_id": 1, "action": "clear", **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def multimedia_recent_watch(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_recent_watch(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_recent_watch(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我看：【最近观看】列表

        GET https://webapi.115.com/multimedia/recent_watch

        :payload:
            - channel_id: int = 5 💡 频道 id，已知：1:音乐 5:视频
            - limit: int = 32
            - offset: int = 0
        """
        api = complete_url("/multimedia/recent_watch", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload = {"channel_id": 5, "limit": 32, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def multimedia_recent_watch_update(
        self,
        payload: dict = {},
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_recent_watch_update(
        self,
        payload: dict = {},
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_recent_watch_update(
        self,
        payload: dict = {},
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听：更新【最近观看】

        POST https://webapi.115.com/multimedia/recent_watch

        .. note::
            目前仅支持 clear 操作，即 清空所有记录

        :payload:
            - channel_id: int = 5 💡 频道 id，已知：1:音乐 5:视频
            - action: str = "clear"
        """
        api = complete_url("/multimedia/recent_watch", base_url=base_url)
        payload = {"channel_id": 5, "action": "clear", **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def multimedia_relate_file(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_relate_file(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_relate_file(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听&我看：罗列专辑（详情）的关联文件

        GET https://webapi.115.com/multimedia/relate_file

        :payload:
            - multimedia_id: int 💡 专辑（详情） id
            - channel_id: int = 1 💡 频道 id，已知：1:音乐 5:视频
            - limit: int = 32
            - offset: int = 0
            - o: "custom_sort" | "file_name" | "file_size" | "created_time" = <default> 💡 排序依据
            - asc: 0 | 1 = <default> 💡 是否升序排列
        """
        api = complete_url("/multimedia/relate_file", base_url=base_url)
        payload = {"channel_id": 1, "limit": 32, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def multimedia_relate_file_update(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        channel_id: int | str = 1,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_relate_file_update(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        channel_id: int | str = 1,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_relate_file_update(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        channel_id: int | str = 1,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听&我看：更新专辑（详情）的关联文件

        POST https://webapi.115.com/multimedia/relate_file

        .. note::
            指定 `multimedia_id` 时，则针对相应的专辑（详情）进行文件增删；未指定时，则自动创建新的专辑（详情）

        :payload:
            - file_ids: int | str 💡 文件或目录 id，多个用逗号 "," 隔开
            - op: str = "relate" 💡 已知："relate":添加 "delete":删除 "update":更新
            - channel_id: int = 1 💡 频道 id，已知：1:音乐 5:视频
            - multimedia_id: int = <default> 💡 专辑（详情） id
            - one_by_one: 0 | 1 = <default> 💡 （未指定 `multimedia_id` 时生效）是否分别创建专辑（详情）：0:为所选文件创建为一个详情页 1:为每个文件创建单独的详情页
            - sort: int = <default> 💡 序号，用来作为自定义排序的依据
            - visited: 0 | 1 | 2 = <default> 💡 是否标记为访问过
        """
        api = complete_url("/multimedia/relate_file", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_ids": payload}
        elif not isinstance(payload, dict):
            payload = {"file_ids": ",".join(map(str, payload))}
        cast(dict, payload).setdefault("channel_id", channel_id)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def multimedia_related(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_related(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_related(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听&我看：人员列表

        GET https://webapi.115.com/multimedia/related

        :payload:
            - channel_id: int = 1 💡 频道 id，已知：1:音乐 5:视频
        """
        api = complete_url("/multimedia/related", base_url=base_url)
        if isinstance(payload, int):
            payload = {"channel_id": payload}
        else:
            payload.setdefault("channel_id", 1)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def multimedia_related_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_related_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_related_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听&我看：更新人员

        GET https://webapi.115.com/multimedia/related

        .. note::
            未指定 `related_id` 时，则是添加（此时需要指定 `related_name`）；指定时，则是修改

        .. todo::
            暂不支持删除人员

        :payload:
            - related_name: str 💡 相关人员名字
            - channel_id: int = 1 💡 频道 id，已知：1:音乐 5:视频
            - related_id: int = <default> 💡 相关人员 id
        """
        api = complete_url("/multimedia/related", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def multimedia_relation(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_relation(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_relation(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听&我看：罗列专辑（详情）的关联

        POST https://webapi.115.com/multimedia/relation

        :payload:
            - multimedia_id: int 💡 专辑（详情） id
            - parent_id: int
            - op: str
        """
        api = complete_url("/multimedia/relation", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def multimedia_type(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_type(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_type(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听&我看：分类列表

        GET https://webapi.115.com/multimedia/type

        :payload:
            - channel_id: int = 1 💡 频道 id，已知：1:音乐 5:视频
            - parent_id: int = <default>
        """
        api = complete_url("/multimedia/type", base_url=base_url)
        if isinstance(payload, int):
            payload = {"channel_id": payload}
        else:
            payload.setdefault("channel_id", 1)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def multimedia_type_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def multimedia_type_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def multimedia_type_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """我听&我看：更新分类

        GET https://webapi.115.com/multimedia/type

        .. note::
            目前支持创建最多 3 级分类，`parent_id=0` 时为 1 级分类

        .. note::
            未指定 `type_id` 时，则是添加（此时需要指定 `type_name`）；指定时，则是修改

        .. todo::
            暂不支持删除分类

        :payload:
            - channel_id: int = 1 💡 频道 id，已知：1:音乐 5:视频
            - parent_id: int = <default> 💡 上级分类 id
            - type_id: int = <default> 💡 分类 id
            - type_name: str = <default> 💡 分类名称
            - sort: int = <default> 💡 序号
        """
        api = complete_url("/multimedia/type", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_bookmark_list(
        self,
        payload: int | str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://bookmark.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_bookmark_list(
        self,
        payload: int | str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://bookmark.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_bookmark_list(
        self,
        payload: int | str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://bookmark.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列书签（网址收藏夹）

        GET https://bookmark.115.com/api/bookmark_list.php

        .. note::
            这个接口支持 GET 和 POST 请求方法

        :payload:
            - search_value: str = ""
            - parent_id: int = 0
            - limit: int = 1150
            - offset: int = 0
        """
        api = complete_url("/api/bookmark_list.php", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        elif isinstance(payload, str):
            payload = {"search_value": payload}
        payload.setdefault("limit", 1150)
        if request_kwargs.get("method", "").upper() == "POST":
            return self.request(url=api, data=payload, async_=async_, **request_kwargs)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def note_cate_add(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_cate_add(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_cate_add(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """添加记录分类

        POST https://note.115.com/?ct=note&ac=addcate

        :payload:
            - cname: str 💡 最多允许 20 个字符
        """
        api = complete_url(base_url=base_url, query={"ct": "note", "ac": "addcate"})
        if isinstance(payload, str):
            payload = {"cname": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_cate_del(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_cate_del(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_cate_del(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除记录分类

        POST https://note.115.com/?ct=note&ac=delcate

        :payload:
            - cid: int 💡 分类 id
            - action: str = <default>
        """
        api = complete_url(base_url=base_url, query={"ct": "note", "ac": "delcate"})
        if isinstance(payload, int):
            payload = {"cid": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_cate_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_cate_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_cate_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """改名记录分类

        POST https://note.115.com/?ct=note&ac=upcate

        :payload:
            - cid: int   💡 分类 id
            - cname: str 💡 分类名，最多 20 个字符
        """
        api = complete_url(base_url=base_url, query={"ct": "node", "ac": "upcate"})
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_cate_list(
        self,
        payload: bool | dict = True,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_cate_list(
        self,
        payload: bool | dict = True,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_cate_list(
        self,
        payload: bool | dict = True,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取记录分类列表

        GET https://note.115.com/?ct=note&ac=cate

        :payload:
            - has_picknews: 0 | 1 = 1 💡 是否显示 id 为负数的分类
        """
        api = complete_url(base_url=base_url, query={"ct": "note", "ac": "cate"})
        if isinstance(payload, bool):
            payload = {"has_picknews": int(payload)}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def note_cate_list2(
        self,
        payload: bool | dict = True,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_cate_list2(
        self,
        payload: bool | dict = True,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_cate_list2(
        self,
        payload: bool | dict = True,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取记录分类列表

        GET https://note.115.com/api/2.0/api.php?ac=get_category

        :payload:
            - has_picknews: 0 | 1 = 1 💡 是否显示 id 为负数的分类
            - is_all: 0 | 1 = <default> 💡 是否显示全部
            - has_msg: 0 | 1 = <default>
        """
        api = complete_url(
            "/api/2.0/api.php", base_url=base_url, query={"ac": "get_category"}
        )
        if isinstance(payload, bool):
            payload = {"has_picknews": int(payload)}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def note_del(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_del(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_del(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除记录

        POST https://note.115.com/?ct=note&ac=delete

        :payload:
            - nid: int | str 💡 记录 id，多个用逗号 "," 隔开
        """
        api = complete_url(base_url=base_url, query={"ct": "note", "ac": "delete"})
        if isinstance(payload, (int, str)):
            payload = {"nid": payload}
        elif not isinstance(payload, dict):
            payload = {"nid": ",".join(map(str, payload))}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_del2(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_del2(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_del2(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除记录

        POST https://note.115.com/api/2.0/api.php?ac=note_delete

        :payload:
            - nid: int | str 💡 记录 id，多个用逗号 "," 隔开
        """
        api = complete_url(
            "/api/2.0/api.php", base_url=base_url, query={"ac": "note_delete"}
        )
        if isinstance(payload, (int, str)):
            payload = {"nid": payload}
        elif not isinstance(payload, dict):
            payload = {"nid": ",".join(map(str, payload))}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_detail(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_detail(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_detail(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取备忘（记录/笔记/记事）数据

        GET https://note.115.com/?ct=note&ac=detail

        :payload:
            - nid: int 💡 记录 id
        """
        api = complete_url(base_url=base_url, query={"ct": "note", "ac": "detail"})
        if isinstance(payload, int):
            payload = {"nid": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def note_detail2(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_detail2(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_detail2(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取备忘（记录/笔记/记事）数据

        GET https://note.115.com/api/2.0/api.php?ac=note_detail

        :payload:
            - nid: int 💡 记录 id
            - has_picknews: 0 | 1 = <default>
            - is_html: 0 | 1 = <default>
            - copy: 0 | 1 = <default>
        """
        api = complete_url(
            "/api/2.0/api.php", base_url=base_url, query={"ac": "note_detail"}
        )
        if isinstance(payload, int):
            payload = {"nid": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def note_edit_attaches(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_edit_attaches(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_edit_attaches(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """给记录修改附件

        POST https://note.115.com/?ct=note&ac=edit_attaches

        .. attention::
            每个附件的大小必须控制在 200 MB 以内，这也是网页版所允许的单次下载的最大文件

        :payload:
            - nid: int 💡 记录 id
            - pickcodes: str 💡 附件的提取码，多个用逗号 "," 隔开
            - op: "add" | "del" | "save" = "add" 💡 操作类型："add":添加 "del":去除 "save":置换
        """
        api = complete_url(
            base_url=base_url, query={"ct": "note", "ac": "edit_attaches"}
        )
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_fav_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_fav_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_fav_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取星标备忘（记录/笔记/记事）列表

        GET https://note.115.com/?ct=note&ac=get_fav_note_list

        :payload:
            - start: int = 0    💡 开始索引，从 0 开始
            - limit: int = 1150 💡 最多返回数量
        """
        api = complete_url(
            base_url=base_url, query={"ct": "note", "ac": "get_fav_note_list"}
        )
        if isinstance(payload, int):
            payload = {"start": payload}
        payload = {"limit": 1150, "start": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def note_fav_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_fav_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_fav_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """给记录添加或去除星标

        POST https://note.115.com/?ct=note&ac=fav

        :payload:
            - note_id: int 💡 记录 id
            - op: "add" | "del" = "add" 💡 操作类型："add":添加 "del":去除
        """
        api = complete_url(base_url=base_url, query={"ct": "note", "ac": "fav"})
        if isinstance(payload, int):
            payload = {"note_id": payload}
        payload.setdefault("op", "add")
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_get_pic_url(
        self,
        payload: str | tuple[str, ...] | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_get_pic_url(
        self,
        payload: str | tuple[str, ...] | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_get_pic_url(
        self,
        payload: str | tuple[str, ...] | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量获取图片的预览图链接

        POST https://note.115.com?ct=note&ac=get_pic_url

        .. hint::
            这个接口获取的链接似乎长久有效，而且支持任何文件（只要有人上传过），但限制文件大小在 50 MB 以内

        :payload:
            - rs: str 💡 图片的 sha1 （必须大写）或者 f"{oss_bucket}_{oss_object}"（由 `upload_file_image` 接口的响应获得），后者跳转次数更少、响应更快
            - rs[]: str
            - ...
            - rs[0]: str
            - rs[1]: str
            - ...
            - module: int = <default>
            - file_names[]: str = <default>
            - ...
            - type[]: int = <default>
            - ...
        """
        api = complete_url(base_url=base_url, query={"ct": "note", "ac": "get_pic_url"})
        if isinstance(payload, str):
            payload = {"rs": payload}
        elif isinstance(payload, tuple):
            payload = [("rs[]", s) for s in payload]
        return self.request(
            url=api,
            method="POST",
            data=payload,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def note_get_pic_url2(
        self,
        payload: str | tuple[str, ...] | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_get_pic_url2(
        self,
        payload: str | tuple[str, ...] | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_get_pic_url2(
        self,
        payload: str | tuple[str, ...] | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量获取图片的预览图链接

        POST https://note.115.com/api/2.0/api.php?ac=get_pic_url

        .. hint::
            这个接口获取的链接似乎长久有效，而且支持任何文件（只要有人上传过），但限制文件大小在 50 MB 以内

        :payload:
            - rs: str 💡 图片的 sha1 （必须大写）或者 f"{oss_bucket}_{oss_object}"（由 `upload_file_image` 接口的响应获得），后者跳转次数更少、响应更快
            - rs[]: str
            - ...
            - rs[0]: str
            - rs[1]: str
            - ...
            - module: int = <default>
            - file_names[]: str = <default>
            - ...
            - type[]: int = <default>
            - ...
        """
        api = complete_url(
            "/api/2.0/api.php", base_url=base_url, query={"ac": "get_pic_url"}
        )
        if isinstance(payload, str):
            payload = {"rs": payload}
        elif isinstance(payload, tuple):
            payload = [("rs[]", s) for s in payload]
        return self.request(
            url=api,
            method="POST",
            data=payload,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def note_is_fav(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_is_fav(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_is_fav(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """检查记录是否被星标

        .. note::
            这个接口支持 GET 和 POST 请求方法

        GET https://note.115.com/api/2.0/api.php?ac=is_fav

        :payload:
            - note_id: int | str 💡 多个用逗号 "," 隔开
        """
        api = complete_url(
            "/api/2.0/api.php", base_url=base_url, query={"ac": "is_fav"}
        )
        if isinstance(payload, (int, str)):
            payload = {"note_id": payload}
        elif not isinstance(payload, dict):
            payload = {"note_id": ",".join(map(str, payload))}
        if request_kwargs.get("method", "").upper() == "POST":
            return self.request(url=api, data=payload, async_=async_, **request_kwargs)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def note_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取备忘（记录/笔记/记事）列表

        GET https://note.115.com/?ct=note

        :payload:
            - ac: "" | "all" = "all"  💡 如果为 "all"，则显示完整信息，如果为 ""，则显示简要信息（只有标题，没有内容文本）
            - start: int = 0          💡 开始索引，从 0 开始
            - page_size: int = 1150   💡 分页大小，相当于 `limit`
            - cid: int = 0            💡 分类 id：0:全部 -10:云收藏 -15:消息备忘
            - has_picknews: 0 | 1 = 1 💡 是否显示 id 为负数的分类
            - keyword: str = <default>
            - recently: 0 | 1 = <default> 💡 是否为最近
        """
        api = complete_url(base_url=base_url, query={"ct": "note"})
        if isinstance(payload, int):
            payload = {"start": payload}
        payload = {
            "ac": "all",
            "cid": 0,
            "has_picknews": 1,
            "page_size": 1150,
            "start": 0,
            **payload,
        }
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def note_list2(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_list2(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_list2(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取备忘（记录/笔记/记事）列表

        GET https://note.115.com/api/2.0/api.php?ac=note_list

        :payload:
            - start: int = 0    💡 开始索引，从 0 开始
            - limit: int = 1150 💡 分页大小
            - cid: int = 0      💡 分类 id：0:全部 -10:云收藏 -15:消息备忘
            - only_public: 0 | 1 = <default>
            - msg_note: 0 | 1 = <default>
            - has_picknews: 0 | 1 = <default>
        """
        api = complete_url(
            "/api/2.0/api.php", base_url=base_url, query={"ac": "note_list"}
        )
        if isinstance(payload, int):
            payload = {"start": payload}
        payload = {
            "cid": 0,
            "has_picknews": 1,
            "page_size": 1150,
            "start": 0,
            **payload,
        }
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def note_save(
        self,
        payload: str | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_save(
        self,
        payload: str | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_save(
        self,
        payload: str | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """保存备忘（记录/笔记/记事）

        POST https://note.115.com/?ct=note&ac=save

        :payload:
            - nid: int = <default>       💡 记录 id，如果提供就是更新，否则就是新建
            - content: str = <default>   💡 记录的文本，最多 50000 个字符
            - title: str = <default>     💡 标题，最多 927 个字节，可以为空
            - cid: int = 0               💡 分类 id
            - is_html: 0 | 1 = 0         💡 是否 HTML，如果为 1，则会自动加上标签（例如 <p>），以使内容成为合法的 HTML
            - pickcodes: str = <default> 💡 附件的提取码，多个用逗号 "," 隔开
            - tags: str = <default>      💡 标签文本
            - tags[]: str = <default>    💡 标签文本（多个用 "[]" 后缀）
            - ...
            - tags[0]: str = <default>   💡 标签文本（多个用 "[0]","[1]",... 后缀）
            - tags[1]: str = <default>   💡 标签文本
            - ...
            - toc_ids: int | str = <default>
        """
        api = complete_url(base_url=base_url, query={"ct": "note", "ac": "save"})
        if isinstance(payload, str):
            payload = {"content": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_save2(
        self,
        payload: str | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_save2(
        self,
        payload: str | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_save2(
        self,
        payload: str | dict | list,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """编辑备忘（记录/笔记/记事）

        POST https://note.115.com/api/2.0/api.php?ac=note_edit

        :payload:
            - nid: int = <default>       💡 记录 id，如果提供就是更新，否则就是新建
            - content: str = <default>   💡 记录的文本，最多 50000 个字符
            - title: str = <default>     💡 标题，最多 927 个字节，可以为空
            - cid: int = <default>       💡 分类 id
            - is_html: 0 | 1 = <default> 💡 是否 HTML，如果为 1，则会自动加上标签（例如 <p>），以使内容成为合法的 HTML
            - pickcodes: str = <default> 💡 附件的提取码，多个用逗号 "," 隔开
            - tags: str = <default>      💡 标签文本
            - tags[]: str = <default>    💡 标签文本（多个用 "[]" 后缀）
            - ...
            - tags[0]: str = <default>   💡 标签文本（多个用 "[0]","[1]",... 后缀）
            - tags[1]: str = <default>   💡 标签文本
            - ...
        """
        api = complete_url(
            "/api/2.0/api.php", base_url=base_url, query={"ac": "note_edit"}
        )
        if isinstance(payload, str):
            payload = {"content": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_search(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_search(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_search(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """搜索备忘（记录/笔记/记事）

        .. note::
            这个接口支持 GET 和 POST 请求方法

        GET https://note.115.com/api/2.0/api.php?ac=search

        :payload:
            - q: str 💡 搜索词
            - start: int = 0          💡 开始索引，从 0 开始
            - limit: int = 1150       💡 最多返回数量
            - count: int = <default>
            - cid: int = 0            💡 分类 id
            - has_picknews: 0 | 1 = 1 💡 是否显示 id 为负数的分类
            - create_time1: str = <default>
            - create_time2: str = <default>
            - start_time: str = <default>    💡 开始日期，格式为 YYYY-MM-DD
            - end_time: str = <default>      💡 结束日期（含），格式为 YYYY-MM-DD
            - tag_arr: str = <default>    💡 标签文本
            - tag_arr[]: str = <default>  💡 标签文本（多个用 "[]" 后缀）
            - ...
            - tag_arr[0]: str = <default> 💡 标签文本（多个用 "[0]","[1]",... 后缀）
            - tag_arr[1]: str = <default> 💡 标签文本
            - ...
        """
        api = complete_url(
            "/api/2.0/api.php", base_url=base_url, query={"ac": "search"}
        )
        if isinstance(payload, str):
            payload = {"q": payload}
        payload = {"has_picknews": 1, "limit": 1150, "start": 0, **payload}
        if request_kwargs.get("method", "").upper() == "POST":
            return self.request(url=api, data=payload, async_=async_, **request_kwargs)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def note_set_cate(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_set_cate(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_set_cate(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """修改记录的分类

        POST https://note.115.com/?ct=note&ac=update_note_cate

        :payload:
            - cid: int 💡 分类 id
            - nid: int | str 💡 记录 id，多个用逗号 "," 隔开
        """
        api = complete_url(
            base_url=base_url, query={"ct": "note", "ac": "update_note_cate"}
        )
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_set_cate2(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_set_cate2(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_set_cate2(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """修改记录的分类

        POST https://note.115.com/api/2.0/api.php?ac=set_note_cate

        :payload:
            - cid: int 💡 分类 id
            - nid: int | str 💡 记录 id，多个用逗号 "," 隔开
        """
        api = complete_url(
            "/api/2.0/api.php", base_url=base_url, query={"ac": "set_note_cate"}
        )
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_set_tag(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_set_tag(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_set_tag(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """修改记录的标签

        POST https://note.115.com/api/2.0/api.php?ac=set_tag

        :payload:
            - nid: int    💡 记录 id
            - tags: str   💡 标签文本
            - tags[]: str 💡 标签文本（多个用 "[]" 后缀）
            - ...
            - tags[0]: str 💡 标签文本（多个用 "[0]","[1]",... 后缀）
            - tags[1]: str 💡 标签文本
            - ...
            - has_picknews: 0 | 1 = <default>
        """
        api = complete_url(
            "/api/2.0/api.php", base_url=base_url, query={"ac": "set_tag"}
        )
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_tag_color(
        self,
        payload: str | Iterable[str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_tag_color(
        self,
        payload: str | Iterable[str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_tag_color(
        self,
        payload: str | Iterable[str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """上传标签，返回标签并提供颜色

        POST https://note.115.com/api/2.0/api.php?ac=get_tag_color

        :payload:
            - tags: str = <default>    💡 标签文本
            - tags[]: str = <default>  💡 标签文本（多个用 "[]" 后缀）
            - ...
            - tags[0]: str = <default> 💡 标签文本（多个用 "[0]","[1]",... 后缀）
            - tags[1]: str = <default> 💡 标签文本
            - ...
        """
        api = complete_url(
            "/api/2.0/api.php", base_url=base_url, query={"ac": "get_tag_color"}
        )
        if isinstance(payload, str):
            payload = {"tags": payload}
        elif (
            payload
            and not isinstance(payload, dict)
            and not (isinstance(payload, Sequence) and not isinstance(payload[0], str))
        ):
            payload = {f"tags[{i}]": t for i, t in enumerate(payload)}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def note_tag_latest(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_tag_latest(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_tag_latest(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取最近使用的标签

        .. note::
            这个接口支持 GET 和 POST 请求方法

        GET https://note.115.com/api/2.0/api.php?ac=get_latest_tags

        :payload:
            - q: str = ""                💡 搜索词
            - is_return_color: 0 | 1 = 1 💡 是否返回颜色
            - limit: int = 1150          💡 最多返回数量
        """
        api = complete_url(
            "/api/2.0/api.php", base_url=base_url, query={"ac": "get_latest_tags"}
        )
        if isinstance(payload, str):
            payload = {"q": payload}
        payload = {"is_return_color": 1, "limit": 1150, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def note_user_setting(
        self,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_user_setting(
        self,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_user_setting(
        self,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取记录的列表展示的配置(目前只有【每页数量设置】）

        GET https://note.115.com/?ct=note&ac=get_user_setting
        """
        api = complete_url(
            base_url=base_url, query={"ct": "note", "ac": "get_user_setting"}
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def note_user_setting_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def note_user_setting_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def note_user_setting_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://note.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """修改记录的列表展示的配置

        POST https://note.115.com/?ct=note&ac=set_user_setting

        :payload:
            - note_page_size: 20 | 25 | 50 | 100 💡 每页数量设置
        """
        api = complete_url(
            base_url=base_url, query={"ct": "note", "ac": "set_user_setting"}
        )
        if isinstance(payload, int):
            payload = {"note_page_size": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def photo_album(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_album(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_album(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取相册信息

        GET https://webapi.115.com/photo/album

        :payload:
            - album_id: int | str 💡 相册 id，如果为 -1，则是【默认加密相册】
        """
        api = complete_url("/photo/album", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"album_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def photo_album_add(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_album_add(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_album_add(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """新建相册

        POST https://webapi.115.com/photo/albumadd

        :payload:
            - album_name: str = <default> 💡 相册名称
            - album_desc: str = <default> 💡 相册描述
            - is_secret: 0 | 1 = <default> 💡 是否加密
        """
        api = complete_url("/photo/albumadd", base_url=base_url)
        if isinstance(payload, str):
            payload = {"album_name": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def photo_album_group(
        self,
        payload: dict = {},
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_album_group(
        self,
        payload: dict = {},
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_album_group(
        self,
        payload: dict = {},
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取相册分组

        GET https://webapi.115.com/photo/albumgroup

        :payload:
            - home_page: 0 | 1 = 1
            - limit: int = 100
        """
        api = complete_url("/photo/albumgroup", base_url=base_url)
        payload = {"home_page": 1, "limit": 100, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def photo_album_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_album_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_album_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取相册列表

        GET https://webapi.115.com/photo/albumlist

        :payload:
            - offset: int = 0   💡 开始索引，从 0 开始
            - limit: int = 9999 💡 最多返回数量
            - album_type: int = 1💡 相册类型。已知：

                - 1: 个人相册
                - 5: 应用相册
                - 6: 加密相册
        """
        api = complete_url("/photo/albumlist", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload = {"album_type": 1, "limit": 9999, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def photo_album_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_album_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_album_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """更新相册

        POST https://webapi.115.com/photo/album

        :payload:
            - album_id: int | str 💡 相册 id，如果为 -1，则是【默认加密相册】
            - album_name: str = <default> 💡 相册名称
            - album_desc: str = <default> 💡 相册描述
            - album_state: 0 | 1 = <default> 💡 是否删除：0:保留 1:删除
            - is_secret: 0 | 1 = <default> 💡 是否加密
        """
        api = complete_url("/photo/album", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def photo_bind(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_bind(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_bind(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """把图片或视频转存到相册

        POST https://webapi.115.com/photo/photo

        .. note::
            虽然被认为是图片的格式很多（你可以用这个方法 `client.fs_files_second_type({"type": 2})` 获得网盘中的所有图片格式），但仅支持以下格式图片添加到相册：jpg,jpeg,png,gif,svg,webp,heic,bmp,dng

        .. caution::
            添加到相册，其实就是复制到 "/手机相册" 目录，如果需要删除，就直接用 ``fs_delete`` 即可

        :payload:
            - file_ids: int | str 💡 文件 id，多个用逗号 "," 隔开
            - to_album_id: int | str = 1 💡 相册 id

                - -1: 添加到【默认加密相册】
                -  1: 添加到照片

            - action: str = "addtoalbum" 💡 动作

                - "addtoalbum": 添加到相册
        """
        api = complete_url("/photo/photo", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_ids": payload}
        elif not isinstance(payload, dict):
            payload = {"file_ids": ",".join(map(str, payload))}
        payload = {"action": "addtoalbum", "to_album_id": 1, **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def photo_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取相册的文件列表

        GET https://webapi.115.com/photo/photolist

        :payload:
            - offset: int = 0   💡 开始索引，从 0 开始
            - limit: int = 1150 💡 最多返回数量
            - album_id: int | str = <default> 💡 相册 id。如果为 -1，则是【默认加密相册】；如果不指定，则是所有相册
            - key_word: str = <default>
            - type: int = <default>
            - tr: str = <default> 💡 时间线，是一个日期，格式为 YYYYMMDD
            - order: str = <default> 💡 排序依据，例如 "add_time"
            - is_asc: 0 | 1 = <default> 💡 是否升序排列
        """
        api = complete_url("/photo/photolist", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload.setdefault("limit", 1150)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def photo_sharealbum(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_sharealbum(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_sharealbum(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取共享相册信息

        GET https://webapi.115.com/photo/sharealbum

        :payload:
            - album_id: int | str 💡 相册 id
        """
        api = complete_url("/photo/sharealbum", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"album_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def photo_sharealbum_add(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_sharealbum_add(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_sharealbum_add(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """新建共享相册

        POST https://webapi.115.com/photo/sharealbumadd

        :payload:
            - album_name: str = <default> 💡 相册名称
            - album_desc: str = <default> 💡 相册描述
        """
        api = complete_url("/photo/sharealbumadd", base_url=base_url)
        if isinstance(payload, str):
            payload = {"album_name": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def photo_sharealbum_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_sharealbum_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_sharealbum_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取共享相册列表

        GET https://webapi.115.com/photo/sharealbumlist

        :payload:
            - offset: int = 0   💡 开始索引，从 0 开始
            - limit: int = 1150 💡 最多返回数量
            - is_asc: 0 | 1 = <default> 💡 是否升序排列
            - order: str = <default> 💡 排序依据，例如 "update_time"
        """
        api = complete_url("/photo/sharealbumlist", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload = {"limit": 1150, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def photo_sharealbum_member(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_sharealbum_member(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_sharealbum_member(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取共享相册的成员用户列表

        GET https://webapi.115.com/photo/sharealbummember

        :payload:
            - album_id: int | str = <default> 💡 相册 id
            - order: str = <default> 💡 排序依据，例如 "join_time"
            - is_asc: 0 | 1 = <default> 💡 是否升序排列
        """
        api = complete_url("/photo/sharealbummember", base_url=base_url)
        if isinstance(payload, int):
            payload = {"album_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def photo_sharealbum_record_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_sharealbum_record_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_sharealbum_record_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取共享相册的操作记录列表

        GET https://webapi.115.com/photo/sharealbumrecordlist

        :payload:
            - offset: int = 0     💡 开始索引，从 0 开始
            - limit: int = 1150   💡 最多返回数量
            - album_id: int | str = <default> 💡 相册 id
        """
        api = complete_url("/photo/sharealbumrecordlist", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload = {"limit": 1150, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def photo_sharealbum_record_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_sharealbum_record_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_sharealbum_record_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """在共享相册中增加或删除 1 条记录

        POST https://webapi.115.com/photo/sharealbumrecord

        :payload:
            - album_id: int | str 💡 相册 id
            - action: "add" | "del" 💡 操作。"add":添加记录 "del":删除记录
            - record_id: int | str = <default> 💡 记录 id
            - record_content: str = <default> 💡 记录的描述文本
            - file_ids: int | str = <default> 💡 记录关联的（在网盘中的）文件 id，多个用逗号 "," 隔开
        """
        api = complete_url("/photo/sharealbumrecord", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def photo_sharealbum_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_sharealbum_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_sharealbum_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """更新共享相册

        POST https://webapi.115.com/photo/sharealbum

        :payload:
            - album_id: int | str 💡 相册 id
            - album_name: str = <default>  💡 相册名称
            - album_desc: str = <default>  💡 相册描述
            - album_cover: str = <default> 💡 相册封面，图片的 sha1 值
            - album_state: 0 | 1 = <default> 💡 是否删除：0:保留 1:删除
            - is_top: 0 | 1 = <default> 💡 是否置顶
            - user_nick_name: str = <default> 💡 用户昵称
        """
        api = complete_url("/photo/sharealbum", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def photo_share_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_share_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_share_list(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取共享相册的图片列表

        GET https://webapi.115.com/photo/sharephotolist

        :payload:
            - offset: int = 0   💡 开始索引，从 0 开始
            - limit: int = 1150 💡 最多返回数量
            - album_id: int | str = <default> 💡 相册 id
            - record_id: int | str = <default> 💡 操作记录 id
            - key_word: str = <default>
            - type: int = <default>
            - tr: str = <default> 💡 时间线，是一个日期，格式为 YYYYMMDD
            - order: str = <default> 💡 排序依据，例如 "add_time"
            - is_asc: 0 | 1 = <default> 💡 是否升序排列
        """
        api = complete_url("/photo/sharephotolist", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload.setdefault("limit", 1150)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def photo_share_remove(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_share_remove(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_share_remove(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """把共享相册的图片移除

        POST https://webapi.115.com/photo/sharephoto

        :payload:
            - album_id: int | str 💡 相册 id
            - photo_ids: int | str = <default> 💡 （在相册中的）图片 id，多个用逗号 "," 隔开
        """
        api = complete_url("/photo/sharephoto", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def photo_share_save(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_share_save(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_share_save(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """把共享相册的图片保存到照片库

        POST https://webapi.115.com/photo/sharephotosave

        :payload:
            - album_id: int | str 💡 相册 id
            - photo_ids: int | str = <default> 💡 （在相册中的）图片 id，多个用逗号 "," 隔开
        """
        api = complete_url("/photo/sharephotosave", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def photo_share_timeline(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_share_timeline(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_share_timeline(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取共享相册的时间线列表，然后你可以通过 `client.photo_share_list` 获取对应时间线的图片列表

        GET https://webapi.115.com/photo/sharephototimeline

        :payload:
            - offset: int = 0    💡 开始索引，从 0 开始
            - limit: int = 99999 💡 最多返回数量
            - album_id: int | str = <default> 💡 相册 id。如果为 -1，则是【默认加密相册】；如果不指定，则是所有相册
            - key_word: str = <default>
        """
        api = complete_url("/photo/sharephototimeline", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload.setdefault("limit", 99999)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def photo_timeline(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def photo_timeline(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def photo_timeline(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取时间线列表，然后你可以通过 `client.photo_list` 获取对应时间线的图片列表

        GET https://webapi.115.com/photo/phototimeline

        :payload:
            - offset: int = 0    💡 开始索引，从 0 开始
            - limit: int = 99999 💡 最多返回数量
            - album_id: int | str = <default> 💡 相册 id。如果为 -1，则是【默认加密相册】；如果不指定，则是所有相册
            - key_word: str = <default>
        """
        api = complete_url("/photo/phototimeline", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload.setdefault("limit", 99999)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def tool_clear_empty_folder(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def tool_clear_empty_folder(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def tool_clear_empty_folder(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除空目录

        GET https://115.com/?ct=tool&ac=clear_empty_folder
        """
        api = complete_url(
            base_url=base_url, query={"ct": "tool", "ac": "clear_empty_folder"}
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def tool_repeat(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def tool_repeat(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def tool_repeat(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """开始一键排重任务

        POST https://aps.115.com/repeat/repeat.php

        :payload:
            - folder_id: int | str 💡 目录 id，对应 parent_id
        """
        api = complete_url("/repeat/repeat.php", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"folder_id": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def tool_repeat_delete(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def tool_repeat_delete(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def tool_repeat_delete(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除重复文件

        POST https://aps.115.com/repeat/repeat_delete.php

        :payload:
            - filter_field: "parents" | "file_name" | "" | "" = <default> 💡 保留条件（1. 用于批量删除）

                - "file_name": 文件名（按长度）
                - "parents": 所在目录路径（按长度）
                - "user_utime": 操作时间
                - "user_ptime": 创建时间

            - filter_order: "asc" | "desc" = <default> 💡 排序（2. 用于批量删除）

                - "asc": 升序，从小到大，取最小
                - "desc": 降序，从大到小，取最大

            - batch: 0 | 1 = <default> 💡 是否批量操作（3. 用于批量删除）
            - sha1s[{sha1}]: int | str = <default> 💡 文件 id，多个用逗号 "," 隔开（1. 用于手动指定删除对象）
        """
        api = complete_url("/repeat/repeat_delete.php", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def tool_repeat_delete_status(
        self,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def tool_repeat_delete_status(
        self,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def tool_repeat_delete_status(
        self,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除重复文件进度和统计信息（status 为 False 表示进行中，为 True 表示完成）

        GET https://aps.115.com/repeat/delete_status.php
        """
        api = complete_url("/repeat/delete_status.php", base_url=base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def tool_repeat_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def tool_repeat_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def tool_repeat_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取重复文件列表

        GET https://aps.115.com/repeat/repeat_list.php

        :payload:
            - s: int = 0 💡 offset，从 0 开始
            - l: int = 100 💡 limit
        """
        api = complete_url("/repeat/repeat_list.php", base_url=base_url)
        if isinstance(payload, int):
            payload = {"l": 100, "s": payload}
        else:
            payload = {"s": 0, "l": 100, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def tool_repeat_status(
        self,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def tool_repeat_status(
        self,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def tool_repeat_status(
        self,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """查询一键排重任务进度和统计信息（status 为 False 表示进行中，为 True 表示完成）

        GET https://aps.115.com/repeat/repeat_status.php
        """
        api = complete_url("/repeat/repeat_status.php", base_url=base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def tool_space(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def tool_space(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def tool_space(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """检验空间

        GET https://115.com/?ct=tool&ac=space

        .. hint::
            1. 校验空间需全局进行扫描，请谨慎操作;
            2. 扫描出无父目录的文件将统一放入到"/修复文件"的目录中;
            3. "/修复文件"的目录若超过存放文件数量限制，将创建多个目录存放，避免无法操作。
            4. 此接口一天只能使用一次
        """
        api = complete_url(base_url=base_url, query={"ct": "tool", "ac": "space"})
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    @staticmethod
    def _init_file(
        file: (
            Buffer
            | str
            | PathLike
            | URL
            | SupportsGeturl
            | SupportsRead
            | Iterable[Buffer]
        ),
        filename: str = "",
        *,
        async_: Literal[False] = False,
    ) -> SupportsRead: ...

    @overload
    @staticmethod
    def _init_file(
        file: (
            Buffer
            | str
            | PathLike
            | URL
            | SupportsGeturl
            | SupportsRead
            | Iterable[Buffer]
            | AsyncIterable[Buffer]
        ),
        filename: str = "",
        *,
        async_: Literal[True],
    ) -> Coroutine[Any, Any, SupportsRead]: ...

    @staticmethod
    def _init_file(
        file: (
            Buffer
            | str
            | PathLike
            | URL
            | SupportsGeturl
            | SupportsRead
            | Iterable[Buffer]
            | AsyncIterable[Buffer]
        ),
        filename: str = "",
        *,
        async_: Literal[False, True] = False,
    ) -> SupportsRead | Coroutine[Any, Any, SupportsRead]:
        def gen_step():
            nonlocal file, filename
            if isinstance(file, SupportsRead):
                if not filename:
                    from os.path import basename

                    filename = getattr(file, "name", "")
                    filename = basename(filename)
            elif not isinstance(file, Buffer):
                path = file
                is_url: None | bool = None
                if isinstance(path, str):
                    is_url = path.startswith(("http://", "https://"))
                elif isinstance(path, (URL, SupportsGeturl)):
                    is_url = True
                    if isinstance(path, URL):
                        path = str(path)
                    else:
                        path = path.geturl()
                elif isinstance(path, PathLike):
                    is_url = False
                    path = fsdecode(path)
                if is_url is not None:
                    path = cast(str, path)
                    if is_url:
                        if async_:

                            async def process():
                                return await AsyncHTTPFileReader.new(
                                    cast(str, path),
                                    headers={
                                        "user-agent": "",
                                        "accept-encoding": "identity",
                                    },
                                )

                            file = yield process()
                        else:
                            from fundrives.pan115._vendor.httpfile import HTTPFileReader

                            file = HTTPFileReader(
                                path,
                                headers={
                                    "user-agent": "",
                                    "accept-encoding": "identity",
                                },
                            )
                        file = cast(HTTPFileReader, file)
                        if not filename:
                            filename = file.name
                    else:
                        file = open(path, "rb")
                    if not filename:
                        if is_url:
                            from posixpath import basename
                            from urllib.parse import unquote

                            filename = basename(unquote(urlsplit(path).path))
                        else:
                            from os.path import basename

                            filename = basename(path)
            return file, filename

        return run_gen_step(gen_step, async_)
