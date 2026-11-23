#!/usr/bin/env python3

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast, overload

if TYPE_CHECKING:
    from . import P115Client

from ._common import (
    CRE_SET_COOKIE,
    P115URL,
    Callable,
    ClientRequestMixin,
    Cookie,
    Coroutine,
    Iterable,
    Mapping,
    _rsa_decrypt,
    check_response,
    complete_url,
    date,
    dumps,
    errno,
    get_request,
    json_loads,
    json_maybe_decrypt_loads,
    rsa_encrypt,
    run_gen_step,
    sha1,
    share_extract_payload,
    throw,
    timedelta,
    unquote,
    urlsplit,
)


class _P115ClientShareMixin:
    """分享与用户分享接口混入。"""

    @overload
    def share_access_user_list(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_access_user_list(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_access_user_list(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """访问账号列表

        GET https://webapi.115.com/share/access_user_list

        :payload:
            - share_code: str
        """
        api = complete_url("/share/access_user_list", base_url=base_url)
        if isinstance(payload, str):
            payload = {"share_code": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_activate(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_activate(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_activate(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """激活分享

        POST https://webapi.115.com/share/activeshare

        :payload:
            - share_code: str
        """
        api = complete_url("/share/activeshare", base_url=base_url)
        if isinstance(payload, str):
            payload = {"share_code": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def share_batch_renewal_long_skip(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_batch_renewal_long_skip(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_batch_renewal_long_skip(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """将免登录下载链接设为长期

        POST https://webapi.115.com/share/batch_renewal_long_skip

        .. attention::
            链接必须开启免登录下载，并且需年费及以上 VIP 会员

        :payload:
            - share_code: str
        """
        api = complete_url("/share/batch_renewal_long_skip", base_url=base_url)
        if isinstance(payload, str):
            payload = {"share_code": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def share_batch_skip_login_down(
        self,
        payload: str | Iterable[str] | dict,
        /,
        skip_login: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_batch_skip_login_down(
        self,
        payload: str | Iterable[str] | dict,
        /,
        skip_login: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_batch_skip_login_down(
        self,
        payload: str | Iterable[str] | dict,
        /,
        skip_login: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量开启或关闭免登录下载

        POST https://webapi.115.com/share/batch_skip_login_down

        .. attention::
            链接必须开启免登录下载，并且需年费及以上 VIP 会员

        :payload:
            - share_code: str       💡 分享码，多个用逗号 "," 隔开
            - skip_login: 0 | 1 = 1 💡 是否允许免登录下载
        """
        api = complete_url("/share/batch_skip_login_down", base_url=base_url)
        if isinstance(payload, str):
            payload = {"share_code": payload}
        elif not isinstance(payload, dict):
            payload = {"share_code": ",".join(payload)}
        payload = cast(dict[str, Any], payload)
        payload.setdefault("skip_login", int(skip_login))
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def share_downlist(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_downlist(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_downlist(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取分享链接的某个目录中可下载的文件的列表（只含文件，不含目录，任意深度，简略信息）

        GET https://webapi.115.com/share/downlist

        .. attention::
            cid 不能为 0 或 空

        :payload:
            - share_code: str
            - receive_code: str
            - cid: int | str
        """
        api = complete_url("/share/downlist", base_url=base_url)
        if not isinstance(payload, dict):
            payload = {"cid": payload}
        if share_url:
            share_payload = share_extract_payload(share_url)
            payload["share_code"] = share_payload["share_code"]
            payload["receive_code"] = share_payload.get("receive_code") or ""
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_downlist_app(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_downlist_app(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_downlist_app(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取分享链接的某个目录中可下载的文件的列表（只含文件，不含目录，任意深度，简略信息）

        GET https://proapi.115.com/app/share/downlist

        .. attention::
            cid 不能为 0 或 空

        :payload:
            - share_code: str
            - receive_code: str
            - cid: int | str
        """
        if app in ("", "chrome"):
            api = complete_url("/app/share/downlist", base_url)
        else:
            if app not in (
                "windows",
                "mac",
                "linux",
                "os_windows",
                "os_mac",
                "os_linux",
            ):
                app = "os_windows"
            api = complete_url("/2.0/share/downlist", base_url=base_url, app=app)
        if not isinstance(payload, dict):
            payload = {"cid": payload}
        if share_url:
            share_payload = share_extract_payload(share_url)
            payload["share_code"] = share_payload["share_code"]
            payload["receive_code"] = share_payload.get("receive_code") or ""
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_download_url(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        strict: bool = True,
        app: str = "android",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> P115URL: ...

    @overload
    def share_download_url(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        strict: bool = True,
        app: str = "android",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, P115URL]: ...

    def share_download_url(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        strict: bool = True,
        app: str = "android",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> P115URL | Coroutine[Any, Any, P115URL]:
        """获取分享链接中某个文件的下载链接

        :param payload: 请求参数，如果为 int 或 str，则视为 `file_id`

            - file_id: int | str 💡 文件 id
            - receive_code: str  💡 接收码（也就是密码）
            - share_code: str    💡 分享码

        :param url: 分享链接，如果提供的话，会被拆解并合并到 `payload` 中，优先级较高
        :param strict: 如果为 True，当目标是目录时，会抛出 IsADirectoryError 异常
        :param app: 使用此设备的接口
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 下载链接
        """

        def gen_step():
            if app in ("web", "desktop"):
                resp = yield self.share_download_url_web(
                    payload, share_url=share_url, async_=async_, **request_kwargs
                )
            else:
                resp = yield self.share_download_url_app(
                    payload,
                    share_url=share_url,
                    app=app,
                    async_=async_,
                    **request_kwargs,
                )
            resp["payload"] = payload
            resp["is_download"] = True
            check_response(resp)
            data = resp.get("data")
            if not data:
                resp["state"] = False
                resp["errno"] = resp.get("errno") or 50015
                resp.setdefault("message", "文件不存在、是目录或者不支持此操作")
            url = data["url"]
            if strict and not url:
                throw(errno.EISDIR, resp)
            return P115URL(
                url["url"] if url else "",
                id=int(data["fid"]),
                name=data["fn"],
                size=int(data["fs"]),
                sha1=data.get("sha1", ""),
                is_dir=not url,
            )

        return run_gen_step(gen_step, async_)

    @overload
    def share_download_url_app(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_download_url_app(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_download_url_app(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取分享链接中某个文件的下载链接

        POST https://proapi.115.com/app/share/downurl

        :payload:
            - file_id: int | str
            - receive_code: str
            - share_code: str
            - dl: 0 | 1 = <default>
        """
        if not isinstance(payload, dict):
            payload = {"file_id": payload}
        if share_url:
            share_payload = share_extract_payload(share_url)
            payload["share_code"] = share_payload["share_code"]
            payload["receive_code"] = share_payload.get("receive_code") or ""
        if app in ("", "chrome"):
            api = complete_url("/app/share/downurl", base_url)

            def parse(_, content: bytes, /) -> dict:
                json = json_maybe_decrypt_loads(content)
                if json["state"] and (data := json.get("data")):
                    json["data"] = json_loads(_rsa_decrypt(data))
                return json

            request_kwargs.setdefault("parse", parse)
            payload = {"data": rsa_encrypt(dumps(payload)).decode()}
            return self.request(
                url=api, method="POST", data=payload, async_=async_, **request_kwargs
            )
        if app not in (
            "windows",
            "mac",
            "linux",
            "os_windows",
            "os_mac",
            "os_linux",
        ):
            app = "os_windows"
        api = complete_url("/2.0/share/downurl", base_url=base_url, app=app)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_download_url_web(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_download_url_web(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_download_url_web(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取分享链接中某个文件的下载链接（网页版接口）

        GET https://webapi.115.com/share/downurl

        .. note::
            最大允许下载 200 MB 的文件

        :payload:
            - file_id: int | str
            - receive_code: str
            - share_code: str
            - dl: int = <default>
        """
        api = complete_url("/share/downurl", base_url=base_url)
        if not isinstance(payload, dict):
            payload = {"file_id": payload}
        if share_url:
            share_payload = share_extract_payload(share_url)
            payload["share_code"] = share_payload["share_code"]
            payload["receive_code"] = share_payload.get("receive_code") or ""
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_info(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_info(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_info(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取（自己的）分享信息

        GET https://webapi.115.com/share/shareinfo

        :payload:
            - share_code: str
        """
        api = complete_url("/share/shareinfo", base_url=base_url)
        if isinstance(payload, str):
            payload = {"share_code": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_info_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_info_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_info_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取（自己的）分享信息

        GET https://proapi.115.com/{app}/2.0/share/shareinfo

        :payload:
            - share_code: str
        """
        api = complete_url("/2.0/share/shareinfo", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"share_code": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列（自己的）分享信息列表

        GET https://webapi.115.com/share/slist

        .. todo::
            暂时不清楚 order 有哪些取值

        :payload:
            - limit: int = 32
            - offset: int = 0
            - order: str = <default> 💡 排序依据，例如 "create_time"
            - asc: 0 | 1 = <default> 💡 是否升序排列
            - show_cancel_share: 0 | 1 = 0
            - share_state: int = <default>
        """
        api = complete_url("/share/slist", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload = {"limit": 32, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_list_app(
        self,
        payload: int | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_list_app(
        self,
        payload: int | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_list_app(
        self,
        payload: int | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列（自己的）分享信息列表

        GET https://proapi.115.com/{app}/2.0/share/slist

        :payload:
            - limit: int = 32
            - offset: int = 0
        """
        api = complete_url("/2.0/share/slist", base_url=base_url, app=app)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload = {"limit": 32, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_notlogin_dl_quota(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_notlogin_dl_quota(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_notlogin_dl_quota(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """免登录下载流量配额

        GET https://webapi.115.com/user/notlogin_dl_quota
        """
        api = complete_url("/user/notlogin_dl_quota", base_url=base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def share_notlogin_dl_quota_app(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_notlogin_dl_quota_app(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_notlogin_dl_quota_app(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """免登录下载流量配额

        GET https://proapi.115.com/{app}/2.0/user/notlogin_dl_quota
        """
        api = complete_url("/2.0/user/notlogin_dl_quota", base_url=base_url, app=app)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def share_receive(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_receive(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_receive(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """接收分享链接的某些文件或目录

        POST https://webapi.115.com/share/receive

        :payload:
            - share_code: str
            - receive_code: str
            - file_id: int | str         💡 有多个时，用逗号 "," 分隔
            - cid: int | str = <default> 💡 这是你网盘的目录 cid，如果不指定则用默认
            - is_check: 0 | 1 = <default>
            - target_folder: str = <default>
        """
        api = complete_url("/share/receive", base_url=base_url)
        if not isinstance(payload, dict):
            payload = {"file_id": payload}
        if share_url:
            share_payload = share_extract_payload(share_url)
            payload["share_code"] = share_payload["share_code"]
            payload["receive_code"] = share_payload.get("receive_code") or ""
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def share_receive_app(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_receive_app(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_receive_app(
        self,
        payload: int | str | dict,
        /,
        share_url: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """接收分享链接的某些文件或目录

        POST https://proapi.115.com/{app}/2.0/share/receive

        :payload:
            - share_code: str
            - receive_code: str
            - file_id: int | str         💡 有多个时，用逗号 "," 分隔
            - cid: int | str = <default> 💡 这是你网盘的目录 cid，如果不指定则用默认
            - is_check: 0 | 1 = <default>
        """
        api = complete_url("/2.0/share/receive", base_url=base_url, app=app)
        if not isinstance(payload, dict):
            payload = {"file_id": payload}
        if share_url:
            share_payload = share_extract_payload(share_url)
            payload["share_code"] = share_payload["share_code"]
            payload["receive_code"] = share_payload.get("receive_code") or ""
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def share_recvcode(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_recvcode(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_recvcode(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """取消访问码

        GET https://webapi.115.com/share/recvcode

        :payload:
            - share_code: str
            - action: str = "cancel"
        """
        api = complete_url("/share/recvcode", base_url=base_url)
        if isinstance(payload, str):
            payload = {"share_code": payload}
        payload.setdefault("action", "cancel")
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_recvcode_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_recvcode_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_recvcode_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """取消访问码

        GET https://proapi.115.com/{app}/2.0/share/recvcode

        :payload:
            - share_code: str
            - action: str = "cancel"
        """
        api = complete_url("/2.0/share/recvcode", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"share_code": payload}
        payload.setdefault("action", "cancel")
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_reshare(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_reshare(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_reshare(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """续期分享

        POST https://webapi.115.com/share/reshare

        :payload:
            - share_code: str
            - ignore_warn: 0 | 1 = 1 💡 忽略信息提示，传 1 就行了
            - renewal_skip_login: str = <default>
        """
        api = complete_url("/share/reshare", base_url=base_url)
        if isinstance(payload, str):
            payload = {"share_code": payload}
        payload.setdefault("ignore_warn", 1)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def share_search(
        self,
        payload: str | dict,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_search(
        self,
        payload: str | dict,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_search(
        self,
        payload: str | dict,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """从分享链接搜索文件或目录

        GET https://webapi.115.com/share/search

        .. attention::
            最多只能取回前 10,000 条数据，也就是 `limit + offset <= 10_000`，不过可以一次性取完

        :payload:
            - share_code: str    💡 分享码
            - receive_code: str  💡 接收码（即密码），如果是自己的分享，则不用传
            - cid: int | str = 0 💡 目录 id，对应 parent_id
            - limit: int = 32    💡 一页大小，意思就是 page_size
            - offset: int = 0   💡 索引偏移，索引从 0 开始计算
            - search_value: str = "." 💡 搜索文本，仅支持搜索文件名
            - suffix: str = <default> 💡 文件后缀（扩展名），优先级高于 `type`
            - type: int = <default>   💡 文件类型

                - 0: 全部
                - 1: 文档
                - 2: 图片
                - 3: 音频
                - 4: 视频
                - 5: 压缩包
                - 6: 软件/应用
                - 7: 书籍
                - 99: 所有文件
        """
        api = complete_url("/share/search", base_url=base_url)
        if not isinstance(payload, dict):
            payload = {"search_value": payload}
        payload = {"cid": 0, "limit": 32, "offset": 0, "search_value": ".", **payload}
        if share_url:
            share_payload = share_extract_payload(share_url)
            payload["share_code"] = share_payload["share_code"]
            payload["receive_code"] = share_payload.get("receive_code") or ""
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_send(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_send(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_send(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """创建（自己的）分享

        POST https://webapi.115.com/share/send

        :payload:
            - file_ids: int | str 💡 文件列表，有多个用逗号 "," 隔开
            - is_asc: 0 | 1 = 1 💡 是否升序排列
            - order: str = "file_name" 💡 用某字段排序

                - "file_name": 文件名
                - "file_size": 文件大小
                - "file_type": 文件种类
                - "user_utime": 修改时间
                - "user_ptime": 创建时间
                - "user_otime": 上一次打开时间

            - ignore_warn: 0 | 1 = 1 💡 忽略信息提示，传 1 就行了
        """
        api = complete_url("/share/send", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_ids": payload}
        payload = {"ignore_warn": 1, "is_asc": 1, "order": "file_name", **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def share_send_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_send_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_send_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """创建（自己的）分享

        POST https://proapi.115.com/{app}/2.0/share/send

        :payload:
            - file_ids: int | str 💡 文件列表，有多个用逗号 "," 隔开
            - is_asc: 0 | 1 = 1 💡 是否升序排列
            - order: str = "file_name" 💡 用某字段排序

                - "file_name": 文件名
                - "file_size": 文件大小
                - "file_type": 文件种类
                - "user_utime": 修改时间
                - "user_ptime": 创建时间
                - "user_otime": 上一次打开时间

            - ignore_warn: 0 | 1 = 1 💡 忽略信息提示，传 1 就行了
        """
        api = complete_url("/2.0/share/send", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"file_ids": payload}
        payload = {"ignore_warn": 1, "is_asc": 1, "order": "file_name", **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def share_setting(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_setting(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_setting(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取分享设置

        GET https://webapi.115.com/share/setting
        """
        api = complete_url("/share/setting", base_url=base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def share_skip_login_check(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_skip_login_check(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_skip_login_check(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """检查是否可免登录下载

        POST https://webapi.115.com/share/is_skip_login

        :payload:
            - share_code: str        💡 分享码
            - receive_code: str      💡 接收码（访问密码）
            - file_id: int | str = 1 💡 文件 id（可以随便填一个非 0 的值）
        """
        api = complete_url("/share/is_skip_login", base_url=base_url)
        payload.setdefault("file_id", 1)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def share_skip_login_down(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_skip_login_down(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_skip_login_down(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """开启或关闭免登录下载

        POST https://webapi.115.com/share/skip_login_down

        :payload:
            - share_code: str       💡 分享码
            - skip_login: 0 | 1 = 1 💡 是否开启
        """
        api = complete_url("/share/skip_login_down", base_url=base_url)
        if isinstance(payload, str):
            payload = {"share_code": payload}
        payload.setdefault("skip_login", 1)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def share_skip_login_download_url(
        self: int | str | dict | ClientRequestMixin,
        payload: None | int | str | dict = None,
        /,
        share_url: str = "",
        strict: bool = True,
        app: str = "chrome",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> P115URL: ...

    @overload
    def share_skip_login_download_url(
        self: int | str | dict | ClientRequestMixin,
        payload: None | int | str | dict = None,
        /,
        share_url: str = "",
        strict: bool = True,
        app: str = "chrome",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, P115URL]: ...

    def share_skip_login_download_url(
        self: int | str | dict | ClientRequestMixin,
        payload: None | int | str | dict = None,
        /,
        share_url: str = "",
        strict: bool = True,
        app: str = "chrome",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> P115URL | Coroutine[Any, Any, P115URL]:
        """获取分享链接中某个文件的下载链接

        .. note::
            可以作为 ``staticmethod`` 使用

        :param payload: 请求参数，如果为 int 或 str，则视为 `file_id`

            - file_id: int | str 💡 文件 id
            - receive_code: str  💡 接收码（访问密码）
            - share_code: str    💡 分享码

        :param share_url: 分享链接，如果提供的话，会被拆解并合并到 `payload` 中，优先级较高
        :param strict: 如果为 True，当目标是目录时，会抛出 IsADirectoryError 异常
        :param app: 使用此设备的接口
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 下载链接
        """
        cls: P115Client = __class__  # type: ignore

        def gen_step():
            if app in ("web", "desktop"):
                resp = yield cls.share_skip_login_download_url_web(
                    self,
                    payload,
                    share_url=share_url,
                    async_=async_,  # type: ignore
                    **request_kwargs,
                )
            else:
                resp = yield cls.share_skip_login_download_url_app(
                    self,
                    payload,
                    share_url=share_url,
                    app=app,
                    async_=async_,  # type: ignore
                    **request_kwargs,
                )
            resp["payload"] = payload
            resp["is_download"] = True
            check_response(resp)
            data = resp.get("data")
            if not data:
                resp["state"] = False
                resp["errno"] = resp.get("errno") or 50015
                resp.setdefault("message", "文件不存在、是目录或者不支持此操作")
            url = data["url"]
            if strict and not url:
                throw(errno.EISDIR, resp)
            return P115URL(
                url["url"] if url else "",
                id=int(data["fid"]),
                name=data["fn"],
                size=int(data["fs"]),
                sha1=data.get("sha1", ""),
                is_dir=not url,
            )

        return run_gen_step(gen_step, async_)

    @overload
    def share_skip_login_download_url_app(
        self: int | str | dict | ClientRequestMixin,
        payload: None | int | str | dict = None,
        /,
        share_url: str = "",
        app: str = "chrome",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_skip_login_download_url_app(
        self: int | str | dict | ClientRequestMixin,
        payload: None | int | str | dict = None,
        /,
        share_url: str = "",
        app: str = "chrome",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_skip_login_download_url_app(
        self: int | str | dict | ClientRequestMixin,
        payload: None | int | str | dict = None,
        /,
        share_url: str = "",
        app: str = "chrome",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取免登录下载链接

        POST https://proapi.115.com/app/share/skip_login_downurl

        .. note::
            可以作为 ``staticmethod`` 使用

        :payload:
            - file_id: int | str
            - receive_code: str
            - share_code: str
        """
        if isinstance(self, ClientRequestMixin):
            assert payload is not None
            request_kwargs["self"] = self
        else:
            payload = self
        if not isinstance(payload, dict):
            payload = {"file_id": payload}
        if share_url:
            share_payload = share_extract_payload(share_url)
            payload["share_code"] = share_payload["share_code"]
            payload["receive_code"] = share_payload.get("receive_code") or ""
        if app in ("", "chrome"):
            api = complete_url("/app/share/skip_login_downurl", base_url)

            def parse(_, content: bytes, /) -> dict:
                json = json_maybe_decrypt_loads(content)
                if json["state"] and (data := json.get("data")):
                    json["data"] = json_loads(_rsa_decrypt(data))
                return json

            request_kwargs.setdefault("parse", parse)
            payload = {"data": rsa_encrypt(dumps(payload)).decode()}
        else:
            api = complete_url(
                "/2.0/share/skip_login_downurl", base_url=base_url, app=app
            )
        request, request_kwargs = get_request(
            url=api, method="POST", data=payload, **request_kwargs
        )
        return request(async_=async_, **request_kwargs)

    @overload
    def share_skip_login_download_url_web(
        self: int | str | dict | ClientRequestMixin,
        payload: None | int | str | dict = None,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_skip_login_download_url_web(
        self: int | str | dict | ClientRequestMixin,
        payload: None | int | str | dict = None,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_skip_login_download_url_web(
        self: int | str | dict | ClientRequestMixin,
        payload: None | int | str | dict = None,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取免登录下载链接

        POST https://webapi.115.com/share/skip_login_downurl

        .. note::
            可以作为 ``staticmethod`` 使用

        :payload:
            - share_code: str    💡 分享码
            - receive_code: str  💡 接收码（访问密码）
            - file_id: int | str 💡 文件 id
        """
        api = complete_url("/share/skip_login_downurl", base_url=base_url)
        if isinstance(self, ClientRequestMixin):
            assert payload is not None
            request_kwargs["self"] = self
        else:
            payload = self
        if not isinstance(payload, dict):
            payload = {"file_id": payload}
        if share_url:
            share_payload = share_extract_payload(share_url)
            payload["share_code"] = share_payload["share_code"]
            payload["receive_code"] = share_payload.get("receive_code") or ""
        request, request_kwargs = get_request(
            url=api, method="POST", data=payload, **request_kwargs
        )
        return request(async_=async_, **request_kwargs)

    @overload
    def share_skip_login_down_first(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_skip_login_down_first(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_skip_login_down_first(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """免登录下载信息

        GET https://webapi.115.com/share/skip_login_down_first

        :payload:
            - share_code: str 💡 分享码
        """
        api = complete_url("/share/skip_login_down_first", base_url=base_url)
        if isinstance(payload, str):
            payload = {"share_code": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_skip_login_down_details(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_skip_login_down_details(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_skip_login_down_details(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """流量消耗明细

        GET https://webapi.115.com/share/skip_login_down_details

        :payload:
            - start_time: str = <default> 💡 开始时间，格式为 "YYYY-MM-DD hh:mm:ss"，默认为今天零点
            - end_time: str = <default>   💡 结束时间（含），默认为明天零点
            - share_code: str = ""        💡 分享码，如果为空则统计所有分享
            - offset: int = 0
            - limit: int = 32
        """
        api = complete_url("/share/skip_login_down_details", base_url=base_url)
        today = date.today()
        default_start_time = f"{today} 00:00:00"
        default_end_time = f"{today + timedelta(days=1)} 00:00:00"
        if isinstance(payload, str):
            payload = {"start_time": payload or default_start_time}
        payload = {
            "share_code": "",
            "limit": 32,
            "offset": 0,
            "start_time": default_start_time,
            "end_time": default_end_time,
            **payload,
        }
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_snap(
        self: int | str | dict | ClientRequestMixin,
        payload: int | str | dict = 0,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_snap(
        self: int | str | dict | ClientRequestMixin,
        payload: int | str | dict = 0,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_snap(
        self: int | str | dict | ClientRequestMixin,
        payload: int | str | dict = 0,
        /,
        share_url: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取分享链接的某个目录中的文件和子目录的列表（包含详细信息）

        GET https://webapi.115.com/share/snap

        .. note::
            可以作为 ``staticmethod`` 使用

            如果是登录状态，且查看自己的分享时，则可以不提供 receive_code，而且即使还在审核中，也能获取文件列表

        .. caution::
            虽然可以不登录即可获取数据，但是一旦过于频繁，会封禁 IP 一段时间

        :payload:
            - share_code: str
            - receive_code: str
            - cid: int | str = 0
            - limit: int = 32
            - offset: int = 0
            - asc: 0 | 1 = <default> 💡 是否升序排列
            - o: str = <default> 💡 用某字段排序

                - "file_name": 文件名
                - "file_size": 文件大小
                - "user_ptime": 创建时间/修改时间
        """
        api = complete_url("/share/snap", base_url=base_url)
        if isinstance(self, ClientRequestMixin):
            request_kwargs["self"] = self
        else:
            payload = self
        if not isinstance(payload, dict):
            payload = {"cid": payload}
        payload = {"cid": 0, "limit": 32, "offset": 0, **payload}
        if share_url:
            share_payload = share_extract_payload(share_url)
            payload["share_code"] = share_payload["share_code"]
            payload["receive_code"] = share_payload.get("receive_code") or ""
        request, request_kwargs = get_request(url=api, params=payload, **request_kwargs)
        return request(async_=async_, **request_kwargs)

    @overload
    def share_snap_app(
        self,
        payload: int | str | dict = 0,
        /,
        share_url: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_snap_app(
        self,
        payload: int | str | dict = 0,
        /,
        share_url: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_snap_app(
        self,
        payload: int | str | dict = 0,
        /,
        share_url: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取分享链接的某个目录中的文件和子目录的列表（包含详细信息）

        GET https://proapi.115.com/{app}/2.0/share/snap

        .. caution::
            这个接口必须登录使用，并且对于其它人的网盘文件，每个目录中最多获取前 1000 条（但获取自己的资源正常）

        :payload:
            - share_code: str
            - receive_code: str
            - cid: int | str = 0
            - limit: int = 32
            - offset: int = 0
            - asc: 0 | 1 = <default> 💡 是否升序排列
            - o: str = <default> 💡 用某字段排序

                - "file_name": 文件名
                - "file_size": 文件大小
                - "user_ptime": 创建时间/修改时间
        """
        api = complete_url("/2.0/share/snap", base_url=base_url, app=app)
        if not isinstance(payload, dict):
            payload = {"cid": payload}
        payload = {"cid": 0, "limit": 32, "offset": 0, **payload}
        if share_url:
            share_payload = share_extract_payload(share_url)
            payload["share_code"] = share_payload["share_code"]
            payload["receive_code"] = share_payload.get("receive_code") or ""
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def share_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def share_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """变更（自己的）分享的配置（例如改访问密码，取消分享）

        POST https://webapi.115.com/share/updateshare

        :payload:
            - share_code: str                       💡 分享码，多个用逗号 "," 隔开
            - receive_code: str = <default>         💡 接收码（访问密码）
            - share_duration: int = <default>       💡 分享天数: n（填入指定天数），-1(长期)
            - is_custom_code: 0 | 1 = <default>     💡 用户自定义口令（不用管）
            - auto_fill_recvcode: 0 | 1 = <default> 💡 分享链接自动填充口令（不用管）
            - auto_renewal: 0 | 1 = <default>       💡 是否自动续期
            - share_channel: int = <default>        💡 分享渠道代码（不用管）
            - action: str = <default>               💡 操作: "cancel":取消分享 "delete":删除分享
            - skip_login_down_flow_limit: "" | int  = <default> 💡 设置免登录下载限制流量，如果为 "" 则不限，单位: 字节
            - access_user_ids = int | str = <default> 💡 设置访问账号，多个用逗号 "," 隔开
            - receive_user_limit: int = <default> 💡 接收次数
            - reset_receive_user: 0 | 1 = <default> 💡 重置接收次数
        """
        api = complete_url("/share/updateshare", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def share_update_app(
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
    def share_update_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def share_update_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """变更（自己的）分享的配置（例如改访问密码，取消分享）

        POST https://proapi.115.com/{app}/2.0/share/updateshare

        :payload:
            - share_code: str                       💡 分享码，多个用逗号 "," 隔开
            - receive_code: str = <default>         💡 接收码（访问密码）
            - share_duration: int = <default>       💡 分享天数: n（填入指定天数），-1(长期)
            - is_custom_code: 0 | 1 = <default>     💡 用户自定义口令（不用管）
            - auto_fill_recvcode: 0 | 1 = <default> 💡 分享链接自动填充口令（不用管）
            - share_channel: int = <default>        💡 分享渠道代码（不用管）
            - action: str = <default>               💡 操作: "cancel":取消分享 "delete":删除分享
            - skip_login_down_flow_limit: "" | int  = <default> 💡 设置免登录下载限制流量，如果为 "" 则不限，单位: 字节
            - access_user_ids = int | str = <default> 💡 设置访问账号，多个用逗号 "," 隔开
            - receive_user_limit: int = <default> 💡 接收次数
            - reset_receive_user: 0 | 1 = <default> 💡 重置接收次数
        """
        api = complete_url("/2.0/share/updateshare", base_url=base_url, app=app)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def usershare_add_folder(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_add_folder(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_add_folder(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """转存共享文件或目录

        POST https://webapi.115.com/usershare/add_folder

        :payload:
            - share_id: int | str
            - pid: int | str
            - cname: str
        """
        api = complete_url("/usershare/add_folder", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def usershare_add_folder_app(
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
    def usershare_add_folder_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_add_folder_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """转存共享文件或目录

        POST https://proapi.115.com/{app}/2.0/usershare/add_folder

        :payload:
            - share_id: int | str
            - pid: int | str
            - cname: str
        """
        api = complete_url("/2.0/usershare/add_folder", base_url=base_url, app=app)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def usershare_action(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_action(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_action(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取共享动态列表

        GET https://webapi.115.com/usershare/action

        :payload:
            - share_id: int | str
            - offset: int = 0
            - limit: int = 32
        """
        api = complete_url("/usershare/action", base_url=base_url)
        if isinstance(payload, int):
            payload = {"share_id": payload}
        payload = {"limit": 32, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def usershare_action_app(
        self,
        payload: int | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_action_app(
        self,
        payload: int | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_action_app(
        self,
        payload: int | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取共享动态列表

        GET https://proapi.115.com/{app}/2.0/usershare/action

        :payload:
            - share_id: int | str
            - offset: int = 0
            - limit: int = 32
        """
        api = complete_url("/2.0/usershare/action", base_url=base_url, app=app)
        if isinstance(payload, int):
            payload = {"share_id": payload}
        payload = {"limit": 32, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def usershare_copy(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_copy(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_copy(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """转存文件或目录

        POST https://webapi.115.com/usershare/copy

        :payload:
            - share_id: int | str
            - file_ids: int | str  💡 文件或目录的 id，多个用逗号 "," 隔开
            - to_cid: int = 0      💡 转存到你的网盘中的目录 id
            - copy_type: 0 | 1 = 0 💡 复制类型：0:共享->网盘 1:网盘->共享
        """
        api = complete_url("/usershare/copy", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def usershare_copy_app(
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
    def usershare_copy_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_copy_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """转存文件或目录

        POST https://proapi.115.com/{app}/2.0/usershare/copy

        :payload:
            - share_id: int | str
            - file_ids: int | str  💡 文件或目录的 id，多个用逗号 "," 隔开
            - to_cid: int = 0      💡 转存到你的网盘中的目录 id
            - copy_type: 0 | 1 = 0 💡 复制类型：0:共享->网盘 1:网盘->共享
        """
        api = complete_url("/2.0/usershare/copy", base_url=base_url, app=app)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def usershare_delete(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_delete(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_delete(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除共享文件或目录

        POST https://webapi.115.com/usershare/delete

        :payload:
            - share_id: int | str
            - file_ids: int | str 💡 共享中的文件或目录的 id，多个用逗号 "," 隔开
            - ignore_warn: 0 | 1 = 0
        """
        api = complete_url("/usershare/delete", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def usershare_delete_app(
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
    def usershare_delete_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_delete_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除共享文件或目录

        POST https://proapi.115.com/{app}/2.0/usershare/delete

        :payload:
            - share_id: int | str
            - file_ids: int | str 💡 共享中的文件或目录的 id，多个用逗号 "," 隔开
            - ignore_warn: 0 | 1 = 0
        """
        api = complete_url("/2.0/usershare/delete", base_url=base_url, app=app)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def usershare_download_url(
        self,
        pickcode: str,
        /,
        share_id: int | str,
        strict: bool = True,
        user_agent: None | str = None,
        app: str = "chrome",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> P115URL: ...

    @overload
    def usershare_download_url(
        self,
        pickcode: str,
        /,
        share_id: int | str,
        strict: bool = True,
        user_agent: None | str = None,
        app: str = "chrome",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, P115URL]: ...

    def usershare_download_url(
        self,
        pickcode: str,
        /,
        share_id: int | str,
        strict: bool = True,
        user_agent: None | str = None,
        app: str = "chrome",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> P115URL | Coroutine[Any, Any, P115URL]:
        """获取共享文件的下载链接

        .. note::
            获取的直链中，部分查询参数的解释：

            - ``t``: 过期时间戳
            - ``u``: 用户 id
            - ``c``: 允许同时打开次数，如果为 0，则是无限次数
            - ``f``: 请求时要求携带请求头
                - 如果为空，则无要求
                - 如果为 1，则需要 user-agent（和请求直链时的一致）
                - 如果为 3，则需要 user-agent（和请求直链时的一致） 和 Cookie（由请求直链时的响应所返回的 Set-Cookie 响应头）

        :param pickcode: 提取码
        :param share_id: 共享 id
        :param strict: 如果为 True，当目标是目录时，会抛出 IsADirectoryError 异常
        :param user_agent: 如果不为 None，则作为请求头 "user-agent" 的值
        :param app: 使用此设备的接口
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 下载链接
        """

        def gen_step():
            payload = {"share_id": share_id, "pick_code": pickcode}
            if app in ("web", "desktop"):
                resp = yield self.usershare_download_url_web(
                    payload,
                    user_agent=user_agent,
                    async_=async_,
                    **request_kwargs,
                )
                resp["payload"] = payload
                resp["is_download"] = True
                try:
                    check_response(resp)
                except IsADirectoryError:
                    if strict:
                        raise
                return P115URL(
                    resp.get("file_url", ""),
                    id=int(resp["file_id"]),
                    pickcode=pickcode,
                    name=resp["file_name"],
                    size=int(resp["file_size"]),
                    is_dir=not resp["state"],
                    headers=resp["headers"],
                )
            else:
                resp = yield self.download_url_app(
                    payload,
                    user_agent=user_agent,
                    app=app,
                    async_=async_,
                    **request_kwargs,
                )
                resp["payload"] = payload
                resp["is_download"] = True
                check_response(resp)
                data = resp.get("data")
                if not data:
                    resp["state"] = False
                    resp["errno"] = resp.get("errno") or 50015
                    resp.setdefault("message", "文件不存在、是目录或者不支持此操作")
                if "url" in data:
                    url = data["url"]
                    return P115URL(
                        url,
                        pickcode=pickcode,
                        name=unquote(urlsplit(url).path.rsplit("/", 1)[-1]),
                        is_dir=False,
                        headers=resp["headers"],
                    )
                for fid, info in data.items():
                    url = info["url"]
                    if strict and not url:
                        throw(
                            errno.EISDIR,
                            f"{fid} is a directory, with response {resp}",
                        )
                    return P115URL(
                        url["url"] if url else "",
                        id=int(fid),
                        pickcode=info["pick_code"],
                        name=info["file_name"],
                        size=int(info["file_size"]),
                        sha1=info["sha1"],
                        is_dir=not url,
                        headers=resp["headers"],
                    )
                throw(
                    errno.ENOENT,
                    f"no such pickcode: {pickcode!r}, with response {resp}",
                )

        return run_gen_step(gen_step, async_)

    @overload
    def usershare_download_urls(
        self,
        pickcodes: str | Iterable[str],
        /,
        share_id: int | str,
        strict: bool = True,
        user_agent: None | str = None,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict[int, P115URL]: ...

    @overload
    def usershare_download_urls(
        self,
        pickcodes: str | Iterable[str],
        /,
        share_id: int | str,
        strict: bool = True,
        user_agent: None | str = None,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict[int, P115URL]]: ...

    def usershare_download_urls(
        self,
        pickcodes: str | Iterable[str],
        /,
        share_id: int | str,
        strict: bool = True,
        user_agent: None | str = None,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict[int, P115URL] | Coroutine[Any, Any, dict[int, P115URL]]:
        """批量获取共享文件的下载链接

        .. note::
            获取的直链中，部分查询参数的解释：

            - ``t``: 过期时间戳
            - ``u``: 用户 id
            - ``c``: 允许同时打开次数，如果为 0，则是无限次数
            - ``f``: 请求时要求携带请求头
                - 如果为空，则无要求
                - 如果为 1，则需要 user-agent（和请求直链时的一致）
                - 如果为 3，则需要 user-agent（和请求直链时的一致） 和 Cookie（由请求直链时的响应所返回的 Set-Cookie 响应头）

        :param pickcodes: 提取码，多个用逗号 "," 隔开
        :param share_id: 共享 id
        :param strict: 如果为 True，当目标是目录时，会直接忽略
        :param user_agent: 如果不为 None，则作为请求头 "user-agent" 的值
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 一批下载链接
        """
        if not isinstance(pickcodes, str):
            pickcodes = ",".join(pickcodes)

        def gen_step():
            payload = {"pickcode": pickcodes, "share_id": share_id}
            resp = yield self.download_url_app(
                payload,
                user_agent=user_agent,
                async_=async_,
                **request_kwargs,
            )
            resp["payload"] = payload
            resp["is_download"] = True
            data = resp.get("data")
            if not data:
                resp["state"] = False
                resp["errno"] = resp.get("errno") or 50015
                resp.setdefault("message", "文件不存在、是目录或者不支持此操作")
            urls: dict[int, P115URL] = {}
            if resp.get("errno") != 50003:
                check_response(resp)
                for fid, info in data.items():
                    url = info["url"]
                    if strict and not url:
                        continue
                    fid = int(fid)
                    urls[fid] = P115URL(
                        url["url"] if url else "",
                        id=fid,
                        pickcode=info["pick_code"],
                        name=info["file_name"],
                        size=int(info["file_size"]),
                        sha1=info["sha1"],
                        is_dir=not url,
                        headers=resp["headers"],
                    )
            return urls

        return run_gen_step(gen_step, async_)

    @overload
    def usershare_download_url_web(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_download_url_web(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_download_url_web(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件的下载链接（网页版接口）

        POST https://webapi.115.com/usershare/download

        .. note::
            下载的文件大小没有 200 MB 的限制

        :payload:
            - share_id: int | str
            - pick_code: str
            - dl: int = 0
        """
        api = complete_url("/usershare/download", base_url=base_url)
        headers = request_kwargs["headers"] = dict(request_kwargs.get("headers") or ())
        if user_agent is None:
            headers.setdefault("user-agent", "")
        else:
            headers["user-agent"] = user_agent

        def parse(resp, content: bytes, /) -> dict:
            json = json_maybe_decrypt_loads(content)
            if "Set-Cookie" in resp.headers:
                if isinstance(resp.headers, Mapping):
                    match = CRE_SET_COOKIE.search(resp.headers["Set-Cookie"])
                    if match is not None:
                        headers["cookie"] = match[0]
                else:
                    for k, v in reversed(resp.headers.items()):
                        if k == "Set-Cookie" and CRE_SET_COOKIE.match(v) is not None:
                            headers["cookie"] = v
                            break
            json["headers"] = headers
            return json

        request_kwargs.setdefault("parse", parse)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def usershare_file_list(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_file_list(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_file_list(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """共享目录中的文件列表

        GET https://webapi.115.com/usershare/filelist

        :payload:
            - share_id: int | str
            - cid: int | str 💡 目录 id，对应 parent_id
            - limit: int = 32 💡 分页大小，目前最大值是 1,150，以前是没限制的
            - offset: int = 0 💡 分页开始的索引，索引从 0 开始计算
            - asc: 0 | 1 = <default> 💡 是否升序排列。0:降序 1:升序
            - count_folders: 0 | 1 = 1 💡 统计文件数和目录数，好像也可以写成 ``countfolders``
            - cur: 0 | 1 = <default> 💡 是否只搜索当前目录
            - custom_order: 0 | 1 = <default> 💡 启用自定义排序，如果指定了 "asc"、"fc_mix"、"o" 中其一，则此参数会被自动设置为 1

                - 0: 使用记忆排序（自定义排序失效）
                - 1: 使用自定义排序（不使用记忆排序）
                - 2: 自定义排序（非目录置顶）

            - fc_mix: 0 | 1 = <default> 💡 是否目录和文件混合，如果为 0 则目录在前（目录置顶）
            - nf: 0 | 1 = <default> 💡 不要显示文件（即仅显示目录），但如果 show_dir=0，则此参数无效
            - o: str = <default> 💡 用某字段排序

                - "file_name": 文件名
                - "file_size": 文件大小
                - "file_type": 文件种类
                - "user_utime": 修改时间
                - "user_ptime": 创建时间
                - "user_otime": 上一次打开时间

            - record_open_time: 0 | 1 = 1 💡 是否要记录目录的打开时间
            - show_dir: 0 | 1 = 1 💡 是否显示目录，好像也可以写成 showdir
            - star: 0 | 1 = <default> 💡 是否星标文件
            - suffix: str = <default> 💡 后缀名（优先级高于 `type`）
            - suffix_type: int = <default>
            - type: int = <default> 💡 文件类型

                - 0: 全部（仅当前目录）
                - 1: 文档
                - 2: 图片
                - 3: 音频
                - 4: 视频
                - 5: 压缩包
                - 6: 软件/应用
                - 7: 书籍
                - 8-11: 大概相当于 1
                - 12: 文档+图片+视频，相当于 1、2、4
                - 13: ？？？，音频
                - 14: ？？？，文档
                - 15: 图片+视频，相当于 2、4
                - 16: 字幕
                - 17~98: 大概相当于 1
                - 99: 所有文件
                - >=100: 大概相当于 1
        """
        api = complete_url("/usershare/filelist", base_url=base_url)
        payload = {"limit": 32, "offset": 0, "show_dir": 1, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def usershare_file_list_app(
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
    def usershare_file_list_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_file_list_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """共享目录中的文件列表

        GET https://proapi.115.com/{app}/2.0/usershare/filelist

        :payload:
            - share_id: int | str
            - cid: int | str 💡 目录 id，对应 parent_id
            - limit: int = 32 💡 分页大小，目前最大值是 1,150，以前是没限制的
            - offset: int = 0 💡 分页开始的索引，索引从 0 开始计算
            - asc: 0 | 1 = <default> 💡 是否升序排列。0:降序 1:升序
            - count_folders: 0 | 1 = 1 💡 统计文件数和目录数，好像也可以写成 ``countfolders``
            - cur: 0 | 1 = <default> 💡 是否只搜索当前目录
            - custom_order: 0 | 1 = <default> 💡 启用自定义排序，如果指定了 "asc"、"fc_mix"、"o" 中其一，则此参数会被自动设置为 1

                - 0: 使用记忆排序（自定义排序失效）
                - 1: 使用自定义排序（不使用记忆排序）
                - 2: 自定义排序（非目录置顶）

            - fc_mix: 0 | 1 = <default> 💡 是否目录和文件混合，如果为 0 则目录在前（目录置顶）
            - nf: 0 | 1 = <default> 💡 不要显示文件（即仅显示目录），但如果 show_dir=0，则此参数无效
            - o: str = <default> 💡 用某字段排序

                - "file_name": 文件名
                - "file_size": 文件大小
                - "file_type": 文件种类
                - "user_utime": 修改时间
                - "user_ptime": 创建时间
                - "user_otime": 上一次打开时间

            - record_open_time: 0 | 1 = 1 💡 是否要记录目录的打开时间
            - show_dir: 0 | 1 = 1 💡 是否显示目录，好像也可以写成 showdir
            - star: 0 | 1 = <default> 💡 是否星标文件
            - suffix: str = <default> 💡 后缀名（优先级高于 `type`）
            - suffix_type: int = <default>
            - type: int = <default> 💡 文件类型

                - 0: 全部（仅当前目录）
                - 1: 文档
                - 2: 图片
                - 3: 音频
                - 4: 视频
                - 5: 压缩包
                - 6: 软件/应用
                - 7: 书籍
                - 8-11: 大概相当于 1
                - 12: 文档+图片+视频，相当于 1、2、4
                - 13: ？？？，音频
                - 14: 大概相当于 1
                - 15: 图片+视频，相当于 2、4
                - >= 16: 相当于 8
        """
        api = complete_url("/2.0/usershare/filelist", base_url=base_url, app=app)
        payload = {"limit": 32, "offset": 0, "show_dir": 1, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def usershare_info(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_info(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_info(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取共享信息

        GET https://webapi.115.com/usershare/shareinfo

        :payload:
            - share_id: int | str
        """
        api = complete_url("/usershare/shareinfo", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"share_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def usershare_info_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_info_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_info_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取共享信息

        GET https://proapi.115.com/{app}/2.0/usershare/shareinfo

        :payload:
            - share_id: int | str
        """
        api = complete_url("/2.0/usershare/shareinfo", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"share_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def usershare_invite(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_invite(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_invite(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取共享链接

        POST https://webapi.115.com/usershare/invite

        :payload:
            - share_id: int | str
        """
        api = complete_url("/usershare/invite", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"share_id": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def usershare_invite_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_invite_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_invite_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取共享链接

        POST https://proapi.115.com/{app}/2.0/usershare/invite

        :payload:
            - share_id: int | str
        """
        api = complete_url("/2.0/usershare/invite", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"share_id": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def usershare_list(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_list(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_list(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """共享列表

        GET https://webapi.115.com/usershare/list

        :payload:
            - offset: int = 0
            - limit: int = 1150
            - type: "all" | "others" | "mine" = "all" 💡 类型：all:全部共享 others:他人共享 mine:我共享的
        """
        api = complete_url("/usershare/list", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"offset": payload}
        payload = {"limit": 1150, "offset": 0, "type": "all", **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def usershare_list_app(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_list_app(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_list_app(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """共享列表

        GET https://proapi.115.com/{app}/2.0/usershare/list

        :payload:
            - offset: int = 0
            - limit: int = 1150
            - type: "all" | "others" | "mine" = "all" 💡 类型：all:全部共享 others:他人共享 mine:我共享的
        """
        api = complete_url("/2.0/usershare/list", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"offset": payload}
        payload = {"limit": 1150, "offset": 0, "type": "all", **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def usershare_member(
        self,
        payload: int | dict,
        /,
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_member(
        self,
        payload: int | dict,
        /,
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_member(
        self,
        payload: int | dict,
        /,
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """某共享的成员信息

        POST https://webapi.115.com/usershare/member

        :payload:
            - share_id: int | str
            - action: str = "member_list"

                - "member_list": 用户列表
                - "member_info": 用户信息
                - "noticeset":   设置通知
                - "priviset":    设置权限（共享拥有者用于对待他人）
                - "remove":      移除成员
                - "join":        加入邀请
                - "quit":        退出共享

            - notice_set: 0 | 1 = <default> 💡 是否开启通知，``action`` 为 "noticeset" 时设置
            - privi_set[{user_id}]: int | str = <default> 💡 设置权限，``action`` 为 "priviset" 时设置，多个用逗号 "," 隔开

                - 2: 上传
                - 8: 转存/下载

            - member_uid: int | str = <default> 💡 用户 id，``action`` 为 "remove" 时设置
            - delete_file: 0 | 1 = <default>    💡 是否同时删除他共享的文件，``action`` 为 "remove" 或 "quit" 时设置
            - invite_code: str = <default>      💡 分享码，``action`` 为 "join" 时设置
        """
        api = complete_url("/usershare/member", base_url=base_url)
        if isinstance(payload, int):
            payload = {"share_id": payload}
        payload.setdefault("action", "member_list")
        return self.request(
            url=api, method=method, payload=payload, async_=async_, **request_kwargs
        )

    @overload
    def usershare_member_app(
        self,
        payload: int | dict,
        /,
        method: str = "POST",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_member_app(
        self,
        payload: int | dict,
        /,
        method: str = "POST",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_member_app(
        self,
        payload: int | dict,
        /,
        method: str = "POST",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """某共享的成员信息

        POST https://proapi.115.com/{app}/2.0/usershare/member

        :payload:
            - share_id: int | str
            - action: str = "member_list"

                - "member_list": 用户列表
                - "member_info": 用户信息
                - "noticeset":   设置通知
                - "priviset":    设置权限（共享拥有者用于对待他人）
                - "remove":      移除成员
                - "join":        加入邀请
                - "quit":        退出共享

            - notice_set: 0 | 1 = <default> 💡 是否开启通知，``action`` 为 "noticeset" 时设置
            - privi_set[{user_id}]: int | str = <default> 💡 设置权限，``action`` 为 "priviset" 时设置，多个用逗号 "," 隔开

                - 2: 上传
                - 8: 转存/下载

            - member_uid: int | str = <default> 💡 用户 id，``action`` 为 "remove" 时设置
            - delete_file: 0 | 1 = <default>    💡 是否同时删除他共享的文件，``action`` 为 "remove" 或 "quit" 时设置
            - invite_code: str = <default>      💡 分享码，``action`` 为 "join" 时设置
        """
        api = complete_url("/2.0/usershare/member", base_url=base_url, app=app)
        if isinstance(payload, int):
            payload = {"share_id": payload}
        payload.setdefault("action", "member_list")
        return self.request(
            url=api, method=method, payload=payload, async_=async_, **request_kwargs
        )

    @overload
    def usershare_share(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_share(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_share(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置共享

        POST https://webapi.115.com/usershare/share

        :payload:
            - file_id: int | str     💡 文件或目录的 id
            - share_opt: 1 | 2 = 1   💡 1: 设置 2: 取消
            - ignore_warn: 0 | 1 = 0
            - safe_pwd: str = ""
        """
        api = complete_url("/usershare/share", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        payload = {"ignore_warn": 0, "share_opt": 1, "safe_pwd": "", **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def usershare_share_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def usershare_share_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def usershare_share_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置共享

        POST https://proapi.115.com/{app}/2.0/usershare/share

        :payload:
            - file_id: int | str     💡 文件或目录的 id
            - share_opt: 1 | 2 = 1   💡 1: 设置 2: 取消
            - ignore_warn: 0 | 1 = 0
            - safe_pwd: str = ""
        """
        api = complete_url("/2.0/usershare/share", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        payload = {"ignore_warn": 0, "share_opt": 1, "safe_pwd": "", **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )
