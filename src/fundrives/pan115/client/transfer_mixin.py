#!/usr/bin/env python3

from __future__ import annotations

from typing import Any, Literal, overload

from ._common import (
    CRE_SET_COOKIE,
    P115URL,
    URL,
    AsyncIterable,
    Buffer,
    Callable,
    Cookie,
    Coroutine,
    Iterable,
    Mapping,
    PathLike,
    SupportsGeturl,
    SupportsRead,
    _app_version,
    _rsa_decrypt,
    b64encode,
    check_response,
    complete_url,
    dict_update,
    dumps,
    ecdh_aes_decrypt,
    ensure_async,
    errno,
    json_loads,
    json_maybe_decrypt_loads,
    loads,
    make_upload_payload,
    normalize_pickcode,
    quote,
    rsa_encrypt,
    run_gen_step,
    sha1,
    throw,
    time,
    to_id,
    unquote,
    upload_file,
    urlsplit,
    uuid4,
)


class _P115ClientTransferMixin:
    """上传、下载、解压与离线下载接口混入。"""

    @overload
    def clouddownload_request(
        self,
        payload: dict = {},
        /,
        action: str = "",
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_request(
        self,
        payload: dict = {},
        /,
        action: str = "",
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_request(
        self,
        payload: dict = {},
        /,
        action: str = "",
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        match type:
            case "web":
                call: Callable = self._clouddownload_web_request
            case "ssp":
                call = self._clouddownload_lixianssp_request
            case _:
                call = self._clouddownload_request
        return call(
            payload,
            action,
            method=method,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def clouddownload_downpath(
        self,
        payload: dict | int = 10,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_downpath(
        self,
        payload: dict | int = 10,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_downpath(
        self,
        payload: dict | int = 10,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取当前默认的云下载到的目录信息（可能有多个）

        GET https://webapi.115.com/offine/downpath

        :payload:
            - limit: int = 1150
        """
        api = complete_url("/offine/downpath", base_url=base_url)
        if isinstance(payload, int):
            payload = {"limit": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def clouddownload_downpath_set(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_downpath_set(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_downpath_set(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置默认选择的云下载到的目录信息

        POST https://webapi.115.com/offine/downpath

        :payload:
            - file_id: int | str 💡 目录 id
        """
        api = complete_url("/offine/downpath", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def clouddownload_get_id(
        self,
        payload: dict | int = 1,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_get_id(
        self,
        payload: dict | int = 1,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_get_id(
        self,
        payload: dict | int = 1,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取和云下载有关的目录 id

        GET https://clouddownload.115.com/?ac=get_id

        .. note::
            调用此接口后，如果相关目录不存在，则会自动创建。
            响应数据里，"cid" 对应的是上传的种子文件的保存目录，"dest_cid" 是云下载的目录

        :payload:
            - torrent: int = 1
        """
        if isinstance(payload, int):
            payload = {"torrent": payload}
        return self.clouddownload_request(
            payload,
            "get_id",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload  # type: ignore
    def clouddownload_quota_info(
        self,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_quota_info(
        self,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_quota_info(
        self,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取当前云下载配额信息（简略）

        GET https://clouddownload.115.com/?ac=get_quota_info
        """
        return self.clouddownload_request(
            ac="get_quota_info",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def clouddownload_quota_package_array(
        self,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_quota_package_array(
        self,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_quota_package_array(
        self,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取当前云下载配额信息（详细）

        GET https://clouddownload.115.com/?ac=get_quota_package_array
        """
        return self.clouddownload_request(
            ac="get_quota_package_array",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def clouddownload_quota_package_info(
        self,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_quota_package_info(
        self,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_quota_package_info(
        self,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取当前云下载配额信息（详细）

        GET https://clouddownload.115.com/?ac=get_quota_package_info
        """
        return self.clouddownload_request(
            ac="get_quota_package_info",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def clouddownload_sign(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_sign(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_sign(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 sign 和 time 字段（各个添加任务的接口需要），以及其它信息

        GET https://115.com/?ct=clouddownload&ac=space
        """
        api = complete_url(
            base_url=base_url, query={"ct": "clouddownload", "ac": "space"}
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def clouddownload_sign_app(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_sign_app(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_sign_app(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 sign 和 time 字段（各个添加任务的接口需要）

        GET https://proapi.115.com/{app}/files/offlinesign
        """
        api = complete_url("/files/offlinesign", base_url=base_url, app=app)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def clouddownload_task(
        self,
        payload: str | dict,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_task(
        self,
        payload: str | dict,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_task(
        self,
        payload: str | dict,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取云下载任务信息

        GET https://clouddownload.115.com/?ac=get_user_task

        :payload:
            - info_hash: str
        """
        if isinstance(payload, str):
            payload = {"info_hash": payload}
        return self.clouddownload_request(
            payload,
            "get_user_task",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload  # type: ignore
    def clouddownload_task_add_bt(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "ssp",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_task_add_bt(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "ssp",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_task_add_bt(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "ssp",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """添加一个种子作为云下载任务

        POST https://clouddownload.115.com/lixianssp/?ac=add_task_bt

        .. note::
            `client.clouddownload_task_add_bt(info_hash)` 相当于 `client.clouddownload_task_add_url(f"magnet:?xt=urn:btih:{info_hash}")`

            但此接口的优势是允许选择要下载的文件

        :payload:
            - info_hash: str 💡 种子文件的 info_hash
            - wanted: str = <default> 💡 选择文件进行下载（是数字索引，从 0 开始计数，用 "," 分隔）
            - savepath: str = <default> 💡 保存到 `wp_path_id` 对应目录下的相对路径
            - wp_path_id: int | str = <default> 💡 保存到目录的 id
        """
        if isinstance(payload, str):
            payload = {"info_hash": payload}
        return self.clouddownload_request(
            payload,
            "add_task_bt",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def clouddownload_task_add_url(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "ssp",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_task_add_url(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "ssp",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_task_add_url(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "ssp",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """添加一个云下载任务

        POST https://clouddownload.115.com/lixianssp/?ac=add_task_url

        :payload:
            - url: str 💡 链接，支持HTTP、HTTPS、FTP、磁力链和电驴链接
            - savepath: str = <default> 💡 保存到目录下的相对路径
            - wp_path_id: int | str = <default> 💡 保存到目录的 id
        """
        if isinstance(payload, str):
            payload = {"url": payload}
        return self.clouddownload_request(
            payload,
            "add_task_url",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload  # type: ignore
    def clouddownload_task_add_urls(
        self,
        payload: str | Iterable[str] | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "ssp",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_task_add_urls(
        self,
        payload: str | Iterable[str] | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "ssp",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_task_add_urls(
        self,
        payload: str | Iterable[str] | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "ssp",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """添加一组云下载任务

        POST https://clouddownload.115.com/lixianssp/?ac=add_task_urls

        :payload:
            - url: str    💡 链接，支持HTTP、HTTPS、FTP、磁力链和电驴链接
            - url[0]: str 💡 链接，支持HTTP、HTTPS、FTP、磁力链和电驴链接
            - url[1]: str
            - ...
            - savepath: str = <default> 💡 保存到目录下的相对路径
            - wp_path_id: int | str = <default> 💡 保存到目录的 id
        """
        if isinstance(payload, str):
            payload = payload.strip("\n").split("\n")
        if not isinstance(payload, dict):
            payload = {f"url[{i}]": url for i, url in enumerate(payload) if url}
            if not payload:
                raise ValueError("no `url` specified")
        return self.clouddownload_request(
            payload,
            "add_task_urls",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload  # type: ignore
    def clouddownload_task_clear(
        self,
        payload: int | dict = 0,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_task_clear(
        self,
        payload: int | dict = 0,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_task_clear(
        self,
        payload: int | dict = 0,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """清空云下载任务列表

        POST https://clouddownload.115.com/?ac=task_clear

        :payload:
            - flag: int = 0 💡 标识，用于对应某种情况

                - 0: 已完成
                - 1: 全部
                - 2: 已失败
                - 3: 进行中
                - 4: 已完成+删除源文件
                - 5: 全部+删除源文件
        """
        if isinstance(payload, int):
            payload = {"flag": payload}
        return self.clouddownload_request(
            payload,
            "task_clear",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def clouddownload_task_cnt(
        self,
        payload: dict | int = 0,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_task_cnt(
        self,
        payload: dict | int = 0,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_task_cnt(
        self,
        payload: dict | int = 0,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取当前正在运行的云下载任务数

        GET https://clouddownload.115.com/?ac=get_task_cnt

        :payload:
            - flag: int = 0
        """
        if isinstance(payload, int):
            payload = {"flag": payload}
        return self.clouddownload_request(
            payload,
            "get_task_cnt",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def clouddownload_task_count(
        self,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_task_count(
        self,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_task_count(
        self,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取当前各种类型任务的计数

        GET https://clouddownload.115.com/?ac=task_count
        """
        return self.clouddownload_request(
            action="task_count",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload  # type: ignore
    def clouddownload_task_del(
        self,
        payload: str | Iterable[str] | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_task_del(
        self,
        payload: str | Iterable[str] | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_task_del(
        self,
        payload: str | Iterable[str] | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除一组云下载任务（无论是否已经完成）

        POST https://clouddownload.115.com/?ac=task_del

        :payload:
            - hash[0]: str
            - hash[1]: str
            - ...
            - flag: 0 | 1 = <default> 💡 是否删除源文件
        """
        if isinstance(payload, str):
            payload = {"hash[0]": payload}
        elif not isinstance(payload, dict):
            payload = {f"hash[{i}]": hash for i, hash in enumerate(payload)}
            if not payload:
                raise ValueError("no `hash` (info_hash) specified")
        return self.clouddownload_request(
            payload,
            "task_del",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload  # type: ignore
    def clouddownload_task_list(
        self,
        payload: int | dict = 1,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_task_list(
        self,
        payload: int | dict = 1,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_task_list(
        self,
        payload: int | dict = 1,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取当前的云下载任务列表

        GET https://clouddownload.115.com/?ac=task_lists

        :payload:
            - page: int = 1
            - page_size: int = 30
            - stat: int = <default> 💡 已知：9:已失败 11:已完成 12:进行中
        """
        if isinstance(payload, int):
            payload = {"page": payload}
        payload.setdefault("page_size", 30)
        return self.clouddownload_request(
            payload,
            "task_lists",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def clouddownload_task_pause(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_task_pause(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_task_pause(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """暂停云下载任务

        POST https://clouddownload.115.com/?ac=pause_task

        :payload:
            - info_hash: str 💡 待重试任务的 info_hash
        """
        if isinstance(payload, str):
            payload = {"info_hash": payload}
        return self.clouddownload_request(
            payload,
            "pause_task",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def clouddownload_task_restart(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_task_restart(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_task_restart(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """重试云下载任务

        POST https://clouddownload.115.com/?ac=restart

        .. tip::
            经常会遇到批量添加的磁力链接，因为空间不足而失败，此接口可以用于重试

            .. code:: python

                from fundrives.pan115 import P115Client
                from fundrives.pan115.tool import *
                client = P115Client.from_path()

                while True:
                    resp = client.clouddownload_task_list({"stat": 9})
                    tasks = [task for task in resp["tasks"] if task["status"] == 2]
                    if not tasks:
                        break
                    for task in tasks:
                        print(client.clouddownload_task_restart(task["info_hash"]))

        :payload:
            - info_hash: str 💡 待重试任务的 info_hash
        """
        if isinstance(payload, str):
            payload = {"info_hash": payload}
        return self.clouddownload_request(
            payload,
            "restart",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def clouddownload_task_resume(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_task_resume(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_task_resume(
        self,
        payload: str | dict,
        /,
        method: str = "POST",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """恢复（被暂停的）云下载任务

        POST https://clouddownload.115.com/?ac=resume_task

        :payload:
            - info_hash: str 💡 待重试任务的 info_hash
        """
        if isinstance(payload, str):
            payload = {"info_hash": payload}
        return self.clouddownload_request(
            payload,
            "resume_task",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload  # type: ignore
    def clouddownload_torrent(
        self,
        payload: str | dict,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def clouddownload_torrent(
        self,
        payload: str | dict,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def clouddownload_torrent(
        self,
        payload: str | dict,
        /,
        method: str = "GET",
        type: Literal["", "web", "ssp"] = "web",
        base_url: str | Callable[[], str] = "https://clouddownload.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """查看种子的文件列表等信息

        GET https://clouddownload.115.com/?ac=torrent

        :payload:
            - sha1: str
        """
        if isinstance(payload, str):
            payload = {"sha1": payload}
        return self.clouddownload_request(
            payload,
            "torrent",
            method=method,
            type=type,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def download_files_app(
        self,
        payload: str | dict,
        /,
        app: str = "chrome",
        version: str = "2.0",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def download_files_app(
        self,
        payload: str | dict,
        /,
        app: str = "chrome",
        version: str = "2.0",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def download_files_app(
        self,
        payload: str | dict,
        /,
        app: str = "chrome",
        version: str = "2.0",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取待下载的文件列表

        GET https://proapi.115.com/app/chrome/downfiles

        .. caution::
            不允许直接从根目录获取，因为根目录没有 ``pickcode``

        .. tip::
            如果 ``app`` 不是 "chrome"，那么会多一个字段 "sha1"，虽依然没有文件名，但有 "fs"（文件大小），搭配 "sha1" 可以用于检测文件重复

        :payload:
            - pickcode: str 💡 提取码
            - page: int = 1 💡 第几页
            - per_page: int = 5000 💡 每页大小，目前最大为 5000
        """
        if app in ("", "web", "desktop", "chrome"):
            api = complete_url(f"/app/{version}/chrome/downfiles", base_url)
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
            api = complete_url("/ufile/downfiles", base_url, app=app, version=version)
            request_kwargs.setdefault("ecdh_encrypt", True)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        payload = {"page": 1, "per_page": 5000, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def download_folders_app(
        self,
        payload: str | dict,
        /,
        app: str = "chrome",
        version: str = "2.0",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def download_folders_app(
        self,
        payload: str | dict,
        /,
        app: str = "chrome",
        version: str = "2.0",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def download_folders_app(
        self,
        payload: str | dict,
        /,
        app: str = "chrome",
        version: str = "2.0",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取待下载的目录列表

        GET https://proapi.115.com/app/chrome/downfolders

        .. caution::
            不允许直接从根目录获取，因为根目录没有 ``pickcode``

        :payload:
            - pickcode: str 💡 提取码
            - page: int = 1 💡 第几页
            - per_page: int = 5000 💡 每页大小，目前最大为 5000
        """
        if app in ("", "web", "desktop", "chrome"):
            api = complete_url(f"/app/{version}/chrome/downfolders", base_url)
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
            api = complete_url("/ufile/downfolders", base_url, app=app, version=version)
            request_kwargs.setdefault("ecdh_encrypt", True)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        payload = {"page": 1, "per_page": 5000, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def download_downfolder_app(
        self,
        payload: str | dict,
        /,
        app: str = "chrome",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def download_downfolder_app(
        self,
        payload: str | dict,
        /,
        app: str = "chrome",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def download_downfolder_app(
        self,
        payload: str | dict,
        /,
        app: str = "chrome",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取待下载的文件列表

        GET https://proapi.115.com/{app}/folder/downfolder

        .. caution::
            一次性拉完，当文件过多时，会报错

        :payload:
            - pickcode: str 💡 提取码
            - share_id: int | str 💡 共享 id
        """
        if app in ("", "web", "desktop", "chrome"):
            api = complete_url("/app/chrome/downfolder", base_url)
        else:
            api = complete_url("/folder/downfolder", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def download_url(
        self,
        pickcode: int | str,
        /,
        strict: bool = True,
        user_agent: None | str = None,
        app: str = "os_windows",
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
        app: str = "os_windows",
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
        app: str = "os_windows",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> P115URL | Coroutine[Any, Any, P115URL]:
        """获取文件的下载链接

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
        :param strict: 如果为 True，当目标是目录时，会抛出 IsADirectoryError 异常
        :param user_agent: 如果不为 None，则作为请求头 "user-agent" 的值
        :param app: 使用此设备的接口
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 下载链接
        """
        if app == "open":
            return self.download_url_open(
                pickcode,
                strict=strict,
                user_agent=user_agent,
                async_=async_,
                **request_kwargs,
            )
        pickcode = self.to_pickcode(pickcode)

        def gen_step():
            if app in ("web2", "video"):
                resp = yield self.download_url_web2(
                    pickcode,
                    user_agent=user_agent,
                    async_=async_,
                    **request_kwargs,
                )
                resp["pickcode"] = pickcode
                resp["is_download"] = True
                check_response(resp)
                url = resp["url"]
                return P115URL(
                    url,
                    id=self.to_id(pickcode),
                    pickcode=pickcode,
                    name=unquote(urlsplit(url).path.rsplit("/", 1)[-1]),
                    is_dir=False,
                    headers=resp["headers"],
                )
            elif app in ("web", "desktop"):
                resp = yield self.download_url_web(
                    pickcode,
                    user_agent=user_agent,
                    async_=async_,
                    **request_kwargs,
                )
                resp["pickcode"] = pickcode
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
                    pickcode,
                    user_agent=user_agent,
                    app=app,
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
    def download_urls(
        self,
        pickcodes: int | str | Iterable[int | str],
        /,
        strict: bool = True,
        user_agent: None | str = None,
        app: str = "os_windows",
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
        app: str = "os_windows",
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
        app: str = "os_windows",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict[int, P115URL] | Coroutine[Any, Any, dict[int, P115URL]]:
        """批量获取文件的下载链接

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
        :param app: 使用此设备的接口，要么是 "open"，要么是 "chrome"（或者其他任何值）
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 一批下载链接
        """
        if app == "open":
            return self.download_urls_open(
                pickcodes,
                strict=strict,
                user_agent=user_agent,
                async_=async_,
                **request_kwargs,
            )
        if isinstance(pickcodes, (int, str)):
            pickcodes = self.to_pickcode(pickcodes)
        else:
            pickcodes = ",".join(map(self.to_pickcode, pickcodes))

        def gen_step():
            resp = yield self.download_url_app(
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
    def download_url_app(
        self,
        payload: str | dict,
        /,
        user_agent: None | str = None,
        app: str = "chrome",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def download_url_app(
        self,
        payload: str | dict,
        /,
        user_agent: None | str = None,
        app: str = "chrome",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def download_url_app(
        self,
        payload: str | dict,
        /,
        user_agent: None | str = None,
        app: str = "chrome",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件的下载链接

        POST https://proapi.115.com/app/chrome/downurl

        .. note::
            `app` 为 "chrome" 时，支持一次获取多个提取码对应的下载链接，但是每多一个提取码，大概多耗时 50 ms，猜测服务端也是逐个从某个服务获取下载链接的。

            如果 `app` 为 "chrome"，则仅支持 `aid=1` 的提取码获取下载链接（以前是不限制 aid 的，这样甚至可以获取已经删除的文件的下载链接）；否则，还支持 `aid=12` 的下载链接。

        .. attention::
            尽量不要尝试对已经删除的文件获取下载链接，不仅会失败，还容易触发风控

        :payload:
            - pickcode: str  💡 如果 `app` 为 "chrome"，则可以接受多个，多个用逗号 "," 隔开
            - pick_code: str 💡 如果不用 ``pickcode``，那就用 ``pick_code``
            - share_id: int | str = <default> 💡 共享 id
            - user_id: int = <default>
        """
        if app in ("", "chrome"):
            api = complete_url("/app/chrome/downurl", base_url)
            if isinstance(payload, str):
                payload = {"pickcode": payload}
            elif "pickcode" not in payload:
                payload["pickcode"] = payload["pick_code"]
        elif app in ("os_windows", "os_mac", "os_linux", "windows", "mac", "linux"):
            if not app.startswith("os_"):
                app = "os_" + app
            api = complete_url("/2.0/ufile/downurl", base_url=base_url, app=app)
            if isinstance(payload, str):
                payload = {"pickcode": payload}
            elif "pickcode" not in payload:
                payload["pickcode"] = payload["pick_code"]
            # NOTE: 提取码不可是 "f" 开头，但允许由任何特征值构造（由 0-9 和 a-z 这 36 个字符，构成的 4 位字符串，例如 "0000"），但限定必须是自己网盘的文件（不能获取别人的文件）
            payload["pickcode"] = ",".join(
                map(normalize_pickcode, payload["pickcode"].split(","))
            )
            request_kwargs.setdefault("ecdh_encrypt", True)
        else:
            api = complete_url("/2.0/ufile/download", base_url=base_url, app=app)
            if isinstance(payload, str):
                payload = {"pick_code": payload}
            elif "pick_code" not in payload:
                payload["pick_code"] = payload["pickcode"]
        payload.setdefault("user_id", self.user_id)
        headers = request_kwargs["headers"] = dict(request_kwargs.get("headers") or ())
        if user_agent is None:
            headers.setdefault("user-agent", "")
        else:
            headers["user-agent"] = user_agent

        def parse(_, content: bytes, /) -> dict:
            json = json_maybe_decrypt_loads(content)
            if json["state"] and (data := json.get("data")):
                json["data"] = json_loads(_rsa_decrypt(data))
            json["headers"] = headers
            return json

        request_kwargs.setdefault("parse", parse)
        request_kwargs["data"] = {"data": rsa_encrypt(dumps(payload)).decode("ascii")}
        return self.request(
            url=api,
            method="POST",
            async_=async_,
            **request_kwargs,
        )

    @overload
    def download_url_web(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def download_url_web(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def download_url_web(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件的下载链接（网页版接口）

        GET https://webapi.115.com/files/download

        .. note::
            最大允许下载 200 MB 的文件，即使文件违规，或者 `aid=12`，也可以正常下载

        :payload:
            - pickcode: str
            - dl: int = 0 💡 如果不为 0，则需要从响应中提取 "file_url_302" 字段，得到一个链接（只能被访问一次，但无需 cookies），然后访问此链接，才能从中获得最终的下载链接
        """
        api = complete_url("/files/download", base_url=base_url)
        if not isinstance(payload, dict):
            payload = {"pickcode": self.to_pickcode(payload)}
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
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def download_url_web2(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def download_url_web2(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def download_url_web2(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件的下载链接（网页版接口）

        GET https://115.com/?ct=download&ac=video

        .. note::
            最大允许下载 200 MB 的文件，即使文件已被删除，也可以正常下载

        :payload:
            - pickcode: str
        """
        api = complete_url(base_url=base_url, query={"ct": "download", "ac": "video"})
        if not isinstance(payload, dict):
            payload = {"pickcode": self.to_pickcode(payload)}
        headers = request_kwargs["headers"] = dict(request_kwargs.get("headers") or ())
        if user_agent is None:
            headers.setdefault("user-agent", "")
        else:
            headers["user-agent"] = user_agent

        def parse(resp, _: bytes, /) -> dict:
            if resp.status != 302:
                return {
                    "state": False,
                    "errno": 31003,
                    "message": "文件不存在、已删除、超过200MB或者是目录",
                    "response": {"status": resp.status, "headers": dict(resp.headers)},
                }
            json = {"state": True, "url": resp.headers["location"]}
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
        request_kwargs.setdefault("follow_redirects", False)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def extract_add_file(
        self,
        payload: list | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def extract_add_file(
        self,
        payload: list | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_add_file(
        self,
        payload: list | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """解压缩到某个目录，推荐直接用封装函数 `extract_file`

        POST https://webapi.115.com/files/add_extract_file

        .. caution::
            【解压到】任务不可并发、不可中止，空目录不会被导出，不会产生 life 操作事件。
            目录层级最多 25 级（不算文件节点），对于超出此限制的路径，会直接把最终的文件保存到第 25 级之下，如果因此造成同名，会在扩展名前加 (1)，数字逐次增加，以此类推。
            但如果文件名是类似 ".name" 的格式，会被视为 ".name.name" 处理，也就是名字翻倍，然后处理成 ".name(1).name"、".name(2).name"、... 这样累计下去，此时整个名字最多 510 字节（按 utf-8 编码算，即 255 * 2），此时扩展名不会变，只会截断当它充当文件名时尾部的一部分。
            名字里面如果有 <>" 这 3 个字符，则会被替换为下划线 _。
            文件名最多 75 个字符（不包括扩展名部分），超出部分会被截断。扩展名部分，不算前缀点号 . 时，最多 254 个字节（按 utf-8 编码算），但如果所有字符都相同的中文字，却最多只有 75 个（为什么呢？）。

        :payload:
            - pick_code: str
            - extract_file: str = ""
            - extract_dir: str = ""
            - extract_file[]: str
            - extract_file[]: str
            - ...
            - to_pid: int | str = 0
            - paths: str = "文件"
        """
        api = complete_url("/files/add_extract_file", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def extract_add_file_app(
        self,
        payload: list | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def extract_add_file_app(
        self,
        payload: list | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_add_file_app(
        self,
        payload: list | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """解压缩到某个目录，推荐直接用封装函数 `extract_file`

        POST https://proapi.115.com/{app}/2.0/ufile/add_extract_file

        .. caution::
            【解压到】任务不可并发、不可中止，空目录不会被导出，不会产生 life 操作事件。
            目录层级最多 25 级（不算文件节点），对于超出此限制的路径，会直接把最终的文件保存到第 25 级之下，如果因此造成同名，会在扩展名前加 (1)，数字逐次增加，以此类推。
            但如果文件名是类似 ".name" 的格式，会被视为 ".name.name" 处理，也就是名字翻倍，然后处理成 ".name(1).name"、".name(2).name"、... 这样累计下去，此时整个名字最多 510 字节（按 utf-8 编码算，即 255 * 2），此时扩展名不会变，只会截断当它充当文件名时尾部的一部分。
            名字里面如果有 <>" 这 3 个字符，则会被替换为下划线 _。
            文件名最多 75 个字符（不包括扩展名部分），超出部分会被截断。扩展名部分，不算前缀点号 . 时，最多 254 个字节（按 utf-8 编码算），但如果所有字符都相同的中文字，却最多只有 75 个（为什么呢？）。

        :payload:
            - pick_code: str
            - extract_file: str = ""
            - extract_dir: str = ""
            - extract_file[]: str
            - extract_file[]: str
            - ...
            - to_pid: int | str = 0
            - paths: str = "文件"
        """
        api = complete_url("/2.0/ufile/add_extract_file", base_url=base_url, app=app)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def extract_download_url(
        self,
        /,
        pickcode: str,
        path: str,
        user_agent: None | str = None,
        app: str = "android",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> P115URL: ...

    @overload
    def extract_download_url(
        self,
        /,
        pickcode: str,
        path: str,
        user_agent: None | str = None,
        app: str = "android",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, P115URL]: ...

    def extract_download_url(
        self,
        /,
        pickcode: str,
        path: str,
        user_agent: None | str = None,
        app: str = "android",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> P115URL | Coroutine[Any, Any, P115URL]:
        """获取压缩包中文件的下载链接

        :param pickcode: 压缩包的提取码
        :param path: 文件在压缩包中的路径
        :param user_agent: 如果不为 None，则作为请求头 "user-agent" 的值
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 下载链接
        """
        path = path.rstrip("/")

        def gen_step():
            payload = {"pick_code": pickcode, "full_name": path.lstrip("/")}
            if app in ("web", "desktop"):
                resp = yield self.extract_download_url_web(
                    payload,
                    user_agent=user_agent,
                    async_=async_,
                    **request_kwargs,
                )
            else:
                resp = yield self.extract_download_url_app(
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
            url = quote(data["url"], safe=":/?&=%#")
            from posixpath import basename

            return P115URL(
                url,
                name=basename(path),
                path=path,
                headers=resp["headers"],
            )

        return run_gen_step(gen_step, async_)

    @overload
    def extract_download_url_app(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        user_agent: None | str = None,
        app: str = "android",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def extract_download_url_app(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        user_agent: None | str = None,
        app: str = "android",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_download_url_app(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        user_agent: None | str = None,
        app: str = "android",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取压缩包中文件的下载链接

        GET https://proapi.115.com/{app}/2.0/ufile/extract_down_file

        :payload:
            - pick_code: str
            - full_name: str
            - dl: int = <default>
        """
        api = complete_url("/2.0/ufile/extract_down_file", base_url=base_url, app=app)
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
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def extract_download_url_web(
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
    def extract_download_url_web(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_download_url_web(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        user_agent: None | str = None,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取压缩包中文件的下载链接

        GET https://webapi.115.com/files/extract_down_file

        :payload:
            - pick_code: str
            - full_name: str
        """
        api = complete_url("/files/extract_down_file", base_url=base_url)
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
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def extract_file(
        self,
        /,
        pickcode: str,
        files: str | Iterable[str] = "",
        dirs: str | Iterable[str] = "",
        dirname: str = "",
        to_pid: int | str = 0,
        app: str = "web",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def extract_file(
        self,
        /,
        pickcode: str,
        files: str | Iterable[str] = "",
        dirs: str | Iterable[str] = "",
        dirname: str = "",
        to_pid: int | str = 0,
        app: str = "web",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_file(
        self,
        /,
        pickcode: str,
        files: str | Iterable[str] = "",
        dirs: str | Iterable[str] = "",
        dirname: str = "",
        to_pid: int | str = 0,
        app: str = "web",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """解压缩到某个目录，此方法是对 `extract_add_file` 的封装，推荐使用

        .. caution::
            【解压到】任务不可并发、不可中止，空目录不会被导出，不会产生 life 操作事件。
            目录层级最多 25 级（不算文件节点），对于超出此限制的路径，会直接把最终的文件保存到第 25 级之下，如果因此造成同名，会在扩展名前加 (1)，数字逐次增加，以此类推。
            但如果文件名是类似 ".name" 的格式，会被视为 ".name.name" 处理，也就是名字翻倍，然后处理成 ".name(1).name"、".name(2).name"、... 这样累计下去，此时整个名字最多 510 字节（按 utf-8 编码算，即 255 * 2），此时扩展名不会变，只会截断当它充当文件名时尾部的一部分。
            名字里面如果有 <>" 这 3 个字符，则会被替换为下划线 _。
            文件名最多 75 个字符（不包括扩展名部分），超出部分会被截断。扩展名部分，不算前缀点号 . 时，最多 254 个字节（按 utf-8 编码算），但如果所有字符都相同的中文字，却最多只有 75 个（为什么呢？）。

        .. note::
            一次解压任务，似乎最多 1 万个文件，而且会排除空目录。但你完全可以利用这一点，来批量创建一个目录结构。
            虽然分次也能解压极大的压缩包，但相应的云解压的耗时也会同步大量增加，处理起来也更为复杂，我建议每次最好限制在 1 万条叶子节点以下。

            1. 首先创建一个压缩包 zip 文件，把目录结构写进去，且为每个目录创建一个空文件，以避免被视为空目录（为了提高效率，请先把所有非叶子节点过滤掉）

                .. code:: python

                    from io import BytesIO
                    from zipfile import ZipFile

                    f = BytesIO()
                    with ZipFile(f, "w") as z:
                        for dir in dirs:
                            z.writestr(dir + "/.placeholder", "")

            2. 把所创建的 zip 压缩包上传到网盘

                .. code:: python

                    from fundrives.pan115 import check_response, P115Client

                    client = P115Client.from_path()

                    resp = client.upload_file_sample(f.getbuffer(), filename='a.zip')
                    check_response(resp)
                    pickcode = resp["data"]["pick_code"]

            3. 将压缩包云解压

                .. code:: python

                    client.extract_push(pickcode)
                    # 查看进度用：client.extract_push_progress(pickcode)

            4. 等待云解压完成后，把压缩包解压到网盘（耗时较长，且不可并发）

                .. code:: python

                    client.extract_file(pickcode)

            5. 解压完成后，把里面所有的 .placeholder 占位文件找出来删了，这里假设顶层目录 id 是 ``pid``

                .. code:: python

                    from fundrives.pan115.tool import batch_delete, iter_download_files

                    empty_file_hash = "DA39A3EE5E6B4B0D3255BFEF95601890AFD80709"
                    files = (
                        info["pc"]
                        for info in iter_download_nodes(client, pid, app="android", get_raw=True)
                        if info["sha1"] == empty_file_hash
                    )
                    batch_delete(client, files)

        :param pickcode: 压缩文件的提取码
        :param files:    待解压缩的文件路径（相对于 ``dirname``），如果以 "/" 结尾，则视为目录
        :param dirs:     待解压缩的文件路径（相对于 ``dirname``）
        :param dirname:  压缩包内路径，为空则是压缩包的根目录
        :param to_pid:   解压到网盘的目录 id
        :param app:      使用此设备的接口
        :param async_:   是否异步
        :param request_kwargs: 其它请求参数

        :return: 接口响应，会返回一个 "extract_id"，需要你去轮询获取进度
        """
        if app in ("", "web", "desktop", "aps"):
            extract_add_file: Callable = self.extract_add_file
        else:
            extract_add_file = self.extract_add_file_app
            request_kwargs["app"] = app
        dirname = dirname.strip("/")

        def gen_step():
            data = [
                ("pick_code", pickcode),
                ("paths", "文件/" + dirname if dirname else "文件"),
                ("to_pid", to_pid),
            ]
            paths: list[str] = []
            add_path = paths.append
            if files:
                if isinstance(files, str):
                    if files.strip("/"):
                        add_path(files)
                else:
                    for p in files:
                        if p.strip("/"):
                            add_path(p)
            if dirs:
                if isinstance(dirs, str):
                    if dirs.strip("/"):
                        add_path(dirs + "/")
                else:
                    for p in dirs:
                        if p.strip("/"):
                            add_path(p + "/")
            if not paths:
                next_marker = ""
                extract_list = self.extract_list
                while True:
                    resp = yield extract_list(
                        pickcode=pickcode,
                        path=dirname,
                        next_marker=next_marker,
                        async_=async_,
                        **request_kwargs,
                    )
                    check_response(resp)
                    for p in resp["data"]["list"]:
                        if p["file_category"]:
                            add_path(p["file_name"])
                        else:
                            add_path(p["file_name"] + "/")
                    if not (next_marker := resp["data"].get("next_marker")):
                        break
            data.extend(
                (
                    "extract_dir[]" if path.endswith("/") else "extract_file[]",
                    path.strip("/"),
                )
                for path in paths
            )
            return extract_add_file(data, async_=async_, **request_kwargs)

        return run_gen_step(gen_step, async_)

    @overload
    def extract_folders(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def extract_folders(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_folders(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取压缩文件的文件列表（简略信息）

        GET https://webapi.115.com/files/extract_folders

        :payload:
            - pick_code: str 💡 压缩包文件的提取码
            - full_dir_name: str 💡 多个用逗号 "," 隔开
            - full_file_name: str = <default> 💡 多个用逗号 "," 隔开
        """
        api = complete_url("/files/extract_folders", base_url=base_url)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def extract_folders_app(
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
    def extract_folders_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_folders_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取压缩文件的文件列表（简略信息）

        GET https://proapi.115.com/{app}/2.0/ufile/extract_folders

        :payload:
            - pick_code: str 💡 压缩包文件的提取码
            - full_dir_name: str 💡 多个用逗号 "," 隔开
            - full_file_name: str = <default> 💡 多个用逗号 "," 隔开
        """
        api = complete_url("/2.0/ufile/extract_folders", base_url=base_url, app=app)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def extract_folders_post(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def extract_folders_post(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_folders_post(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取压缩文件的文件列表是否可批量下载（最高支持1万的文件操作数量）

        POST https://webapi.115.com/files/extract_folders

        :payload:
            - pick_code: str 💡 压缩包文件的提取码
            - full_dir_name: str 💡 多个用逗号 "," 隔开
            - full_file_name: str = <default> 💡 多个用逗号 "," 隔开
        """
        api = complete_url("/files/extract_folders", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def extract_folders_post_app(
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
    def extract_folders_post_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_folders_post_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取压缩文件的文件列表是否可批量下载（最高支持1万的文件操作数量）

        POST https://proapi.115.com/{app}/2.0/ufile/extract_folders

        :payload:
            - pick_code: str 💡 压缩包文件的提取码
            - full_dir_name: str 💡 多个用逗号 "," 隔开
            - full_file_name: str = <default> 💡 多个用逗号 "," 隔开
        """
        api = complete_url("/2.0/ufile/extract_folders", base_url=base_url, app=app)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def extract_info(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def extract_info(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_info(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取压缩文件的文件列表，推荐直接用封装函数 `extract_list`

        GET https://webapi.115.com/files/extract_info

        :payload:
            - pick_code: str
            - file_name: str = "" 💡 在压缩包中的相对路径
            - next_marker: str = ""
            - page_count: int | str = 999 💡 分页大小，介于 1-999
            - paths: str = "文件" 💡 省略即可
        """
        api = complete_url("/files/extract_info", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        payload = {
            "paths": "文件",
            "page_count": 999,
            "next_marker": "",
            "file_name": "",
            **payload,
        }
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def extract_info_app(
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
    def extract_info_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_info_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取压缩文件的文件列表，推荐直接用封装函数 `extract_list_app`

        GET https://proapi.115.com/{app}/2.0/ufile/extract_info

        :payload:
            - pick_code: str
            - file_name: str = "" 💡 在压缩包中的相对路径
            - next_marker: str = ""
            - page_count: int | str = 999 💡 分页大小，介于 1-999
            - paths: str = "文件" 💡 省略即可
        """
        api = complete_url("/2.0/ufile/extract_info", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        payload = {
            "paths": "文件",
            "page_count": 999,
            "next_marker": "",
            "file_name": "",
            **payload,
        }
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def extract_list(
        self,
        /,
        pickcode: str,
        path: str = "",
        next_marker: str = "",
        page_count: int = 999,
        app: str = "web",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def extract_list(
        self,
        /,
        pickcode: str,
        path: str = "",
        next_marker: str = "",
        page_count: int = 999,
        app: str = "web",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_list(
        self,
        /,
        pickcode: str,
        path: str = "",
        next_marker: str = "",
        page_count: int = 999,
        app: str = "web",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取压缩文件的文件列表，此方法是对 `extract_info` 的封装，推荐使用

        :param pickcode: 压缩文件的提取码
        :param path: 压缩包内（目录）路径，为空则是压缩包的根目录
        :param next_marker: 翻页标记，用来获取下一页
        :param page_count: 这一页有多少条数据，范围在 ``[1, 999]``
        :param app: 使用此设备的接口
        :param async_: 是否异步
        :param request_kwargs: 其它请求参数

        :return: 接口响应
        """
        if not 1 <= page_count <= 999:
            page_count = 999
        payload = {
            "pick_code": pickcode,
            "file_name": path.strip("/"),
            "paths": "文件",
            "next_marker": next_marker,
            "page_count": page_count,
        }
        if app in ("", "web", "desktop", "aps"):
            extract_info: Callable = self.extract_info
        else:
            extract_info = self.extract_info_app
        return extract_info(
            payload,
            app=app,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def extract_progress(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def extract_progress(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_progress(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 解压缩到目录 任务的进度

        GET https://webapi.115.com/files/add_extract_file

        :payload:
            - extract_id: str
        """
        api = complete_url("/files/add_extract_file", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"extract_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def extract_progress_app(
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
    def extract_progress_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_progress_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 解压缩到目录 任务的进度

        GET https://proapi.115.com/{app}/2.0/ufile/add_extract_file

        :payload:
            - extract_id: str
        """
        api = complete_url("/2.0/ufile/add_extract_file", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"extract_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def extract_push(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def extract_push(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_push(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """推送一个解压缩任务给服务器，完成后，就可以查看压缩包的文件列表了

        .. warning::
            只能云解压 20GB 以内文件，不支持云解压分卷压缩包，只支持 .zip、.rar 和 .7z 等

        POST https://webapi.115.com/files/push_extract

        :payload:
            - pick_code: str
            - secret: str = "" 💡 解压密码
        """
        api = complete_url("/files/push_extract", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def extract_push_app(
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
    def extract_push_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_push_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """推送一个解压缩任务给服务器，完成后，就可以查看压缩包的文件列表了

        .. warning::
            只能云解压 20GB 以内文件，不支持云解压分卷压缩包，只支持 .zip、.rar 和 .7z 等

        POST https://proapi.115.com/{app}/2.0/ufile/push_extract

        :payload:
            - pick_code: str
            - secret: str = "" 💡 解压密码
        """
        api = complete_url("/2.0/ufile/push_extract", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def extract_push_progress(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def extract_push_progress(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_push_progress(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """查询解压缩任务的进度

        GET https://webapi.115.com/files/push_extract

        :payload:
            - pick_code: str
        """
        api = complete_url("/files/push_extract", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def extract_push_progress_app(
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
    def extract_push_progress_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def extract_push_progress_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """查询解压缩任务的进度

        GET https://proapi.115.com/{app}/2.0/ufile/push_extract

        :payload:
            - pick_code: str
        """
        api = complete_url("/2.0/ufile/push_extract", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def upload_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取和上传有关的信息，其中 "user_id" 和 "userkey" 是至关重要的

        GET https://webapi.115.com/files/uploadinfo
        """
        api = complete_url("/files/uploadinfo", base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def upload_info_app(
        self,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_info_app(
        self,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_info_app(
        self,
        /,
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取和上传有关的信息，其中 "user_id" 和 "userkey" 是至关重要的

        GET https://proapi.115.com/app/uploadinfo
        """
        api = complete_url("/app/uploadinfo", base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def upload_init(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_init(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_init(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """初始化上传任务，可能秒传

        POST https://uplb.115.com/4.0/initupload.php

        .. caution::
            这个接口，偶尔会返回 HTTP 401 错误，你只需要再次重试即可

        :payload:
            - fileid: str           💡 文件的 sha1
            - filename: str         💡 文件名
            - filesize: int         💡 文件大小
            - target: str = "U_1_0" 💡 保存目标，格式为 f"U_{aid}_{pid}" 或 f"S_{share_id}_{pid}"
            - sign_key: str = ""    💡 2 次验证的 key
            - sign_val: str = ""    💡 2 次验证的值
            - topupload: int | str = "true" 💡 上传调度文件类型调度标记
            - userid: int | str = <default> 💡 用户 id
            - userkey: str = <default> 💡 用户的 key
        """
        api = complete_url("/4.0/initupload.php", base_url=base_url)
        payload = {
            "appid": 0,
            "target": "U_1_0",
            "sign_key": "",
            "sign_val": "",
            "topupload": "true",
            "appversion": _app_version,
            **payload,
        }
        appversion = payload["appversion"]
        if "userid" not in payload:
            payload["userid"] = self.user_id
        if "userkey" not in payload:
            payload["userkey"] = self.user_key
        request_kwargs["headers"] = dict_update(
            dict(request_kwargs.get("headers") or ()),
            {
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": f"Mozilla/5.0 115disk/{appversion} 115Browser/{appversion} 115wangpan_android/{appversion}",
            },
        )
        request_kwargs.update(make_upload_payload(payload))

        def parse_upload_init_response(_, content: bytes, /) -> dict:
            data = ecdh_aes_decrypt(content)
            return json_loads(data)

        request_kwargs.setdefault("parse", parse_upload_init_response)
        return self.request(url=api, method="POST", async_=async_, **request_kwargs)

    @overload
    def upload_key(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_key(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_key(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 user_key

        GET https://proapi.115.com/{app}/2.0/user/upload_key
        """
        api = complete_url("/2.0/user/upload_key", base_url=base_url, app=app)

        def gen_step():
            resp = yield self.request(url=api, async_=async_, **request_kwargs)
            if resp["state"]:
                self.user_key = resp["data"]["userkey"]
            return resp

        return run_gen_step(gen_step, async_)

    @overload
    def upload_resume(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_resume(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_resume(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取恢复断点续传所需信息

        POST https://uplb.115.com/3.0/resumeupload.php

        :payload:
            - fileid: str   💡 文件的 sha1 值
            - filesize: int 💡 文件大小，单位是字节
            - target: str   💡 上传目标，默认为 "U_1_0"，格式为 f"U_{aid}_{pid}" 或 f"S_{share_id}_{pid}"
            - pickcode: str 💡 提取码
            - userid: int = <default> 💡 用户 id
        """
        api = complete_url("/3.0/resumeupload.php", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        else:
            payload = dict(payload)
            if "pickcode" not in payload:
                if "pick_code" in payload:
                    payload["pickcode"] = payload["pick_code"]
            callback_var: None | dict = None
            if "callback_var" in payload:
                callback_var = loads(payload["callback_var"])
            elif "callback" in payload:
                callback_var = loads(payload["callback"]["callback_var"])
            if callback_var:
                payload.update(
                    pickcode=callback_var["x:pick_code"],
                    target=callback_var["x:target"],
                    userid=callback_var["x:user_id"],
                )
        payload.setdefault("fileid", "0" * 40)
        payload.setdefault("filesize", 1)
        payload.setdefault("target", "U_1_0")
        if "userid" not in payload:
            payload["userid"] = self.user_id
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def upload_avatar(
        self,
        /,
        file: (Buffer | str | PathLike | SupportsRead | Iterable[Buffer]),
        app: str = "web",
        base_url: str | Callable[[], str] = "https://ictxl.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_avatar(
        self,
        /,
        file: (
            Buffer
            | str
            | PathLike
            | SupportsRead
            | Iterable[Buffer]
            | AsyncIterable[Buffer]
        ),
        app: str = "web",
        base_url: str | Callable[[], str] = "https://ictxl.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_avatar(
        self,
        /,
        file: (
            Buffer
            | str
            | PathLike
            | SupportsRead
            | Iterable[Buffer]
            | AsyncIterable[Buffer]
        ),
        app: str = "web",
        base_url: str | Callable[[], str] = "https://ictxl.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """上传一张图片，可用于作为头像（图片时效性很短，请尽快使用）

        POST https://ictxl.115.com/app/1.1/{app}/1.2/upload/set_avatar

        .. attention::
            此接口采用 multi-part 上传，其实是可以一次传多个文件的，但我做的封装只允许传一张图片。

            一次接口调用的上传流量，算上分片分隔符，大概是不能超过 32 MB，需要进一步测验。

        :param file: 待上传的文件
        :param app: 使用此设备的接口
        :param base_url: 接口的基地址
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 接口响应
        """
        api = complete_url(f"/app/1.1/{app}/1.2/upload/set_avatar", base_url=base_url)
        if isinstance(file, (str, PathLike)):
            file = open(file, "rb")
        return self.request(
            url=api,
            method="POST",
            files={"file": ("a.jpg", file)},
            async_=async_,
            **request_kwargs,
        )

    @overload
    def upload_avatar2(
        self,
        /,
        file: Buffer | str | PathLike,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://job.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_avatar2(
        self,
        /,
        file: Buffer | str | PathLike,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://job.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_avatar2(
        self,
        /,
        file: Buffer | str | PathLike,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://job.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """上传一张图片，可用于作为头像

        POST https://job.115.com/api/1.0/{app}/26.0/5/upload/avatar

        :param file: 待上传的文件数据
        :param app: 使用此设备的接口
        :param base_url: 接口的基地址
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 接口响应
        """
        api = complete_url(f"/api/1.0/{app}/1.0/upload/avatar", base_url=base_url)
        if isinstance(file, (str, PathLike)):
            data: Buffer = open(file, "rb").read()
        else:
            data = file
        headers = dict(request_kwargs.pop("headers", None) or ())
        headers["content-type"] = "application/x-www-form-urlencoded"
        return self.request(
            url=api,
            method="POST",
            data=b"img=" + b64encode(data),
            headers=headers,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def upload_chat_image_init(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_chat_image_init(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_chat_image_init(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """聊天窗口中上传图片接口的初始化

        POST https://115.com/api/chat/image/upload

        .. caution::
            此接口不支持秒传，最大支持上传 50 MB 的文件，上传成功后不占用空间

        .. caution::
            通过扩展名来识别，仅支持以下格式图片(jpg,jpeg,png,gif,svg,webp,heic,bmp,dng)

        .. note::
            ``target`` 随便设置，例如 ``"U_3_-1"``、``"U_4_-1"``、``"U_5_-2"``、``"U_3_-10"`` 等

        :payload:
            - filename: str = <default> 💡 文件名，默认为一个新的 uuid4 对象的字符串表示
            - target: str = ``"U_3_-1"`` 💡 上传目标，格式为 ``f"U_{aid}_{pid}"``
            - filesize: int | str = <default> 💡 图片大小
            - height: int = <default> 💡 图片高度
            - width: int = <default>  💡 图片宽度
        """
        api = complete_url("/api/chat/image/upload", base_url=base_url)
        if isinstance(payload, str):
            payload = {"filename": payload}
        elif "filename" not in payload:
            payload["filename"] = str(uuid4()) + ".jpg"
        payload = {
            "filesize": 1,
            "width": 1,
            "height": 1,
            "target": "U_3_-1",
            "userid": 11500,
            **payload,
        }
        return self.request(
            url=api, method="POST", json=payload, async_=async_, **request_kwargs
        )

    @overload
    def upload_image(
        self,
        /,
        file: (Buffer | str | PathLike | SupportsRead | Iterable[Buffer]),
        app: str = "web",
        base_url: str | Callable[[], str] = "https://credentials.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_image(
        self,
        /,
        file: (
            Buffer
            | str
            | PathLike
            | SupportsRead
            | Iterable[Buffer]
            | AsyncIterable[Buffer]
        ),
        app: str = "web",
        base_url: str | Callable[[], str] = "https://credentials.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_image(
        self,
        /,
        file: (
            Buffer
            | str
            | PathLike
            | SupportsRead
            | Iterable[Buffer]
            | AsyncIterable[Buffer]
        ),
        app: str = "web",
        base_url: str | Callable[[], str] = "https://credentials.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """上传一张图片，可用于作为证件照

        POST https://credentials.115.com/api/1.0/{app}/1.0/credentials/upload_images

        .. attention::
            此接口采用 multi-part 上传，其实是可以一次传多个文件的，但我做的封装只允许传一张图片，最大允许传 10 MB

        :param file: 待上传的文件
        :param app: 使用此设备的接口
        :param base_url: 接口的基地址
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 接口响应
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/credentials/upload_images", base_url=base_url
        )
        if isinstance(file, (str, PathLike)):
            file = open(file, "rb")
        return self.request(
            url=api,
            method="POST",
            files={"image": ("a.jpg", file)},
            async_=async_,
            **request_kwargs,
        )

    @overload
    def upload_image_init(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_image_init(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_image_init(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """网页端的上传图片接口的初始化

        POST https://uplb.115.com/3.0/imginitupload.php

        .. caution::
            此接口不支持秒传，最大支持上传 50 MB 的文件，上传成功后不占用空间

        .. caution::
            通过扩展名来识别，仅支持以下格式图片(jpg,jpeg,png,gif,svg,webp,heic,bmp,dng)

        .. note::
            ``target`` 随便设置，例如 ``"U_3_-1"``、``"U_4_-1"``、``"U_5_-2"``、``"U_3_-10"`` 等

        :payload:
            - filename: str = <default> 💡 文件名，默认为一个新的 uuid4 对象的字符串表示
            - target: str = ``"U_4_-1"`` 💡 上传目标，格式为 ``f"U_{aid}_{pid}"``
            - filesize: int | str = <default> 💡 图片大小
            - height: int = <default> 💡 图片高度
            - width: int = <default>  💡 图片宽度
        """
        api = complete_url("/3.0/imginitupload.php", base_url=base_url)
        if isinstance(payload, str):
            payload = {"filename": payload}
        elif "filename" not in payload:
            payload["filename"] = str(uuid4()) + ".jpg"
        payload.setdefault("target", "U_4_-1")
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def upload_sample_init(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_sample_init(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_sample_init(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://uplb.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """网页端的上传接口的初始化

        POST https://uplb.115.com/3.0/sampleinitupload.php

        .. caution::
            此接口不支持秒传

        .. note::
            如果上传到自己的网盘，则 ``target`` 的格式是 "U_{aid}_{pid}"，如果上传到共享目录，格式为 "S_{share_id}_{pid}"

        :payload:
            - filename: str = <default> 💡 文件名，默认为一个新的 uuid4 对象的字符串表示
            - target: str = "U_1_0" 💡 上传目标，格式为 f"U_{aid}_{pid}"（网盘）或 f"S_{share_id}_{pid}"（共享目录）
            - path: str = <default> 💡 保存目录，是在 `target` 对应目录下的相对路径，默认为 `target` 所对应目录本身
            - filesize: int | str = <default> 💡 文件大小
        """
        api = complete_url("/3.0/sampleinitupload.php", base_url=base_url)
        if isinstance(payload, str):
            payload = {"filename": payload}
        elif "filename" not in payload:
            payload["filename"] = str(uuid4())
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
        share_id: int = 0,
        payload: None | Mapping = None,
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
        share_id: int = 0,
        payload: None | Mapping = None,
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
        share_id: int = 0,
        payload: None | Mapping = None,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """初始化上传，可能秒传，此接口是对 `upload_init` 的封装

        .. note::
            - 文件大小 和 sha1 是必需的，只有 sha1 是没用的。
            - 如果文件大于等于 1 MB (1048576 B)，就需要 2 次检验一个范围哈希，就必须提供 `read_range_bytes_or_hash`

        :param filename: 文件名
        :param filesize: 文件大小
        :param filesha1: 文件的 sha1
        :param dirname: 保存目录，是在 `pid` 对应目录下的相对路径，默认为 `pid` 所对应目录本身
        :param read_range_bytes_or_hash: 调用以获取 2 次验证的数据或计算 sha1，接受一个数据范围，格式符合:
            `HTTP Range Requests <https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests>`_，
            返回值如果是 str，则视为计算好的 sha1，如果为 Buffer，则视为数据（之后会被计算 sha1）
        :param pid: 上传文件到此目录的 id，或者指定的 target（格式为 f"U_{aid}_{pid}" 或 f"S_{share_id}_{pid}"，但这里的 `aid` 无论如何取值，都视为 1）
        :param share_id: 共享 id
        :param payload: 其它的查询参数
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 接口响应
        """
        if isinstance(pid, str) and pid.startswith(("U_", "S_")):
            target = pid
        else:
            pid = to_id(pid)
            if share_id:
                target = f"S_{share_id}_{pid}"
            else:
                target = f"U_1_{pid}"
        default_payload = payload

        def gen_step():
            payload = {
                "filename": filename,
                "fileid": filesha1.upper(),
                "filesize": filesize,
                "target": target,
                "path": dirname,
            }
            if default_payload:
                payload.update(default_payload)
            resp = yield self.upload_init(
                payload,
                async_=async_,
                **request_kwargs,
            )
            status = resp["status"]
            if status == 7:
                if read_range_bytes_or_hash is None:
                    raise ValueError(
                        "filesize >= 1 MB, thus need pass the `read_range_bytes_or_hash` argument"
                    )
                payload["sign_key"] = resp["sign_key"]
                sign_check: str = resp["sign_check"]
                content: str | Buffer
                if async_:
                    content = yield ensure_async(read_range_bytes_or_hash)(sign_check)
                else:
                    content = read_range_bytes_or_hash(sign_check)
                if isinstance(content, str):
                    payload["sign_val"] = content.upper()
                else:
                    payload["sign_val"] = sha1(content).hexdigest().upper()
                resp = yield self.upload_init(
                    payload,
                    async_=async_,  # type: ignore
                    **request_kwargs,
                )
                status = resp["status"]
            resp["reuse"] = status == 2
            resp["state"] = status in (1, 2)
            return resp

        return run_gen_step(gen_step, async_)

    @overload
    def upload_chat_image(
        self,
        /,
        file: (
            Buffer
            | str
            | PathLike
            | URL
            | SupportsGeturl
            | SupportsRead
            | Iterable[Buffer]
        ),
        pid: int | str = "U_3_-1",
        share_id: int = 0,
        filename: str = "1.jpg",
        dirname: str = "",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_chat_image(
        self,
        /,
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
        pid: int | str = "U_3_-1",
        share_id: int = 0,
        filename: str = "1.jpg",
        dirname: str = "",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_chat_image(
        self,
        /,
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
        pid: int | str = "U_3_-1",
        share_id: int = 0,
        filename: str = "1.jpg",
        dirname: str = "",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """聊天窗口中上传一张图片

        .. caution::
            不支持秒传，但也不必传文件大小和 sha1，最大支持上传 50 MB 的文件

        .. note::
            ``target`` 随便设置，例如 ``"U_3_-1"``、``"U_4_-1"``、``"U_5_-2"``、``"U_3_-10"`` 等

        :param file: 待上传的文件
        :param pid: 上传文件到此目录的 id 或 pickcode，或者指定的 target（格式为 ``f"U_{aid}_{pid}"`` 或 ``f"S_{share_id}_{pid}"``）
        :param share_id: 共享 id
        :param filename: 文件名，如果为空，则会自动确定
        :param dirname: 保存目录，是在 `pid` 对应目录下的相对路径，默认为 `pid` 所对应目录本身
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 接口响应
        """
        if isinstance(pid, str) and pid.startswith(("U_", "S_")):
            target = pid
        else:
            pid = to_id(pid)
            if share_id:
                target = f"S_{share_id}_{pid}"
            else:
                target = f"U_1_{pid}"

        def gen_step():
            nonlocal file, filename
            file, filename = yield self._init_file(file, filename, async_=async_)  # type: ignore
            resp = yield self.upload_chat_image_init(
                {
                    "filename": filename or str(uuid4()) + ".jpg",
                    "path": dirname,
                    "target": target,
                },
                async_=async_,
                **request_kwargs,
            )
            check_response(resp)

            def parse(_, content: bytes):
                data = json_maybe_decrypt_loads(content)
                data["oss_info"] = resp
                return data

            request_kwargs.setdefault("parse", parse)
            return self.request(
                url=resp["host"],
                method="POST",
                data={
                    "host": resp["host"],
                    "key": resp["object"],
                    "policy": resp["policy"],
                    "OSSAccessKeyId": resp["accessid"],
                    "signature": resp["signature"],
                    "callback": resp["callback"],
                },
                files={"file": file},
                async_=async_,
                **request_kwargs,
            )

        return run_gen_step(gen_step, async_)

    @overload
    def upload_file_image(
        self,
        /,
        file: (
            Buffer
            | str
            | PathLike
            | URL
            | SupportsGeturl
            | SupportsRead
            | Iterable[Buffer]
        ),
        pid: int | str = "U_4_-1",
        share_id: int = 0,
        filename: str = "1.jpg",
        dirname: str = "",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_file_image(
        self,
        /,
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
        pid: int | str = "U_4_-1",
        share_id: int = 0,
        filename: str = "1.jpg",
        dirname: str = "",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_file_image(
        self,
        /,
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
        pid: int | str = "U_4_-1",
        share_id: int = 0,
        filename: str = "1.jpg",
        dirname: str = "",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """网页端的上传图片接口

        .. caution::
            不支持秒传，但也不必传文件大小和 sha1，最大支持上传 50 MB 的文件

        .. note::
            ``target`` 随便设置，例如 ``"U_3_-1"``、``"U_4_-1"``、``"U_5_-2"``、``"U_3_-10"`` 等

        :param file: 待上传的文件
        :param pid: 上传文件到此目录的 id 或 pickcode，或者指定的 target（格式为 ``f"U_{aid}_{pid}"`` 或 ``f"S_{share_id}_{pid}"``）
        :param share_id: 共享 id
        :param filename: 文件名，如果为空，则会自动确定
        :param dirname: 保存目录，是在 `pid` 对应目录下的相对路径，默认为 `pid` 所对应目录本身
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 接口响应
        """
        if isinstance(pid, str) and pid.startswith(("U_", "S_")):
            target = pid
        else:
            pid = to_id(pid)
            if share_id:
                target = f"S_{share_id}_{pid}"
            else:
                target = f"U_1_{pid}"

        def gen_step():
            nonlocal file, filename
            file, filename = yield self._init_file(file, filename, async_=async_)  # type: ignore
            resp = yield self.upload_image_init(
                {
                    "filename": filename or str(uuid4()) + ".jpg",
                    "path": dirname,
                    "target": target,
                },
                async_=async_,
                **request_kwargs,
            )

            def parse(_, content: bytes):
                data = json_maybe_decrypt_loads(content)
                data["oss_info"] = resp
                return data

            request_kwargs.setdefault("parse", parse)
            return self.request(
                url=resp["host"],
                method="POST",
                data={
                    "name": filename,
                    "key": resp["object"],
                    "policy": resp["policy"],
                    "OSSAccessKeyId": resp["accessid"],
                    "success_action_status": "200",
                    "callback": resp["callback"],
                    "signature": resp["signature"],
                },
                files={"file": file},
                async_=async_,
                **request_kwargs,
            )

        return run_gen_step(gen_step, async_)

    @overload
    def upload_file_sample(
        self,
        /,
        file: (
            Buffer
            | str
            | PathLike
            | URL
            | SupportsGeturl
            | SupportsRead
            | Iterable[Buffer]
        ),
        pid: int | str = 0,
        share_id: int = 0,
        filename: str = "",
        dirname: str = "",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def upload_file_sample(
        self,
        /,
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
        pid: int | str = 0,
        share_id: int = 0,
        filename: str = "",
        dirname: str = "",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def upload_file_sample(
        self,
        /,
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
        pid: int | str = 0,
        share_id: int = 0,
        filename: str = "",
        dirname: str = "",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """网页端的上传接口

        .. caution::
            不支持秒传，但也不必传文件大小和 sha1

        .. note::
            如果上传到共享目录，占用的是创建者的网盘空间

        .. note::
            只要上传后的 ``aid`` 或 ``area_id`` 不为 1，则不占用空间，这是 ``upload_file`` 所不能的（因为即使指定了 ``"U_{aid}_{pid}"``，也会忽略其中的 ``aid``，强行视为 1）

        .. note::
            如果我们把文件名分成两部分，名字 + 扩展名（含前缀点号 .），那么就有以下限制：

            1. 如果只有名字，最长 255 字节，超出则截掉尾部
            2. 如果只有扩展名，最长 255 字节，超出则截掉尾部
            3. 如果两者皆有，则情况比较复杂：

                1. （😯 这属于通常情况了）如果扩展名长度 <= 253 字节，则总长度不超过 255 字节，名字的超出部分会被替换为两个点号 ..，占用 2 个字节
                2. （😂 特意构造或者误断）如果扩展名长度 > 253 字节，允许的长度上限至少是 512 字节，又会有几套限制规则（具体会是哪一个，我目前还比较迷糊）：

                    1. 总长不超过 552 字节，超出部分会直接截掉名字的尾部，仍然不够则再截掉扩展名的尾部，此时只有 552 字节的扩展名部分
                    2. 总长不超过 512 字节，超出部分会直接截掉名字的尾部
                    3. 总长不超过 512 字节，超出部分会直接截掉名字的尾部并替换为 2 个点号 ..，仍然不够则再截掉扩展名的尾部，极端情况下，扩展名为 510 字节，名字部分变成两个点号 ..，占 2 字节
                    4. 总长不超过 512 字节，只要超过 255 字节，名字就被整体替换为 2 个点号 ..，仍然不够则再截掉扩展名的尾部
                    5. 总长不超过 512 字节，只要超过 255 字节，只会把名字的最后两个字符替换为 2 个点号 ..
                    6. ... (其它未被发现的规则，例如我还未测试仅含中文的场景)

        .. note::
            通过 ``pid``，支持随意指定上传目标。特别是当格式为 ``f"U_{aid}_{pid}"``，允许其中的 ``aid != 1`` 和 ``pid < 0`` （可能有特殊指代）。
            这里有一些特殊的位置：

            - ``U_0_{n}``: 等同于 ``pid="U_1_0"``，无论 ``n`` 是什么值
            - ``U_1_-11``: 上传附件到根目录下的 "记录文件"
            - ``U_3_-6``: 上传附件到根目录下的 "消息文件"
            - ``U_3_-15``: 上传封面到临时目录，等同于 ``pid="U_15_0"``
            - ``U_3_-24``: 上传文件到根目录下的 "手机备份"
            - ``U_3_{n}``: ``n`` 可取 -1,-2,-3,-4,-5,-8,-9,-10,-12,-13，等同于 ``pid="U_120_0"``
            - ``U_{a}_{n}``: ``n`` 可取 0 或所有 ``aid=1`` 的文件或目录的 id，则上传目标为 ``aid=a, cid=n``

        .. caution::
            如果最终的 ``aid`` 为 1 或 15，则剩余网盘空间会减掉上传文件的大小。
            尽量不要使 ``aid=15``，因为这会导致白白占掉空间，不能删除，也不能正常下载。

        :param file: 待上传的文件
        :param pid: 上传文件到此目录的 id 或 pickcode，或者指定的 target（格式为 ``f"U_{aid}_{pid}"`` 或 ``f"S_{share_id}_{pid}"``）
        :param share_id: 共享 id
        :param filename: 文件名，如果为空，则会自动确定
        :param dirname: 保存目录，是在 `pid` 对应目录下的相对路径，默认为 `pid` 所对应目录本身
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 接口响应
        """
        if isinstance(pid, str) and pid.startswith(("U_", "S_")):
            target = pid
        else:
            pid = to_id(pid)
            if share_id:
                target = f"S_{share_id}_{pid}"
            else:
                target = f"U_1_{pid}"

        def gen_step():
            nonlocal file, filename
            file, filename = yield self._init_file(file, filename, async_=async_)  # type: ignore
            resp = yield self.upload_sample_init(
                {
                    "filename": filename or str(uuid4()),
                    "path": dirname,
                    "target": target,
                },
                async_=async_,
                **request_kwargs,
            )

            def parse(_, content: bytes):
                data = json_maybe_decrypt_loads(content)
                data["oss_info"] = resp
                return data

            request_kwargs.setdefault("parse", parse)
            return self.request(
                url=resp["host"],
                method="POST",
                data={
                    "name": filename,
                    "key": resp["object"],
                    "policy": resp["policy"],
                    "OSSAccessKeyId": resp["accessid"],
                    "success_action_status": "200",
                    "callback": resp["callback"],
                    "signature": resp["signature"],
                },
                files={"file": file},
                async_=async_,
                **request_kwargs,
            )

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
            此时可以省略 ``pid``、``filename``、``filesha1``、``filesize``、``user_id``、``user_key``、``partsize``

        .. caution::
            ``partsize > 0`` 时，不要把 ``partsize`` 设置得太小，起码得 10 MB (10485760) 以上

        .. note::
            这个文件无论把文件传到哪，都会占用空间。这里有一些特殊的位置：

            - ``U_3_-8``: 此时 ``aid=120``，会平白占用空间，根本不能回收，所以要慎用
            - ``U_3_-9``: 此时 ``aid=12``，可以通过 ``fs_delete_app`` 删除上传后的文件 id 来释放空间

        :param file: 待上传的文件
        :param pid: 上传文件到此目录的 id 或 pickcode，或者指定的 target（格式为 f"U_{aid}_{pid}" 或 f"S_{share_id}_{pid}"，但这里的 `aid` 无论如何取值，都视为 1）
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
        return upload_file(
            file=file,
            pid=pid,
            share_id=share_id,
            filename=filename,
            filesha1=filesha1,
            filesize=filesize,
            dirname=dirname,
            user_id=self.user_id,
            user_key=self.user_key,
            payload=payload,
            partsize=partsize,
            callback=callback,
            upload_id=upload_id,
            endpoint=endpoint,
            async_=async_,  # type: ignore
            **request_kwargs,
        )
