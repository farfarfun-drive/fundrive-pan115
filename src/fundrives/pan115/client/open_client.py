#!/usr/bin/env python3

from __future__ import annotations

from typing import Any, Literal, Self, cast, overload

from ._common import (
    P115URL,
    URL,
    Buffer,
    Callable,
    ClientRequestMixin,
    Cookie,
    Coroutine,
    Iterable,
    Mapping,
    PathLike,
    SupportsGeturl,
    SupportsRead,
    check_response,
    complete_url,
    date,
    digits,
    ensure_async,
    errno,
    json_maybe_decrypt_loads,
    loads,
    locked_cacheproperty,
    run_gen_step,
    sha1,
    throw,
    time,
    to_id,
    to_pickcode,
    upload_file,
)


class P115OpenClient(ClientRequestMixin):
    """115 的客户端对象

    .. admonition:: Reference

        https://www.yuque.com/115yun/open

    :param access_token: 访问令牌
    :param refresh_token: 刷新令牌
    :param app_id: 授权的 open 应用的 AppID
    :param console_qrcode: 需要扫码登录时，是否在命令行输出二维码
    """

    def __init__(
        self,
        /,
        access_token: str = "",
        refresh_token: str = "",
        app_id: int = 0,
        console_qrcode: bool = True,
    ):
        self.init(
            access_token=access_token,
            refresh_token=refresh_token,
            app_id=app_id,
            console_qrcode=console_qrcode,
            instance=self,
        )

    def __eq__(self, other, /) -> bool:
        return type(self) is type(other) and self.user_id == other.user_id

    def __hash__(self, /) -> int:
        return id(self)

    def __repr__(self, /) -> str:
        cls = type(self)
        return f"<{cls.__module__}.{cls.__qualname__}(app_id={self.app_id}) at {hex(id(self))}>"

    @overload
    @classmethod
    def init(
        cls,
        /,
        access_token: str = "",
        refresh_token: str = "",
        app_id: int = 0,
        console_qrcode: bool = True,
        instance: None | Self = None,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> Self: ...
    @overload
    @classmethod
    def init(
        cls,
        /,
        access_token: str = "",
        refresh_token: str = "",
        app_id: int = 0,
        console_qrcode: bool = True,
        instance: None | Self = None,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, Self]: ...
    @classmethod
    def init(
        cls,
        /,
        access_token: str = "",
        refresh_token: str = "",
        app_id: int = 0,
        console_qrcode: bool = True,
        instance: None | Self = None,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> Self | Coroutine[Any, Any, Self]:
        def gen_step():
            if instance is None:
                self = cls.__new__(cls)
            else:
                self = instance
            self.app_id = app_id
            self.access_token = access_token
            self.refresh_token = refresh_token
            if not access_token:
                if refresh_token:
                    resp = yield self.login_refresh_token_open(
                        refresh_token,
                        async_=async_,
                        **request_kwargs,
                    )
                else:
                    resp = yield self.login_with_app_id(
                        app_id or 100195125,
                        console_qrcode=console_qrcode,
                        async_=async_,
                        **request_kwargs,
                    )
                check_response(resp)
                data = resp["data"]
                self.refresh_token = data["refresh_token"]
                self.access_token = data["access_token"]
            return self

        return run_gen_step(gen_step, async_)

    @locked_cacheproperty
    def pickcode_stable_point(self, /) -> str:
        """获取 pickcode 的不动点，或者也叫本征值

        .. todo::
            不动点可能和用户 id 有某种联系，但目前样本不足，难以推断，以后再尝试分析
        """
        from ..util import get_stable_point, set_stable_point

        try:
            return get_stable_point(self.user_id)
        except KeyError:
            resp = self.fs_files({"show_dir": 1, "limit": 1, "cid": 0})
            check_response(resp)
            if resp["data"]:
                info = resp["data"][0]
                pickcode = info["pc"]
            else:
                if hasattr(self, "upload_file_sample"):
                    resp = self.upload_file_sample(b"", "U_120_0")
                    check_response(resp)
                    pickcode = resp["data"]["pick_code"]
                else:
                    resp = self.upload_file(b"", filename="test")
                    pickcode = resp["data"]["pickcode"]
                    try:
                        self.fs_delete(self.to_id(pickcode))
                    except Exception:
                        pass
            return set_stable_point(self.user_id, pickcode)

    @overload
    def refresh_access_token(
        self,
        /,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def refresh_access_token(
        self,
        /,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def refresh_access_token(
        self,
        /,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """更新 access_token 和 refresh_token （⚠️ 目前是 7200 秒内就要求刷新一次）"""

        def gen_step():
            if refresh_token := getattr(self, "refresh_token", ""):
                resp = yield self.login_refresh_token_open(
                    refresh_token,
                    async_=async_,
                    **request_kwargs,
                )
            elif app_id := self.app_id:
                if hasattr(self, "login_with_open"):
                    resp = yield self.login_with_open(
                        app_id,
                        async_=async_,
                        **request_kwargs,
                    )
                else:
                    resp = yield self.login_with_app_id(
                        app_id,
                        console_qrcode=True,
                        async_=async_,
                        **request_kwargs,
                    )
            else:
                raise RuntimeError("no `refresh_token` or `app_id` provided")
            check_response(resp)
            data = resp["data"]
            self.refresh_token = data["refresh_token"]
            self.access_token = data["access_token"]
            return data

        return run_gen_step(gen_step, async_)

    ########## Cloud Download API ##########

    @overload
    def clouddownload_quota_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def clouddownload_quota_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def clouddownload_quota_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取云下载配额信息

        GET https://proapi.115.com/open/offline/get_quota_info

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/gif2n3smh54kyg0p
        """
        api = complete_url("/open/offline/get_quota_info", base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def clouddownload_task_add_bt(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def clouddownload_task_add_bt(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def clouddownload_task_add_bt(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """添加云下载 BT 任务

        POST https://proapi.115.com/open/offline/add_task_bt

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/svfe4unlhayvluly

        :payload:
            - info_hash: str 💡 种子文件的 info_hash
            - pick_code: str 💡 种子文件的提取码
            - save_path: str 💡 保存到 `wp_path_id` 对应目录下的相对路径
            - torrent_sha1: str 💡 种子文件的 sha1
            - wanted: str 💡 选择文件进行下载（是数字索引，从 0 开始计数，用 "," 分隔）
            - wp_path_id: int | str = <default> 💡 保存目标目录 id
        """
        api = complete_url("/open/offline/add_task_bt ", base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def clouddownload_task_add_urls(
        self,
        payload: str | Iterable[str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def clouddownload_task_add_urls(
        self,
        payload: str | Iterable[str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def clouddownload_task_add_urls(
        self,
        payload: str | Iterable[str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """添加云下载链接任务

        POST https://proapi.115.com/open/offline/add_task_urls

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/zkyfq2499gdn3mty

        :payload:
            - urls: str 💡 链接，用 "\\n" 分隔，支持HTTP、HTTPS、FTP、磁力链和电驴链接
            - wp_path_id: int | str = <default> 💡 保存到目录的 id
        """
        api = complete_url("/open/offline/add_task_urls", base_url)
        if isinstance(payload, str):
            payload = {"urls": payload.strip("\n")}
        elif not isinstance(payload, dict):
            payload = {"urls": ",".join(payload)}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def clouddownload_task_clear(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def clouddownload_task_clear(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def clouddownload_task_clear(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """清空云下载任务

        POST https://proapi.115.com/open/offline/clear_task

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/uu5i4urb5ylqwfy4

        :payload:
            - flag: int = 0 💡 标识，用于对应某种情况

                - 0: 已完成
                - 1: 全部
                - 2: 已失败
                - 3: 进行中
                - 4: 已完成+删除源文件
                - 5: 全部+删除源文件
        """
        api = complete_url("/open/offline/clear_task", base_url)
        if isinstance(payload, int):
            payload = {"flag": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def clouddownload_task_del(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def clouddownload_task_del(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def clouddownload_task_del(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除云下载任务

        POST https://proapi.115.com/open/offline/del_task

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/pmgwc86lpcy238nw

        :payload:
            - info_hash: str 💡 待删除任务的 info_hash
            - del_source_file: 0 | 1 = <default> 💡 是否删除源文件 1:删除 0:不删除
        """
        api = complete_url("/open/offline/del_task", base_url)
        if isinstance(payload, str):
            payload = {"info_hash": payload}
        return self.request(
            api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def clouddownload_task_list(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def clouddownload_task_list(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def clouddownload_task_list(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取云下载任务列表

        GET https://proapi.115.com/open/offline/get_task_list

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/av2mluz7uwigz74k

        :payload:
            - page: int = 1
        """
        api = complete_url("/open/offline/get_task_list", base_url)
        if isinstance(payload, int):
            payload = {"page": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def clouddownload_torrent(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def clouddownload_torrent(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def clouddownload_torrent(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """解析 BT 种子

        POST https://proapi.115.com/open/offline/torrent

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/evez3u50cemoict1

        :payload:
            - torrent_sha1: str 💡 种子文件的 sha1
            - pick_code: str    💡 种子文件的提取码
        """
        api = complete_url("/open/offline/torrent", base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    ########## Download API ##########

    @overload
    def download_url(
        self,
        pickcode: int | str,
        /,
        strict: bool = True,
        user_agent: None | str = None,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> P115URL: ...
    @overload
    def download_url(
        self,
        pickcode: int | str,
        /,
        strict: bool = True,
        user_agent: None | str = None,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, P115URL]: ...
    def download_url(
        self,
        pickcode: int | str,
        /,
        strict: bool = True,
        user_agent: None | str = None,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> P115URL | Coroutine[Any, Any, P115URL]:
        """获取文件的下载链接，此接口是对 `download_url_info` 的封装

        .. note::
            获取的直链中，部分查询参数的解释：

            - ``t``: 过期时间戳
            - ``u``: 用户 id
            - ``c``: 允许同时打开次数，如果为 0，则是无限次数
            - ``f``: 请求时要求携带请求头
                - 如果为空，则无要求
                - 如果为 1，则需要 user-agent（和请求直链时的一致）
                - 如果为 3，则需要 user-agent（和请求直链时的一致） 和 Cookie（由请求直链时的响应所返回的 Set-Cookie 响应头）

        :param pickcode: id 或者提取码
        :param strict: 如果为 True，当目标是目录时，会抛出 IsADirectoryError 异常
        :param user_agent: 如果不为 None，则作为请求头 "user-agent" 的值
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 下载链接
        """
        pickcode = self.to_pickcode(pickcode)

        def gen_step():
            resp = yield self.download_url_info_open(
                pickcode,
                user_agent=user_agent,
                async_=async_,
                **request_kwargs,
            )
            resp["pickcode"] = pickcode
            resp["is_download"] = True
            data = resp.get("data")
            if not data:
                resp["state"] = False
                resp["errno"] = resp.get("errno") or 50015
                resp.setdefault("message", "文件不存在、是目录或者不支持此操作")
            check_response(resp)
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
    def download_urls(
        self,
        pickcodes: int | str | Iterable[int | str],
        /,
        strict: bool = True,
        user_agent: None | str = None,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict[int, P115URL]: ...
    @overload
    def download_urls(
        self,
        pickcodes: int | str | Iterable[int | str],
        /,
        strict: bool = True,
        user_agent: None | str = None,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict[int, P115URL]]: ...
    def download_urls(
        self,
        pickcodes: int | str | Iterable[int | str],
        /,
        strict: bool = True,
        user_agent: None | str = None,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict[int, P115URL] | Coroutine[Any, Any, dict[int, P115URL]]:
        """批量获取文件的下载链接，此接口是对 `download_url_info` 的封装

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
        :param strict: 如果为 True，当目标是目录时，会直接忽略
        :param user_agent: 如果不为 None，则作为请求头 "user-agent" 的值
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 一批下载链接
        """
        if isinstance(pickcodes, (int, str)):
            pickcodes = self.to_pickcode(pickcodes)
        else:
            pickcodes = ",".join(map(self.to_pickcode, pickcodes))

        def gen_step():
            resp = yield self.download_url_info_open(
                pickcodes,
                user_agent=user_agent,
                async_=async_,
                **request_kwargs,
            )
            resp["pickcode"] = pickcodes
            resp["is_download"] = True
            data = resp.get("data")
            if not data:
                resp["state"] = False
                resp["errno"] = resp.get("errno") or 50015
                resp.setdefault("message", "文件不存在、是目录或者不支持此操作")
                throw(errno.EIO, resp)
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
    def download_url_info(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def download_url_info(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def download_url_info(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件的下载链接

        POST https://proapi.115.com/open/ufile/downurl

        .. hint::
            相当于 `P115Client.download_url_app(app="chrome")`

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/um8whr91bxb5997o

        :payload:
            - pick_code: str 💡 提取码，多个用逗号 "," 隔开
        """
        api = complete_url("/open/ufile/downurl", base_url)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        headers = request_kwargs["headers"] = dict(request_kwargs.get("headers") or ())
        if user_agent is None:
            headers.setdefault("user-agent", "")
        else:
            headers["user-agent"] = user_agent

        def parse(_, content: bytes, /) -> dict:
            json = json_maybe_decrypt_loads(content)
            json["headers"] = headers
            return json

        request_kwargs.setdefault("parse", parse)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    ########## File System API ##########

    @overload
    def fs_copy(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_copy(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_copy(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """文件复制

        POST https://proapi.115.com/open/ufile/copy

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/lvas49ar94n47bbk

        .. caution::
            ⚠️ 请不要并发执行，限制在 5 万个文件和目录以内

        :payload:
            - file_id: int | str 💡 文件或目录的 id，多个用逗号 "," 隔开
            - pid: int | str = 0 💡 父目录 id
            - nodupli: 0 | 1 = 0 💡 复制的文件在目标目录是否允许重复：0:可以 1:不可以
        """
        api = complete_url("/open/ufile/copy", base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        elif not isinstance(payload, dict):
            payload = {"file_id": ",".join(map(str, payload))}
        cast(dict, payload).setdefault("pid", pid)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_delete(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_delete(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_delete(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除文件或目录

        POST https://proapi.115.com/open/ufile/delete

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/kt04fu8vcchd2fnb

        .. caution::
            ⚠️ 请不要并发执行，限制在 5 万个文件和目录以内

        :payload:
            - file_ids: int | str 💡 文件或目录的 id，多个用逗号 "," 隔开
        """
        api = complete_url("/open/ufile/delete", base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_ids": payload}
        elif not isinstance(payload, dict):
            payload = {"file_ids": ",".join(map(str, payload))}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_files(
        self,
        payload: None | int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_files(
        self,
        payload: None | int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_files(
        self,
        payload: None | int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录中的文件列表和基本信息

        GET https://proapi.115.com/open/ufile/files

        .. hint::
            相当于 ``P115Client.fs_files_app()``

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/kz9ft9a7s57ep868

        :payload:
            - cid: int | str = 0 💡 目录 id，对应 parent_id
            - limit: int = 32 💡 分页大小，最大值不一定，看数据量，7,000 应该总是安全的，10,000 有可能报错，但有时也可以 20,000 而成功
            - offset: int = 0 💡 分页开始的索引，索引从 0 开始计算

            - aid: int = 1 💡 area_id

                - 0: 会被视为 1
                - 1: 正常文件
                - 2: <unknown>
                - 3: <unknown>
                - 4: <unknown>
                - 5: <unknown>
                - 7: 回收站文件
                - 9: <unknown>
                - 12: 瞬间文件
                - 15: <unknown>
                - 120: 彻底删除文件、简历附件
                - <其它>: 会被视为 0

            - asc: 0 | 1 = <default> 💡 是否升序排列。0:降序 1:升序
            - count_folders: 0 | 1 = 1 💡 统计文件数和目录数
            - cur: 0 | 1 = <default>   💡 是否只显示当前目录
            - custom_order: 0 | 1 | 2 = <default> 💡 是否使用记忆排序。如果指定了 "asc"、"fc_mix"、"o" 中其一，则此参数会被自动设置为 2

                - 0: 使用记忆排序（自定义排序失效）
                - 1: 使用自定义排序（不使用记忆排序）
                - 2: 自定义排序（非目录置顶）

            - fc_mix: 0 | 1 = <default> 💡 是否目录和文件混合，如果为 0 则目录在前（目录置顶）
            - fields: str = <default>
            - for: str = <default> 💡 文件格式，例如 "doc"
            - is_q: 0 | 1 = <default>
            - is_share: 0 | 1 = <default>
            - min_size: int = 0 💡 最小的文件大小
            - max_size: int = 0 💡 最大的文件大小（含），<= 0 表示不限，因此并不能借此仅筛选出空文件
            - natsort: 0 | 1 = <default> 💡 是否执行自然排序(natural sorting)
            - nf: 0 | 1 = <default> 💡 不要显示文件（即仅显示目录），但如果 show_dir=0，则此参数无效
            - o: str = <default> 💡 用某字段排序

                - "file_name": 文件名
                - "file_size": 文件大小
                - "file_type": 文件种类
                - "user_etime": 事件时间（无效，效果相当于 "user_utime"）
                - "user_utime": 修改时间
                - "user_ptime": 创建时间（无效，效果相当于 "user_utime"）
                - "user_otime": 上一次打开时间（无效，效果相当于 "user_utime"）

            - qid: int = <default>
            - r_all: 0 | 1 = <default>
            - record_open_time: 0 | 1 = 1 💡 是否要记录目录的打开时间
            - scid: int | str = <default>
            - show_dir: 0 | 1 = 1 💡 是否显示目录
            - snap: 0 | 1 = <default>
            - source: str = <default>
            - star: 0 | 1 = <default> 💡 是否星标文件
            - stdir: 0 | 1 = <default> 💡 筛选文件时，是否显示目录：1:展示 0:不展示
            - suffix: str = <default> 💡 后缀名（优先级高于 `type`）
            - type: int = <default> 💡 文件类型

                - 0: 全部（仅当前目录）
                - 1: 文档
                - 2: 图片
                - 3: 音频
                - 4: 视频
                - 5: 压缩包
                - 6: 软件/应用
                - 7: 书籍
                - 8: 其它
                - 9: 相当于 8
                - 10: 相当于 8
                - 11: 相当于 8
                - 12: ？？？
                - 13: ？？？
                - 14: ？？？
                - 15: 图片和视频，相当于 2 和 4
                - >= 16: 相当于 8
        """
        api = complete_url("/open/ufile/files", base_url)
        if payload is None:
            return self.request(url=api, async_=async_, **request_kwargs)
        if isinstance(payload, (int, str)):
            payload = {"cid": payload}
        payload = {
            "aid": 1,
            "count_folders": 1,
            "limit": 32,
            "offset": 0,
            "record_open_time": 1,
            "show_dir": 1,
            "cid": 0,
            **payload,
        }
        if payload.keys() & frozenset(("asc", "fc_mix", "o")):
            payload["custom_order"] = 2
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_info(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        method: str = "GET",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_info(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        method: str = "GET",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_info(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        method: str = "GET",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件或目录详情

        GET https://proapi.115.com/open/folder/get_info

        .. note::
            支持 GET 和 POST 方法。`file_id` 和 `path` 需必传一个

        .. hint::
            具有 ``P115Client.fs_category_get()`` 的能力，而且更强，因为支持用 path 查询

        .. caution::
            尝试获取目录的信息时，会去计算目录中文件和目录的数量、总文件大小 等信息，可能会消耗大量时间，但短时间内再次查询同一目录，耗时可能会大大减小

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/rl8zrhe2nag21dfw

        :payload:
            - file_id: int | str 💡 文件或目录的 id
            - path: str = <default> 💡 文件或目录的路径。分隔符支持 / 和 > 两种符号，最前面需分隔符开头，以分隔符分隔目录层级
        """
        api = complete_url("/open/folder/get_info", base_url)
        if isinstance(payload, int):
            payload = {"file_id": payload}
        elif isinstance(payload, str):
            if payload.startswith("0") or payload.strip(digits):
                payload = {"path": payload}
            else:
                payload = {"file_id": payload}
        if path := payload.get("path"):
            if path.startswith(("/", ">")):
                sep = path[0]
                payload["path"] = sep + path.strip(sep)
            elif ">" in path:
                payload["path"] = "/" + path.rstrip("/")
            else:
                payload["path"] = ">" + path.rstrip(">")
        if method.upper() == "POST":
            request_kwargs["data"] = payload
        else:
            request_kwargs["params"] = payload
        return self.request(url=api, method=method, async_=async_, **request_kwargs)

    @overload
    def fs_mkdir(
        self,
        payload: str | dict,
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_mkdir(
        self,
        payload: str | dict,
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_mkdir(
        self,
        payload: str | dict,
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """新建目录

        POST https://proapi.115.com/open/folder/add

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/qur839kyx9cgxpxi

        :payload:
            - file_name: str     💡 新建目录名称，限制 255 个字符
            - pid: int | str = 0 💡 新建目录所在的父目录ID (根目录的ID为0)
        """
        api = complete_url("/open/folder/add", base_url)
        if isinstance(payload, str):
            payload = {"pid": pid, "file_name": payload}
        payload.setdefault("pid", pid)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_move(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_move(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_move(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """文件移动

        POST https://proapi.115.com/open/ufile/move

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/vc6fhi2mrkenmav2

        .. caution::
            ⚠️ 请不要并发执行，限制在 5 万个文件和目录以内

        :payload:
            - file_ids: int | str 💡 文件或目录的 id，多个用逗号 "," 隔开
            - to_cid: int | str = 0 💡 父目录 id
        """
        api = complete_url("/open/ufile/move", base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_ids": payload}
        elif not isinstance(payload, dict):
            payload = {"file_ids": ",".join(map(str, payload))}
        cast(dict, payload).setdefault("to_cid", pid)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_rename(
        self,
        payload: tuple[int | str, str] | dict,
        /,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_rename(
        self,
        payload: tuple[int | str, str] | dict,
        /,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_rename(
        self,
        payload: tuple[int | str, str] | dict,
        /,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """重命名文件或目录，此接口是对 `fs_update_open` 的封装

        .. caution::
            改名时，虽然不能修改扩展名，但是一定要带上扩展名（无论是啥），不然会把最后一个句点 . 及其之后文字截断

        :payload:
            - file_id: int | str 💡 文件 id
            - file_name: str     💡 文件名
        """
        if isinstance(payload, tuple):
            payload = {"file_id": payload[0], "file_name": payload[1]}
        return self.fs_update_open(payload, async_=async_, **request_kwargs)

    @overload
    def fs_search(
        self,
        payload: str | dict = ".",
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_search(
        self,
        payload: str | dict = ".",
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_search(
        self,
        payload: str | dict = ".",
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """搜索文件或目录

        GET https://proapi.115.com/open/ufile/search

        .. attention::
            最多只能取回前 10,000 条数据，也就是 `limit + offset <= 10_000`，不过可以一次性取完

            不过就算正确设置了 `limit` 和 `offset`，并且总数据量大于 `limit + offset`，可能也不足 `limit`，这应该是 bug，也就是说，就算数据总量足够你也取不到足量

            它返回数据中的 `count` 字段的值表示总数据量（即使你只能取前 10,000 条），往往并不准确，最多能当作一个可参考的估计值

        .. note::
            这个方法似乎不支持仅搜索目录本身，搜索范围是从指定目录开始的整个目录树

        .. hint::
            相当于 ``P115Client.fs_search_app2()``

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/ft2yelxzopusus38

        :payload:
            - aid: int = 1 💡 area_id

                - 0: 会被视为 1
                - 1: 正常文件
                - 2: <unknown>
                - 3: <unknown>
                - 4: <unknown>
                - 5: <unknown>
                - 7: 回收站文件
                - 9: <unknown>
                - 12: 瞬间文件
                - 15: <unknown>
                - 120: 彻底删除文件、简历附件
                - <其它>: 会被视为 0

            - asc: 0 | 1 = <default> 💡 是否升序排列
            - cid: int | str = 0 💡 目录 id。cid=-1 时，表示不返回列表任何内容
            - count_folders: 0 | 1 = <default>
            - date: str = <default> 💡 筛选日期
            - fc: 0 | 1 = <default> 💡 只显示文件或目录。1:只显示目录 2:只显示文件
            - fc_mix: 0 | 1 = <default> 💡 是否目录和文件混合，如果为 0 则目录在前（目录置顶）
            - file_label: int | str = <default> 💡 标签 id
            - gte_day: str 💡 搜索结果匹配的开始时间；格式：YYYY-MM-DD
            - limit: int = 32 💡 一页大小，意思就是 page_size
            - lte_day: str 💡 搜索结果匹配的结束时间；格式：YYYY-MM-DD
            - o: str = <default> 💡 用某字段排序

                - "file_name": 文件名
                - "file_size": 文件大小
                - "file_type": 文件种类
                - "user_utime": 修改时间
                - "user_ptime": 创建时间
                - "user_otime": 上一次打开时间

            - offset: int = 0  💡 索引偏移，索引从 0 开始计算
            - search_value: str = "." 💡 搜索文本，可以是 sha1
            - source: str = <default>
            - star: 0 | 1 = <default> 💡 是否星标文件
            - suffix: str = <default> 💡 后缀名（优先级高于 `type`）
            - type: int = <default> 💡 文件类型

                - 0: 全部（仅当前目录）
                - 1: 文档
                - 2: 图片
                - 3: 音频
                - 4: 视频
                - 5: 压缩包
                - 6: 软件/应用
                - 7: 书籍
                - 99: 所有文件

            - version: str = <default> 💡 版本号，比如 3.1
        """
        api = complete_url("/open/ufile/search", base_url)
        if isinstance(payload, str):
            payload = {"search_value": payload}
        payload = {
            "aid": 1,
            "cid": 0,
            "limit": 32,
            "offset": 0,
            "show_dir": 1,
            "search_value": ".",
            **payload,
        }
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_star_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        star: bool = True,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_star_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        star: bool = True,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_star_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        star: bool = True,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """为文件或目录设置或取消星标，此接口是对 `fs_update_open` 的封装

        .. note::
            即使其中任何一个 id 目前已经被删除，也可以操作成功

        :payload:
            - file_id: int | str    💡 只能传入 1 个
            - file_id[0]: int | str 💡 如果有多个，则按顺序给出
            - file_id[1]: int | str
            - ...
            - star: 0 | 1 = 1
        """
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        elif not isinstance(payload, dict):
            payload = {f"file_id[{i}]": id for i, id in enumerate(payload)}
        payload.setdefault("star", int(star))
        return self.fs_update_open(payload, async_=async_, **request_kwargs)

    @overload
    def fs_video(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_video(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_video(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取视频在线播放地址（和视频文件相关数据）

        GET https://proapi.115.com/open/video/play

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/hqglxv3cedi3p9dz

        .. hint::
            需切换音轨时，在请求返回的播放地址中增加请求参数 `&audio_track=${index}`，值就是接口响应中 `multitrack_list` 中某个成员的索引，从 0 开始计数

        :payload:
            - pick_code: str 💡 文件提取码
            - share_id: int | str = <default> 💡 共享 id，获取共享文件播放地址所需
        """
        api = complete_url("/open/video/play", base_url)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_video_history(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_video_history(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_video_history(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取视频播放进度

        GET https://proapi.115.com/open/video/history

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/gssqdrsq6vfqigag

        :payload:
            - pick_code: str 💡 文件提取码
        """
        api = complete_url("/open/video/history", base_url)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_video_history_set(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_video_history_set(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_video_history_set(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """记忆视频播放进度

        POST https://proapi.115.com/open/video/history

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/bshagbxv1gzqglg4

        :payload:
            - pick_code: str 💡 文件提取码
            - time: int = <default> 💡 视频播放进度时长 (单位秒)
            - watch_end: int = <default> 💡 视频是否播放播放完毕 0:未完毕 1:完毕
        """
        api = complete_url("/open/video/history", base_url)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_video_push(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_video_push(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_video_push(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """提交视频转码

        POST https://proapi.115.com/open/video/video_push

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/nxt8r1qcktmg3oan

        :payload:
            - pick_code: str 💡 文件提取码
            - op: str = "vip_push" 💡 提交视频加速转码方式

                - "vip_push": 根据；vip 等级加速
                - "pay_push": 枫叶加速
        """
        api = complete_url("/open/video/video_push", base_url)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        payload.setdefault("op", "vip_push")
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_video_subtitle(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_video_subtitle(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_video_subtitle(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """视频字幕列表

        GET https://proapi.115.com/open/video/subtitle

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/nx076h3glapoyh7u

        :payload:
            - pick_code: str 💡 文件提取码
        """
        api = complete_url("/open/video/subtitle", base_url)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def fs_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def fs_update(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置文件或目录（备注、标签、封面等）

        POST https://proapi.115.com/open/ufile/update

        .. hint::
            即使文件已经被删除，也可以操作成功

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/gyrpw5a0zc4sengm

        :payload:
            - file_id: int | str    💡 只能传入 1 个
            - file_id[0]: int | str 💡 如果有多个，则按顺序给出
            - file_id[1]: int | str
            - ...
            - file_name: str = <default> 💡 文件名
            - star: 0 | 1 = <default> 💡 是否星标：0:取消星标 1:设置星标
            - ...
        """
        api = complete_url("/open/ufile/update", base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    ########## Recyclebin API ##########

    @overload
    def recyclebin_clean(
        self,
        payload: int | str | Iterable[int | str] | dict = {},
        /,
        password: str = "000000",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def recyclebin_clean(
        self,
        payload: int | str | Iterable[int | str] | dict = {},
        /,
        password: str = "000000",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def recyclebin_clean(
        self,
        payload: int | str | Iterable[int | str] | dict = {},
        /,
        password: str = "000000",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """回收站：删除或清空

        POST https://proapi.115.com/open/rb/del

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/gwtof85nmboulrce

        .. note::
            ``password`` 参数是不用传的

        :payload:
            - tid: int | str 💡 不传就是清空，多个用逗号 "," 隔开
        """
        api = complete_url("/open/rb/del", base_url)
        if isinstance(payload, (int, str)):
            payload = {"tid": payload}
        elif not isinstance(payload, dict):
            payload = {"tid": ",".join(map(str, payload))}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def recyclebin_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def recyclebin_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def recyclebin_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """回收站：列表

        GET https://proapi.115.com/open/rb/list

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/bg7l4328t98fwgex

        :payload:
            - limit: int = 32
            - offset: int = 0
        """
        api = complete_url("/open/rb/list", base_url)
        if isinstance(payload, int):
            payload = {"limit": 32, "offset": payload}
        payload.setdefault("limit", 32)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def recyclebin_revert(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def recyclebin_revert(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def recyclebin_revert(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """回收站：还原

        POST https://proapi.115.com/open/rb/revert

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/gq293z80a3kmxbaq

        .. caution::
            ⚠️ 请不要并发执行，限制在 5 万个文件和目录以内

        :payload:
            - tid: int | str 💡 多个用逗号 "," 隔开
        """
        api = complete_url("/open/rb/revert", base_url)
        if isinstance(payload, (int, str)):
            payload = {"tid": payload}
        elif not isinstance(payload, dict):
            payload = {"tid": ",".join(map(str, payload))}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    ########## Upload API ##########

    @overload
    def upload_gettoken_open(
        self,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def upload_gettoken_open(
        self,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def upload_gettoken_open(
        self,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取阿里云 OSS 的 token（上传凭证）

        GET https://proapi.115.com/open/upload/get_token

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/kzacvzl0g7aiyyn4
        """
        api = complete_url("/open/upload/get_token", base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def upload_init(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def upload_init(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def upload_init(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """初始化上传任务，可能秒传

        POST https://proapi.115.com/open/upload/init

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/ul4mrauo5i2uza0q

        :payload:
            - file_name: str 💡 文件名
            - fileid: str 💡 文件的 sha1 值
            - file_size: int 💡 文件大小，单位是字节
            - target: str 💡 上传目标，格式为 f"U_{aid}_{pid}" 或 f"S_{share_id}_{pid}"
            - topupload: int = 0 💡 上传调度文件类型调度标记

                -  0: 单文件上传任务标识 1 条单独的文件上传记录
                -  1: 目录任务调度的第 1 个子文件上传请求标识 1 次目录上传记录
                -  2: 目录任务调度的其余后续子文件不作记作单独上传的上传记录
                - -1: 没有该参数

            - sign_key: str = "" 💡 2 次验证时读取文件的范围
            - sign_val: str = "" 💡 2 次验证的签名值
        """
        api = complete_url("/open/upload/init", base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def upload_resume(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def upload_resume(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def upload_resume(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取恢复断点续传所需信息

        POST https://proapi.115.com/open/upload/resume

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/tzvi9sbcg59msddz

        :payload:
            - pick_code: str 💡 上传任务 key
            - target: str    💡 上传目标，默认为 "U_1_0"，格式为 f"U_{aid}_{pid}" 或 f"S_{share_id}_{pid}"
            - fileid: str    💡 文件的 sha1 值（⚠️ 可以是任意值）
            - file_size: int 💡 文件大小，单位是字节（⚠️ 可以是任意值）
        """
        api = complete_url("/open/upload/resume", base_url)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        else:
            payload = dict(payload)
            if "pick_code" not in payload:
                if "pickcode" in payload:
                    payload["pick_code"] = payload["pickcode"]
            callback_var: None | dict = None
            if "callback_var" in payload:
                callback_var = loads(payload["callback_var"])
            elif "callback" in payload:
                callback_var = loads(payload["callback"]["callback_var"])
            if callback_var:
                payload.update(
                    pick_code=callback_var["x:pick_code"],
                    target=callback_var["x:target"],
                )
        payload.setdefault("fileid", "0" * 40)
        payload.setdefault("file_size", 1)
        payload.setdefault("target", "U_1_0")
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def upload_file_init(
        self,
        /,
        filename: str,
        filesha1: str,
        filesize: int,
        dirname: str = "",
        read_range_bytes_or_hash: None | Callable[[str], str | Buffer] = None,
        pid: int | str = 0,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def upload_file_init(
        self,
        /,
        filename: str,
        filesha1: str,
        filesize: int,
        dirname: str = "",
        read_range_bytes_or_hash: None | Callable[[str], str | Buffer] = None,
        pid: int | str = 0,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def upload_file_init(
        self,
        /,
        filename: str,
        filesha1: str,
        filesize: int,
        dirname: str = "",
        read_range_bytes_or_hash: None | Callable[[str], str | Buffer] = None,
        pid: int | str = 0,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """初始化上传，可能秒传，此接口是对 `upload_init_open` 的封装

        .. note::
            - 文件大小 和 sha1 是必需的，只有 sha1 是没用的。
            - 如果文件大于等于 1 MB (1048576 B)，就需要 2 次检验一个范围哈希，就必须提供 `read_range_bytes_or_hash`

        :param filename: 文件名
        :param filesha1: 文件的 sha1
        :param filesize: 文件大小
        :param dirname: 保存目录，是在 `pid` 对应目录下的相对路径，默认为 `pid` 所对应目录本身
        :param read_range_bytes_or_hash: 调用以获取 2 次验证的数据或计算 sha1，接受一个数据范围，格式符合:
            `HTTP Range Requests <https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests>`_，
            返回值如果是 str，则视为计算好的 sha1，如果为 Buffer，则视为数据（之后会被计算 sha1）
        :param pid: 上传文件到此目录的 id，或者指定的 target（格式为 f"U_{aid}_{pid}" 或 f"S_{share_id}_{pid}"，但若 `aid != 1`，则会报参数错误）
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 接口响应
        """

        def gen_step():
            if isinstance(pid, str) and pid.startswith(("U_", "S_")):
                target = pid
            else:
                target = f"U_1_{pid}"
            payload = {
                "file_name": filename,
                "fileid": filesha1.upper(),
                "file_size": filesize,
                "target": target,
                "path": dirname,
                "topupload": 1,
            }
            resp = yield self.upload_init_open(
                payload,
                async_=async_,
                **request_kwargs,
            )
            if not resp["state"]:
                return resp
            data = resp["data"]
            if data["status"] == 7:
                if read_range_bytes_or_hash is None:
                    raise ValueError(
                        "filesize >= 1 MB, thus need pass the `read_range_bytes_or_hash` argument"
                    )
                payload["sign_key"] = data["sign_key"]
                sign_check: str = data["sign_check"]
                content: str | Buffer
                if async_:
                    content = yield ensure_async(read_range_bytes_or_hash)(sign_check)
                else:
                    content = read_range_bytes_or_hash(sign_check)
                if isinstance(content, str):
                    payload["sign_val"] = content.upper()
                else:
                    payload["sign_val"] = sha1(content).hexdigest().upper()
                resp = yield self.upload_init_open(
                    payload,
                    async_=async_,  # type: ignore
                    **request_kwargs,
                )
            resp["reuse"] = resp["data"].get("status") == 2
            return resp

        return run_gen_step(gen_step, async_)

    @overload
    def upload_file(
        self,
        /,
        file: Buffer | str | PathLike | URL | SupportsGeturl | SupportsRead,
        pid: int | str = 0,
        share_id: int = 0,
        filename: str = "",
        filesha1: str = "",
        filesize: int = -1,
        dirname: str = "",
        payload: None | Mapping = None,
        partsize: int = 0,
        callback: None | dict = None,
        upload_id: str = "",
        endpoint: str = "https://oss-cn-shenzhen.aliyuncs.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def upload_file(
        self,
        /,
        file: Buffer | str | PathLike | URL | SupportsGeturl | SupportsRead,
        pid: int | str = 0,
        share_id: int = 0,
        filename: str = "",
        filesha1: str = "",
        filesize: int = -1,
        dirname: str = "",
        payload: None | Mapping = None,
        partsize: int = 0,
        callback: None | dict = None,
        upload_id: str = "",
        endpoint: str = "https://oss-cn-shenzhen.aliyuncs.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def upload_file(
        self,
        /,
        file: Buffer | str | PathLike | URL | SupportsGeturl | SupportsRead,
        pid: int | str = 0,
        share_id: int = 0,
        filename: str = "",
        filesha1: str = "",
        filesize: int = -1,
        dirname: str = "",
        payload: None | Mapping = None,
        partsize: int = 0,
        callback: None | dict = None,
        upload_id: str = "",
        endpoint: str = "https://oss-cn-shenzhen.aliyuncs.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """上传文件

        .. note::
            如果提供了 ``callback``，则强制为分块上传。
            此时，最好提供一下 ``upload_id``，否则就是从头开始。
            此时可以省略 ``pid``、``filename``、``filesha1``、``filesize``、``partsize``

        .. caution::
            ``partsize > 0`` 时，不要把 ``partsize`` 设置得太小，起码得 10 MB (10485760) 以上

        :param file: 待上传的文件
        :param pid: 上传文件到此目录的 id 或 pickcode，或者指定的 target（格式为 f"U_{aid}_{pid}" 或 f"S_{share_id}_{pid}"，但若 `aid != 1`，则会报参数错误）
        :param share_id: 共享 id
        :param filename: 文件名，如果为空，则会自动确定
        :param filesha1: 文件的 sha1，如果为空，则会自动确定
        :param filesize: 文件大小，如果为 -1，则会自动确定
        :param dirname: 保存目录，是在 `pid` 对应目录下的相对路径，默认为 `pid` 所对应目录本身
        :param payload: 其它的查询参数
        :param partsize: 分块上传的分块大小。如果为 0，则不做分块上传；如果 < 0，则会自动确定
        :param callback: 回调数据
        :param upload_id: 上传任务 id
        :param endpoint: 上传目的网址
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 接口响应
        """
        request_kwargs["headers"] = dict(
            request_kwargs.get("headers") or (),
            authorization=self.headers["authorization"],
        )
        return upload_file(
            file=file,
            pid=pid,
            share_id=share_id,
            filename=filename,
            filesha1=filesha1,
            filesize=filesize,
            dirname=dirname,
            payload=payload,
            partsize=partsize,
            callback=callback,
            upload_id=upload_id,
            endpoint=endpoint,
            async_=async_,  # type: ignore
            **request_kwargs,
        )

    ########## User API ##########

    @overload
    def user_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def user_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def user_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取用户信息

        GET https://proapi.115.com/open/user/info

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/ot1litggzxa1czww
        """
        api = complete_url("/open/user/info", base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    ########## Other API ##########s

    @overload
    def vip_qr_url(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...
    @overload
    def vip_qr_url(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...
    def vip_qr_url(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取产品列表地址（即引导用户扫码购买 115 的 VIP 服务，以获取提成）

        GET https://proapi.115.com/open/vip/qr_url

        .. admonition:: Reference

            https://www.yuque.com/115yun/open/cguk6qshgapwg4qn#oByvI

        :payload:
            - open_device: int
            - default_product_id: int = <default> 💡 打开产品列表默认选中的产品对应的产品id，如果没有则使用默认的产品顺序。

                - 月费: 5
                - 年费: 1
                - 尝鲜1天: 101
                - 长期VIP(长期): 24072401
                - 超级VIP: 24072402
        """
        api = complete_url("/open/vip/qr_url", base_url)
        if not isinstance(payload, dict):
            payload = {"open_device": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    clouddownload_quota_info_open = clouddownload_quota_info
    clouddownload_task_add_bt_open = clouddownload_task_add_bt
    clouddownload_task_add_urls_open = clouddownload_task_add_urls
    clouddownload_task_clear_open = clouddownload_task_clear
    clouddownload_task_del_open = clouddownload_task_del
    clouddownload_task_list_open = clouddownload_task_list
    clouddownload_torrent_open = clouddownload_torrent
    download_url_open = download_url
    download_urls_open = download_urls
    download_url_info_open = download_url_info
    fs_copy_open = fs_copy
    fs_delete_open = fs_delete
    fs_files_open = fs_files
    fs_info_open = fs_info
    fs_mkdir_open = fs_mkdir
    fs_move_open = fs_move
    fs_rename_open = fs_rename
    fs_search_open = fs_search
    fs_star_set_open = fs_star_set
    fs_video_open = fs_video
    fs_video_history_open = fs_video_history
    fs_video_history_set_open = fs_video_history_set
    fs_video_push_open = fs_video_push
    fs_video_subtitle_open = fs_video_subtitle
    fs_update_open = fs_update
    recyclebin_clean_open = recyclebin_clean
    recyclebin_list_open = recyclebin_list
    recyclebin_revert_open = recyclebin_revert
    upload_init_open = upload_init
    upload_resume_open = upload_resume
    user_info_open = user_info
    upload_file_init_open = upload_file_init
    upload_file_open = upload_file
    vip_qr_url_open = vip_qr_url

    to_id = staticmethod(to_id)

    def to_pickcode(
        self,
        id: int | str,
        /,
        prefix: Literal["a", "b", "c", "d", "e", "fa", "fb", "fc", "fd", "fe"] = "a",
        stable_point: str = "",
    ) -> str:
        """把可能是 id 或 pickcode 的一律转换成 pickcode

        .. note::
            规定：空提取码 "" 对应的 id 是 0

        :param id: 可能是 id 或 pickcode
        :param prefix: 前缀
        :param stable_point: 提取码的本征值，不同用户的值不同，你也可以直接传一个此用户的有效 pickcode

        :return: pickcode
        """
        return to_pickcode(
            id,
            stable_point=stable_point or self.pickcode_stable_point,
            prefix=prefix,
        )
