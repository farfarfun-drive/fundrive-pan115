#!/usr/bin/env python3

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Self, cast, overload

from .open_client import P115OpenClient

if TYPE_CHECKING:
    from . import P115Client

from ._common import (
    SSOENT_TO_APP,
    Callable,
    ClientRequestMixin,
    Coroutine,
    P115Warning,
    check_response,
    complete_url,
    get_request,
    itemgetter,
    json_maybe_decrypt_loads,
    md5,
    md5_secret_password,
    run_gen_step,
    sha1,
    time,
    warn,
)


class _P115ClientAccountMixin:
    """登录、账号、VIP、设备与社交接口混入。"""

    @overload
    def login_with_app(
        self,
        /,
        app: None | str = None,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def login_with_app(
        self,
        /,
        app: None | str = None,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def login_with_app(
        self,
        /,
        app: None | str = None,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """执行一次自动扫登录二维码，然后绑定到指定设备

        :param app: 绑定的 `app` （或者叫 `device`），如果为 None 或 ""，则和当前 client 的登录设备相同
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 响应信息，包含 cookies

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
            if not app:
                app = yield self.login_app(async_=async_, **request_kwargs)
            if not app:
                raise ValueError("can't determine the login app")
            uid: str = yield self.login_without_app(async_=async_, **request_kwargs)
            return self.login_qrcode_scan_result(
                uid,
                app=app,
                async_=async_,
                **request_kwargs,
            )

        return run_gen_step(gen_step, async_)

    @overload
    def login_without_app(
        self,
        /,
        show_warning: bool = False,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> str: ...

    @overload
    def login_without_app(
        self,
        /,
        show_warning: bool = False,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, str]: ...

    def login_without_app(
        self,
        /,
        show_warning: bool = False,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> str | Coroutine[Any, Any, str]:
        """执行一次自动扫登录二维码，但不绑定设备，返回扫码的 uid，可用于之后绑定设备

        :param show_warning: 是否显示提示信息
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 二维码的 uid
        """

        def gen_step():
            uid = check_response(
                (
                    yield self.login_qrcode_token(  # type: ignore
                        async_=async_,
                        **request_kwargs,
                    )
                )
            )["data"]["uid"]
            resp = yield self.login_qrcode_scan(
                uid,
                async_=async_,
                **request_kwargs,
            )
            check_response(resp)
            if show_warning:
                warn(f"qrcode scanned: {resp}", category=P115Warning)
            resp = yield self.login_qrcode_scan_confirm(
                uid,
                async_=async_,
                **request_kwargs,
            )
            check_response(resp)
            return uid

        return run_gen_step(gen_step, async_)

    @overload
    def login_info_open(
        self,
        /,
        app_id: int = 0,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def login_info_open(
        self,
        /,
        app_id: int = 0,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def login_info_open(
        self,
        /,
        app_id: int = 0,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取某个开放接口应用的信息（目前可获得名称和头像）

        :param app_id: AppID
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 接口返回值
        """
        if not app_id:
            app_id = self.app_id
        if not app_id:
            app_id = 100195125

        def gen_step():
            resp = yield self.login_qrcode_token_open(
                app_id, async_=async_, **request_kwargs
            )
            check_response(resp)
            login_uid = resp["data"]["uid"]
            resp = yield self.login_qrcode_scan(
                login_uid, async_=async_, **request_kwargs
            )
            check_response(resp)
            tip_txt = resp["data"]["tip_txt"]
            return {
                "app_id": app_id,
                "name": tip_txt[:-10].removeprefix("\ufeff"),
                "icon": resp["data"]["icon"],
            }

        return run_gen_step(gen_step, async_)

    @overload
    def login_with_open(
        self,
        /,
        app_id: int = 0,
        *,
        show_warning: bool = False,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def login_with_open(
        self,
        /,
        app_id: int = 0,
        *,
        show_warning: bool = False,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def login_with_open(
        self,
        /,
        app_id: int = 0,
        *,
        show_warning: bool = False,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """登录某个开放接口应用

        .. note::
            同一个开放应用 id，最多同时有 3 个登入，如果有新的登录，则自动踢掉较早的那一个

        :param app_id: AppID
        :param show_warning: 是否显示提示信息
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 接口返回值
        """
        if not app_id:
            app_id = self.app_id
        if not app_id:
            app_id = 100195125

        def gen_step():
            resp = yield self.login_qrcode_token_open(
                app_id, async_=async_, **request_kwargs
            )
            check_response(resp)
            login_uid = resp["data"]["uid"]
            resp = yield self.login_qrcode_scan(
                login_uid, async_=async_, **request_kwargs
            )
            check_response(resp)
            if show_warning:
                warn(f"qrcode scanned: {resp}", category=P115Warning)
            resp = yield self.login_qrcode_scan_confirm(
                login_uid, async_=async_, **request_kwargs
            )
            check_response(resp)
            return self.login_qrcode_access_token_open(
                login_uid, async_=async_, **request_kwargs
            )

        return run_gen_step(gen_step, async_)

    @overload
    def login_another_app(
        self,
        /,
        app: None | str = None,
        replace: bool | Self = False,
        show_warning: bool = False,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> Self: ...

    @overload
    def login_another_app(
        self,
        /,
        app: None | str = None,
        replace: bool | Self = False,
        show_warning: bool = False,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, Self]: ...

    def login_another_app(
        self,
        /,
        app: None | str = None,
        replace: bool | Self = False,
        show_warning: bool = False,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> Self | Coroutine[Any, Any, Self]:
        """登录某个设备（同一个设备可以有多个同时在线，但可以通过某些操作，把除了最近登录的那个都下线，也可以专门把最近登录那个也下线）

        .. hint::
            一个设备被新登录者下线，意味着这个 cookies 失效了，不能执行任何需要权限的操作

            但一个设备的新登录者，并不总是意味着把较早的登录者下线，一般需要触发某个检查机制后，才会把同一设备下除最近一次登录外的所有 cookies 失效

            所以你可以用一个设备的 cookies 专门用于扫码登录，获取另一个设备的 cookies 执行网盘操作，第 2 个 cookies 失效了，则用第 1 个 cookies 扫码，如此可避免单个 cookies 失效后，不能自动获取新的

        :param app: 要登录的 app，如果为 None，则用当前登录设备，如果无当前登录设备，则报错
        :param replace: 替换某个 ``P115Client`` 对象的 cookie

            - 如果为 ``P115Client``, 则更新到此对象
            - 如果为 True，则更新到 `self`
            - 如果为 False，否则返回新的 ``P115Client`` 对象

        :param show_warning: 是否显示提示信息
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 客户端实例

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
            from . import P115Client

            if not app and isinstance(replace, P115Client):
                app = yield replace.login_app(async_=True)
            resp = yield self.login_with_app(
                app,
                show_warning=show_warning,
                async_=async_,
                **request_kwargs,
            )
            check_response(resp)
            cookies = resp["data"]["cookie"]
            ssoent = self.login_ssoent
            if isinstance(replace, P115Client):
                inst = replace
                inst.update_cookies(cookies)
            elif replace:
                inst = self
                inst.update_cookies(cookies)
            else:
                inst = type(self)(cookies)
            if self is not inst and ssoent == inst.login_ssoent:
                warn(
                    f"login with the same ssoent {ssoent!r}, {self!r} will expire within 60 seconds",
                    category=P115Warning,
                )
            return inst

        return run_gen_step(gen_step, async_)

    @overload
    def login_another_open(
        self,
        /,
        app_id: int = 0,
        replace: bool | P115OpenClient = False,
        show_warning: bool = False,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> P115OpenClient: ...

    @overload
    def login_another_open(
        self,
        /,
        app_id: int = 0,
        replace: bool | P115OpenClient = False,
        show_warning: bool = False,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, P115OpenClient]: ...

    def login_another_open(
        self,
        /,
        app_id: int = 0,
        replace: bool | P115OpenClient = False,
        show_warning: bool = False,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> P115OpenClient | Coroutine[Any, Any, P115OpenClient]:
        """登录某个开放接口应用

        .. note::
            同一个开放应用 id，最多同时有 3 个登入，如果有新的登录，则自动踢掉较早的那一个

        :param app_id: AppID
        :param replace: 替换某个 client 对象的 `access_token` 和 `refresh_token`

            - 如果为 ``P115Client``, 则更新到此对象
            - 如果为 True，则更新到 `self`
            - 如果为 False，否则返回新的 ``P115Client`` 对象

        :param show_warning: 是否显示提示信息
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 客户端实例
        """
        if not app_id:
            app_id = self.app_id
        if not app_id:
            app_id = 100195125

        def gen_step():
            resp = yield self.login_with_open(
                app_id,
                show_warning=show_warning,
                async_=async_,
                **request_kwargs,
            )
            check_response(resp)
            from . import P115Client

            data = resp["data"]
            if replace is False:
                inst: P115OpenClient = P115OpenClient(
                    data["access_token"], data["refresh_token"]
                )
            else:
                if replace is True:
                    inst = self
                else:
                    inst = replace
                inst.refresh_token = data["refresh_token"]
                inst.access_token = data["access_token"]
            inst.app_id = app_id
            return inst

        return run_gen_step(gen_step, async_)

    @overload
    @classmethod
    def login_bind_app(
        cls,
        /,
        uid: str,
        app: str = "alipaymini",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> Self: ...

    @overload
    @classmethod
    def login_bind_app(
        cls,
        /,
        uid: str,
        app: str = "alipaymini",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, Self]: ...

    @classmethod
    def login_bind_app(
        cls,
        /,
        uid: str,
        app: str = "alipaymini",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> Self | Coroutine[Any, Any, Self]:
        """获取绑定到某个设备的 cookies

        .. hint::
            同一个设备可以有多个 cookies 同时在线

            其实只要你不主动去执行检查，这些 cookies 可以同时生效，只是看起来像“黑户”

        :param uid: 登录二维码的 uid
        :param app: 待绑定的设备名称
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 新的实例

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
            resp = yield cls.login_qrcode_scan_result(
                uid,
                app=app,
                async_=async_,
                **request_kwargs,
            )
            check_response(resp)
            cookies = resp["data"]["cookie"]
            return cls(cookies)

        return run_gen_step(gen_step, async_)

    @overload
    def login_app(
        self,
        /,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> None | str: ...

    @overload
    def login_app(
        self,
        /,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, None | str]: ...

    def login_app(
        self,
        /,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> None | str | Coroutine[Any, Any, None | str]:
        """获取当前的登录设备名，如果为 None，说明未能获得"""

        def gen_step():
            ssoent = self.login_ssoent
            if not ssoent:
                return None
            if ssoent in SSOENT_TO_APP:
                return SSOENT_TO_APP[ssoent]
            device = yield self.login_device(async_=async_, **request_kwargs)
            if device is None:
                return None
            return device["icon"]

        return run_gen_step(gen_step, async_)

    @overload
    def login_open_auth_detail(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def login_open_auth_detail(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def login_open_auth_detail(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取某个开放应用的授权信息

        GET https://qrcodeapi.115.com/app/1.0/{app}/1.0/user/getAppAuthDetail

        :payload:
            - auth_id: int | str 💡 授权 id
        """
        api = complete_url(
            f"/app/1.0/{app}/1.0/user/getAppAuthDetail", base_url=base_url
        )
        if isinstance(payload, (int, str)):
            payload = {"auth_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def login_open_auth_list(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def login_open_auth_list(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def login_open_auth_list(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取所有授权的开放应用的列表

        GET https://qrcodeapi.115.com/app/1.0/{app}/1.0/user/getAppAuthList
        """
        api = complete_url(f"/app/1.0/{app}/1.0/user/getAppAuthList", base_url=base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def login_open_deauth(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def login_open_deauth(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def login_open_deauth(
        self,
        payload: int | str | dict,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """取消某个开放应用的授权

        GET https://qrcodeapi.115.com/app/1.0/{app}/1.0/user/deauthApp

        :payload:
            - auth_id: int | str 💡 授权 id
        """
        api = complete_url(f"/app/1.0/{app}/1.0/user/deauthApp", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"auth_id": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def login_check_sso(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def login_check_sso(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def login_check_sso(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """检查当前 cookies 的登录状态信息，并且自最近一次登录的 60 秒后，使当前设备下除最近一次登录外的所有 cookies 失效

        GET https://qrcodeapi.115.com/app/1.0/{app}/1.0/check/sso
        """
        api = complete_url(f"/app/1.0/{app}/1.0/check/sso", base_url=base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def login_device(
        self,
        /,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> None | dict: ...

    @overload
    def login_device(
        self,
        /,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, None | dict]: ...

    def login_device(
        self,
        /,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> None | dict | Coroutine[Any, Any, None | dict]:
        """获取当前的登录设备的信息，如果为 None，也不代表当前的 cookies 被下线，只能说明有更晚的登录到同一设备"""

        def parse(_, content: bytes, /) -> None | dict:
            login_devices = json_maybe_decrypt_loads(content)
            if not login_devices["state"]:
                return None
            return next(
                filter(
                    cast(Callable, itemgetter("is_current")),
                    login_devices["data"]["list"],
                ),
                None,
            )

        request_kwargs.setdefault("parse", parse)
        return self.login_devices(async_=async_, **request_kwargs)

    @overload
    def login_devices(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def login_devices(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def login_devices(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取所有的已登录设备的信息，不过当前的 cookies 必须是登录状态（未退出或未失效）

        GET https://qrcodeapi.115.com/app/1.0/{app}/1.0/login_log/login_devices
        """
        api = complete_url(
            f"/app/1.0/{app}/1.0/login_log/login_devices", base_url=base_url
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def login_info(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def login_info(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def login_info(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取登录信息

        GET https://proapi.115.com/{app}/2.0/login_info
        """
        api = complete_url("/2.0/login_info", base_url=base_url, app=app)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def login_log(
        self,
        payload: dict = {},
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def login_log(
        self,
        payload: dict = {},
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def login_log(
        self,
        payload: dict = {},
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取登录信息日志列表

        GET https://qrcodeapi.115.com/app/1.0/{app}/1.0/login_log/log

        :payload:
            - start: int = 0
            - limit: int = 100
        """
        api = complete_url(f"/app/1.0/{app}/1.0/login_log/log", base_url=base_url)
        payload = {"start": 0, "limit": 100, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def login_online(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def login_online(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def login_online(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """当前登录的设备总数和最近登录的设备

        GET https://qrcodeapi.115.com/app/1.0/{app}/1.0/login_log/login_online
        """
        api = complete_url(
            f"/app/1.0/{app}/1.0/login_log/login_online", base_url=base_url
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @property
    def login_ssoent(self, /) -> str:
        """获取当前的登录设备 ssoent，如果为空，说明未能获得（会直接获取 Cookies 中名为 UID 字段的值，所以即使能获取，也不能说明登录未失效）"""
        return self.cookies_str.UID.ssoent

    @overload
    def logout(
        self,
        /,
        app: None | str = "android",
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> None: ...

    @overload
    def logout(
        self,
        /,
        app: None | str = "android",
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, None]: ...

    def logout(
        self,
        /,
        app: None | str = "android",
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> None | Coroutine[Any, Any, None]:
        """当前设备退出登录状态

        POST https://qrcodeapi.115.com/app/1.0/{app}/1.0/logout/index

        .. tip::
            无论指定什么 ``app``，都是退出当前 cookies 所对应的登录设备
        """
        api = complete_url(f"/app/1.0/{app}/1.0/logout/index", base_url=base_url)
        return self.request(api, method=method, async_=async_, **request_kwargs)

    @overload
    def logout_by_app(
        self,
        /,
        app: None | str = None,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> None: ...

    @overload
    def logout_by_app(
        self,
        /,
        app: None | str = None,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, None]: ...

    def logout_by_app(
        self,
        /,
        app: None | str = None,
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> None | Coroutine[Any, Any, None]:
        """退出登录状态（可以把某个客户端下线，所有已登录设备可从 `login_devices` 获取）

        GET https://qrcodeapi.115.com/app/1.0/{app}/1.0/logout/logout

        :param app: 退出登录的 app

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
            if app is None:
                app = yield self.login_app(async_=async_)
            if app == "desktop":
                app = "web"
            api = complete_url(f"/app/1.0/{app}/1.0/logout/logout", base_url=base_url)
            request_kwargs.setdefault("parse", lambda *a: None)
            return self.request(url=api, async_=async_, **request_kwargs)

        return run_gen_step(gen_step, async_)

    @overload
    def logout_by_ssoent(
        self,
        payload: None | str | dict = None,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def logout_by_ssoent(
        self,
        payload: None | str | dict = None,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def logout_by_ssoent(
        self,
        payload: None | str | dict = None,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """退出登录状态（可以把某个客户端下线，所有已登录设备可从 `login_devices` 获取）

        POST https://qrcodeapi.115.com/app/1.0/{app}/1.0/logout/mange

        :payload:
            - ssoent: str

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
        api = complete_url(f"/app/1.0/{app}/1.0/logout/mange", base_url=base_url)
        if payload is None:
            payload = {"ssoent": self.login_ssoent or ""}
        elif isinstance(payload, str):
            payload = {"ssoent": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def user_base_info(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_base_info(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_base_info(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://qrcodeapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取用户的基本信息

        GET https://qrcodeapi.115.com/app/1.0/{app}/1.0/user/base_info
        """
        api = complete_url(f"/app/1.0/{app}/1.0/user/base_info", base_url=base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_card(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_card(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_card(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取用户信息

        GET https://proapi.115.com/{app}/user/card
        """
        api = complete_url("/user/card", base_url=base_url, app=app)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_count_space_nums(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_count_space_nums(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_count_space_nums(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取当前已用空间、可用空间、登录设备等信息

        GET https://proapi.115.com/{app}/2.0/user/count_space_nums
        """
        api = complete_url("/2.0/user/count_space_nums", base_url=base_url, app=app)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_display_uid_list(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_display_uid_list(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_display_uid_list(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """账号信息 VIP 相关信息

        GET https://passportapi.115.com/app/1.0/{app}/1.0/user/display_uid_list
        """
        api = complete_url(
            f"/app/1.0/{app}/1.0/user/display_uid_list", base_url=base_url
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_fingerprint(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_fingerprint(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_fingerprint(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取截图时嵌入的水印

        GET https://webapi.115.com/user/fingerprint
        """
        api = complete_url("/user/fingerprint", base_url=base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload  # type: ignore
    def user_info(
        self: int | str | dict | ClientRequestMixin = 11500,
        payload: None | int | str | dict = None,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_info(
        self: int | str | dict | ClientRequestMixin = 11500,
        payload: None | int | str | dict = None,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_info(
        self: int | str | dict | ClientRequestMixin = 11500,
        payload: None | int | str | dict = None,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取用户信息

        GET https://my.115.com/proapi/3.0/index.php

        .. note::
            可以作为 ``staticmethod`` 使用，但必须指定查询参数 ``uid``

        :payload:
            - uid: int | str
            - method: str = "user_info" 💡 需要获取的数据类别

                - "user_info": 用户信息
                - "get_interests_list": 兴趣列表
                - "get_jobs_list": 工作列表
                - "get_privacy_settings": 隐私资料
                - "get_public": 公开资料
                - "check_secret_token": 隐私令牌
                - ...
        """
        api = complete_url(
            "/proapi/3.0/index.php", base_url=base_url, query={"method": "user_info"}
        )
        if isinstance(self, ClientRequestMixin):
            request_kwargs["self"] = self
            if payload is None:
                if isinstance(self, P115OpenClient):
                    payload = self.user_id
                else:
                    payload = 11500
        else:
            payload = self
        if isinstance(payload, int):
            payload = {"uid": payload}
        elif isinstance(payload, str):
            payload = {"method": payload}
        payload.setdefault("method", "user_info")
        request, request_kwargs = get_request(url=api, params=payload, **request_kwargs)
        return request(async_=async_, **request_kwargs)

    @overload
    def user_info2(
        self,
        payload: int | str | dict = "",
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://home.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_info2(
        self,
        payload: int | str | dict = "",
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://home.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_info2(
        self,
        payload: int | str | dict = "",
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://home.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取用户信息

        GET https://home.115.com/api/1.0/{app}/1.0/user/user_info

        :payload:
            - uid: int | str
        """
        api = complete_url(f"/api/1.0/{app}/1.0/user/user_info", base_url=base_url)
        if not payload:
            payload = {"uid": self.user_id}
        elif not isinstance(payload, dict):
            payload = {"uid": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def user_info3(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_info3(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_info3(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取用户信息

        GET https://my.115.com/?ct=ajax&ac=nav
        """
        api = complete_url(base_url=base_url, query={"ct": "ajax", "ac": "nav"})
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_info4(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_info4(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_info4(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取用户信息

        GET https://webapi.115.com/user/info
        """
        api = complete_url("/user/info", base_url=base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_info_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_info_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_info_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """更新用户信息

        POST https://my.115.com/proapi/3.0/index.php?method=set_user

        :payload:
            - user_name: str = <default> 💡 网名（1-15 个中英文字符，15天允许修改一次网名）
            - gender: -1 | 0 | 1 = <default> 💡 性别。-1:未知 0:女 1:男
            - calendar_type: 0 | 1 = <default> 💡 日历类型。0:公历 1:农历
            - birthday: str = <default> 💡 生日，格式为 年-月-日（不需要补前 0，初始值为 0-0-0）
            - height: int = <default> 💡 身高
            - weight: int = <default> 💡 体重
            - blood_type: "A" | "B" | "C" | "D" | "O" = <default> 💡 血型。A:A型 B:B型 C:AB型 O:O型 D:其它
            - is_marry: int = <default> 💡 感情

                - 0: 保密
                - 1: 单身
                - 2: 恋爱中
                - 3: 已婚
                - 4: 分居
                - 5: 离异
                - 9: 请选择

            - education: int = <default> 💡 学历

                - -1: 选择学历
                -  0: 初中
                -  1: 高中
                -  2: 中专
                -  3: 大专
                -  4: 本科
                -  5: 硕士
                -  6: 博士及以上

            - job: int = <default> 💡 职业

                - -1: 选择职业
                -  1: 计算机/互联网/通信
                -  2: 生产/工艺/制造
                -  3: 医疗/护理/制药
                -  4: 金融/银行/投资/保险
                -  5: 商业/服务业/个体经营
                -  6: 文化/广告/传媒
                -  7: 娱乐/艺术/表演
                -  8: 律师/法务
                -  9: 教育/培训
                - 10: 公务员/行政/事业单位
                - 11: 模特
                - 12: 空姐
                - 13: 学生
                - 14: 其他职业

            - salary: str = <default> 💡 收入

                - ""
                - "2千-3千"
                - "3千-4.5千"
                - "4.5千-6千"
                - "7千-8千"
                - "8千-1万"
                - "1万以下"
                - "1万-2万"
                - "2万-3万"
                - "3万-4万"
                - "4万-5万"
                - "5万以上"

            - location_birth: int = <default> 💡 家乡。填 115 给出的地区编码，初始值为 0
            - location: int = <default> 💡 现居地。填 115 给出的地区编码，初始值为 0
            - location_link: int = <default> 💡 快递地址。填 115 给出的地区编码，初始值为 0
            - address: str = <default> 💡 输入详细街道地址
            - wechat: str = <default> 💡 微信
            - weibo: str = <default> 💡 微博
            - alipay: str = <default> 💡 支付宝
            - pub_mobile: str = <default> 💡 电话
            - pub_email: str = <default> 💡 邮箱
            - homepage: str = <default> 💡 个人网站
            - like_celeb: str = <default> 💡 最喜欢的名人
            - like_music: str = <default> 💡 最喜欢的音乐
            - like_animal: str = <default> 💡 最喜欢的动物
            - like_book: str = <default> 💡 最喜欢的书籍
            - like_video: str = <default> 💡 最喜欢的视频
            - interest: str = <default> 💡 兴趣爱好
        """
        api = complete_url(
            "/proapi/3.0/index.php", base_url=base_url, query={"method": "set_user"}
        )
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def user_interests_list(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_interests_list(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_interests_list(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户兴趣列表

        GET https://my.115.com/proapi/3.0/index.php?method=get_interests_list
        """
        api = complete_url(
            "/proapi/3.0/index.php",
            base_url=base_url,
            query={"method": "get_interests_list"},
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_my(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_my(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_my(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取此用户信息

        GET https://my.115.com/?ct=ajax&ac=
        """
        api = complete_url(base_url=base_url, query={"ct": "ajax", "ac": "nav"})
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_my_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_my_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_my_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取此用户信息（更全）

        GET https://my.115.com/?ct=ajax&ac=get_user_aq
        """
        api = complete_url(base_url=base_url, query={"ct": "ajax", "ac": "get_user_aq"})
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_points_balance(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://points.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_points_balance(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://points.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_points_balance(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://points.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """剩余的签到积分

        GET https://points.115.com/api/1.0/{app}/1.0/user/balance
        """
        api = complete_url(f"/api/1.0/{app}/1.0/user/balance", base_url=base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_points_sign(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_points_sign(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_points_sign(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取签到信息

        GET https://proapi.115.com/{app}/2.0/user/points_sign
        """
        api = complete_url("/2.0/user/points_sign", base_url=base_url, app=app)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_points_sign_post(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_points_sign_post(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_points_sign_post(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """每日签到（注意：不要用 web，即浏览器，的 cookies，会失败）

        POST https://proapi.115.com/{app}/2.0/user/points_sign
        """
        api = complete_url("/2.0/user/points_sign", base_url=base_url, app=app)
        t = int(time())
        payload = {
            "token": sha1(b"%d-Points_Sign@#115-%d" % (self.user_id, t)).hexdigest(),
            "token_time": t,
        }
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def user_points_transaction(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://points.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_points_transaction(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://points.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_points_transaction(
        self,
        payload: int | dict = 0,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://points.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """签到记录

        GET https://points.115.com/api/1.0/{app}/1.0/user/transaction

        payload:
            - start: int = 0
            - limit: int = 32
            - month: str = <default> 💡 月份，格式为 YYYYMM
        """
        api = complete_url(f"/api/1.0/{app}/1.0/user/transaction", base_url=base_url)
        if isinstance(payload, int):
            payload = {"start": payload}
        payload.setdefault("limit", 32)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def user_public(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_public(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_public(
        self,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户隐私设置

        GET https://my.115.com/proapi/3.0/index.php?method=get_public
        """
        api = complete_url(
            "/proapi/3.0/index.php", base_url=base_url, query={"method": "get_public"}
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_public_set(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_public_set(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_public_set(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://my.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置用户隐私

        POST https://my.115.com/proapi/3.0/index.php?method=set_public

        :payload:
            - column: str 💡 隐私项
            - open: 0 | 1 = 1 💡 是否公开可见
        """
        api = complete_url(
            "/proapi/3.0/index.php", base_url=base_url, query={"method": "set_public"}
        )
        if isinstance(payload, str):
            payload = {"column": payload}
        payload.setdefault("open", 1)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def user_relation_info(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://home.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_relation_info(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://home.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_relation_info(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://home.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取用户的关系信息

        GET https://home.115.com/api/1.0/{app}/1.0/my_star/relation_info
        """
        api = complete_url(
            f"api/1.0/{app}/1.0/my_star/relation_info", base_url=base_url
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_security_key_check(
        self,
        payload: int | str | dict = "",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_security_key_check(
        self,
        payload: int | str | dict = "",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_security_key_check(
        self,
        payload: int | str | dict = "",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取安全密钥对应的 token，可以提供给某些接口，作为通过安全密钥验证的凭证

        POST https://passportapi.115.com/app/1.0/{app}/1.0/user/security_key_check

        :payload:
            - passwd: int | str = "000000" 💡 安全密钥，值为实际安全密钥的 md5 哈希值
        """
        api = complete_url(
            f"/app/1.0/{app}/1.0/user/security_key_check", base_url=base_url
        )
        if isinstance(payload, (int, str)):
            payload = {"passwd": payload}
        payload["passwd"] = md5_secret_password(payload.get("passwd"))
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def user_setting(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_setting(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_setting(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取此账户的设置

        GET https://115.com/?ac=setting&even=saveedit&is_wl_tpl=1
        """
        api = complete_url(
            base_url=base_url,
            query={"ac": "setting", "even": "saveedit", "is_wl_tpl": 1},
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_setting2(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_setting2(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_setting2(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取此账户的设置

        GET https://115.com/?ct=user_setting&ac=get
        """
        api = complete_url(base_url=base_url, query={"ct": "user_setting", "ac": "get"})
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_setting_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_setting_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_setting_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """修改此账户的网页版设置（提示：较为复杂，自己抓包研究）

        POST https://115.com/?ac=setting&even=saveedit&is_wl_tpl=1
        """
        api = complete_url(
            base_url=base_url,
            query={"ct": "setting", "even": "saveedit", "is_wl_tpl": 1},
        )
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def user_setting_web(
        self,
        payload: dict = {},
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_setting_web(
        self,
        payload: dict = {},
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_setting_web(
        self,
        payload: dict = {},
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取此账户的 app 版设置（提示：较为复杂，自己抓包研究）

        GET https://webapi.115.com/user/setting

        :payload:
            - keys: str 💡 查询的设置参数，多个用逗号 "," 隔开
        """
        api = complete_url("/user/setting", base_url=base_url)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def user_setting_web_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_setting_web_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_setting_web_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取（并可修改）此账户的网页版设置（提示：较为复杂，自己抓包研究）

        POST https://webapi.115.com/user/setting
        """
        api = complete_url("/user/setting", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def user_setting_app(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_setting_app(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_setting_app(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取此账户的 app 版设置（提示：较为复杂，自己抓包研究）

        GET https://proapi.115.com/{app}/1.0/user/setting
        """
        api = complete_url("/1.0/user/setting", base_url=base_url, app=app)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_setting_app_set(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_setting_app_set(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_setting_app_set(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取（并可修改）此账户的网页版设置（提示：较为复杂，自己抓包研究）

        POST https://proapi.115.com/{app}/1.0/user/setting
        """
        api = complete_url("/1.0/user/setting", base_url=base_url, app=app)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def user_sign(
        self,
        /,
        base_url: str | Callable[[], str] = "https://q.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_sign(
        self,
        /,
        base_url: str | Callable[[], str] = "https://q.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_sign(
        self,
        /,
        base_url: str | Callable[[], str] = "https://q.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """个性签名

        GET https://q.115.com/home/setting/sign
        """
        api = complete_url("/home/setting/sign", base_url=base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_sign_set(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://q.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_sign_set(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://q.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_sign_set(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://q.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """修改个性签名

        POST https://q.115.com/ajax_users/save_sign

        :payload:
            - content: str 💡 个性签名，支持 HTML
        """
        api = complete_url("/ajax_users/save_sign", base_url=base_url)
        if isinstance(payload, str):
            payload = {"content": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def user_space_info(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_space_info(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_space_info(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取使用空间的统计数据（较为简略，如需更详细，请用 ``P115Client.fs_index_info()``）

        GET https://proapi.115.com/{app}/user/space_info
        """
        api = complete_url("/user/space_info", base_url=base_url, app=app)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_teen_mode_state(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_teen_mode_state(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_teen_mode_state(
        self,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取青少年（未成年）模式状态

        GET https://passportapi.115.com/app/1.0/{app}/1.0/user/teen_mode_state
        """
        api = complete_url(
            f"/app/1.0/{app}/1.0/user/teen_mode_state", base_url=base_url
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_teen_mode_state_set(
        self,
        payload: bool | dict = True,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_teen_mode_state_set(
        self,
        payload: bool | dict = True,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_teen_mode_state_set(
        self,
        payload: bool | dict = True,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://passportapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """开关青少年（未成年）模式状态

        POST https://passportapi.115.com/app/1.0/{app}/1.0/user/teen_mode_set_state

        :payload:
            - state: 0 | 1 💡 是否开启
            - passwd: str = "0000" 💡 密码（4 位数字），需要经过 md5 签名处理，`md5(f"{passwd}{user_id}62454aa2c6fd4".encode("ascii")).hexdigest()`
        """
        api = complete_url(
            f"/app/1.0/{app}/1.0/user/teen_mode_set_state", base_url=base_url
        )
        if isinstance(payload, bool):
            payload = {"state": int(payload), "passwd": "0000"}
        else:
            payload.setdefault("passwd", "0000")
        if len(str(passwd := payload.get("passwd"))):
            payload["passwd"] = md5(
                f"{passwd:>04}{self.user_id}62454aa2c6fd4".encode("ascii")
            ).hexdigest()
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def user_vip_check_spw(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_vip_check_spw(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_vip_check_spw(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取用户积分、余额等信息

        GET https://proapi.115.com/{app}/vip/check_spw
        """
        api = complete_url("/vip/check_spw", base_url=base_url, app=app)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def user_vip_limit(
        self,
        payload: int | dict = 2,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def user_vip_limit(
        self,
        payload: int | dict = 2,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def user_vip_limit(
        self,
        payload: int | dict = 2,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 vip 的某些限制

        GET https://webapi.115.com/user/vip_limit

        :payload:
            - feature: int = 2
        """
        api = complete_url("/user/vip_limit", base_url=base_url)
        if isinstance(payload, int):
            payload = {"feature": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)
