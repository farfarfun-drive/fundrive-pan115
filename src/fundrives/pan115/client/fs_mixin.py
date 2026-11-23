#!/usr/bin/env python3

from __future__ import annotations

from typing import Any, Literal, cast, overload

from ._common import (
    Callable,
    Coroutine,
    Iterable,
    Path,
    _rsa_decrypt,
    complete_url,
    date,
    datetime,
    dumps,
    errno,
    json_loads,
    json_maybe_decrypt_loads,
    md5,
    md5_secret_password,
    rsa_encrypt,
    sha1,
    time,
)


class _P115ClientFsMixin:
    """文件系统、目录、回收站与标签接口混入。"""

    @overload
    def fs_batch_edit(
        self,
        payload: list | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_batch_edit(
        self,
        payload: list | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_batch_edit(
        self,
        payload: list | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量设置文件或目录（显示时长等）

        POST https://webapi.115.com/files/batch_edit

        :payload:
            - show_play_long[{fid}]: 0 | 1 = 1 💡 设置或取消显示时长
        """
        api = complete_url("/files/batch_edit", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_batch_edit_app(
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
    def fs_batch_edit_app(
        self,
        payload: list | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_batch_edit_app(
        self,
        payload: list | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量设置文件或目录（显示时长等）

        POST https://proapi.115.com/{app}/files/batch_edit

        :payload:
            - show_play_long[{fid}]: 0 | 1 = 1 💡 设置或取消显示时长
        """
        api = complete_url("/files/batch_edit", base_url=base_url, app=app)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_category_get(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_category_get(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_category_get(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """显示属性，可获取文件或目录的统计信息（提示：但得不到根目录的统计信息，所以 cid 为 0 时无意义）

        GET https://webapi.115.com/category/get

        .. caution::
            尝试获取目录的信息时，会去计算目录中文件和目录的数量、总文件大小 等信息，可能会消耗大量时间，但短时间内再次查询同一目录，耗时可能会大大减小

        :payload:
            - cid: int | str
            - fid: int | str 💡 ``cid`` 和 ``fid`` 至少需要提供一个
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

            - status: 0 | 1 = <default> 💡 如果为 1，那么文件已被删除，会返回错误
        """
        api = complete_url("/category/get", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"cid": payload}
        payload.setdefault("aid", 1)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_category_get_app(
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
    def fs_category_get_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_category_get_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """显示属性，可获取文件或目录的统计信息（提示：但得不到根目录的统计信息，所以 cid 为 0 时无意义）

        GET https://proapi.115.com/{app}/2.0/category/get

        .. caution::
            尝试获取目录的信息时，会去计算目录中文件和目录的数量、总文件大小 等信息，可能会消耗大量时间，但短时间内再次查询同一目录，耗时可能会大大减小

        :payload:
            - cid: int | str
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
        """
        api = complete_url("/2.0/category/get", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"cid": payload}
        payload.setdefault("aid", 1)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    fs_info = fs_category_get  # type: ignore

    fs_info_app = fs_category_get_app

    @overload
    def fs_category_shortcut(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_category_shortcut(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_category_shortcut(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """快捷入口列表（罗列所有的快捷入口）

        GET https://webapi.115.com/category/shortcut

        :payload:
            - offset: int = 0
            - limit: int = 1150
        """
        api = complete_url("/category/shortcut", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"offset": payload}
        payload = {"limit": 1150, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_category_shortcut_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        set: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_category_shortcut_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        set: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_category_shortcut_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        set: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """把一个目录设置或取消为快捷入口（快捷入口需要是目录）

        POST https://webapi.115.com/category/shortcut

        :payload:
            - file_id: int | str 目录 id，多个用逗号 "," 隔开
            - op: "add" | "delete" | "top" = "add" 操作代码

                - "add":    添加
                - "delete": 删除
                - "top":    置顶
        """
        api = complete_url("/category/shortcut", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload, "op": ("delete", "add")[set]}
        elif not isinstance(payload, dict):
            payload = {
                "file_id": ",".join(map(str, payload)),
                "op": ("delete", "add")[set],
            }
        else:
            payload = {"op": ("delete", "add")[set], **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_copy(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_copy(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_copy(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """复制文件或目录

        POST https://webapi.115.com/files/copy

        .. caution::
            ⚠️ 请不要并发执行，限制在 5 万个文件和目录以内

        :payload:
            - fid: int | str 💡 文件或目录 id，只接受单个 id
            - fid[]: int | str
            - ...
            - fid[0]: int | str
            - fid[1]: int | str
            - ...
            - pid: int | str = 0 💡 目标目录 id
        """
        api = complete_url("/files/copy", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"fid": payload}
        elif not isinstance(payload, dict):
            payload = {f"fid[{i}]": fid for i, fid in enumerate(payload)}
        payload.setdefault("pid", pid)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_copy_app(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_copy_app(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_copy_app(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """复制文件或目录

        POST https://proapi.115.com/{app}/files/copy

        .. caution::
            ⚠️ 请不要并发执行，限制在 5 万个文件和目录以内

        :payload:
            - fid: int | str 💡 文件或目录的 id，多个用逗号 "," 隔开
            - pid: int | str = 0 💡 目标目录 id
        """
        api = complete_url("/files/copy", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"fid": payload}
        elif not isinstance(payload, dict):
            payload = {"fid": ",".join(map(str, payload))}
        cast(dict, payload).setdefault("pid", pid)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_cover_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        fid_cover: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_cover_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        fid_cover: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_cover_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        fid_cover: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """修改封面，可以设置目录的封面，此接口是对 `fs_edit` 的封装"""
        return self._fs_edit_set(
            payload,
            "fid_cover",
            default=fid_cover,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def fs_cover_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        fid_cover: int | str,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_cover_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        fid_cover: int | str,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_cover_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        fid_cover: int | str = 0,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """修改封面，可以设置目录的封面，此接口是对 `fs_files_update_app` 的封装"""
        return self._fs_edit_set_app(
            payload,
            "fid_cover",
            default=fid_cover,
            app=app,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def fs_delete(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_delete(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_delete(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除文件或目录

        POST https://webapi.115.com/rb/delete

        .. caution::
            ⚠️ 请不要并发执行，但不限制文件数

        .. caution::
            删除和（从回收站）还原是互斥的，同时最多只允许执行一个操作

        :payload:
            - fid: int | str 💡 文件或目录的 id，多个用逗号 "," 隔开
            - fid[]: int | str
            - ...
            - fid[0]: int | str
            - fid[1]: int | str
            - ...
            - ignore_warn: 0 | 1 = <default>
            - from: int = <default>
            - pid: int = <default>
        """
        api = complete_url("/rb/delete", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"fid": payload}
        elif not isinstance(payload, dict):
            payload = {f"fid[{i}]": fid for i, fid in enumerate(payload)}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_delete_app(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_delete_app(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_delete_app(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除文件或目录

        POST https://proapi.115.com/{app}/rb/delete

        .. caution::
            ⚠️ 请不要并发执行，限制在 5 万个文件和目录以内

        .. caution::
            删除和（从回收站）还原是互斥的，同时最多只允许执行一个操作

        .. caution::
            有超过 5 万个文件和文件夹时，不能直接执行删除。如果删除的只是文件，那么在接口响应时，涉及的文件，已经删除完毕；但如果是目录，那么接口响应时，后台可能还在执行，而删除是不可并发的，因此下一个删除任务执行失败时，只需要反复重试即可

        .. note::
            此接口还能删除 `aid=12` 下的文件，且不会经过回收站（`aid=7`），而是彻底删除（`aid=120`）

            .. code:: python

                from pathlib import Path
                from itertools import batched
                from fundrives.pan115 import P115Client

                client = P115Client(Path("~/115-cookies.txt").expanduser())
                while True:
                    fids = [info["fid"] for info in client.fs_files({"aid": 12, "limit": 1150, "show_dir": 0})["data"]]
                    if not fids:
                        break
                    client.fs_delete_app(fids)

        :payload:
            - file_ids: int | str 💡 文件或目录的 id，多个用逗号 "," 隔开
            - user_id: int | str = <default> 💡 用户 id
        """
        api = complete_url("/rb/delete", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"file_ids": payload, "user_id": self.user_id}
        elif isinstance(payload, dict):
            payload = dict(payload, user_id=self.user_id)
        else:
            payload = {"file_ids": ",".join(map(str, payload)), "user_id": self.user_id}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_desc(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_desc(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_desc(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件或目录的备注

        GET https://webapi.115.com/files/desc

        :payload:
            - file_id: int | str
            - field: str = <default> 💡 可取示例值："pass"
            - compat: 0 | 1 = 1
            - new_html: 0 | 1 = <default>
        """
        api = complete_url("/files/desc", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        payload = {"compat": 1, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_desc_app(
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
    def fs_desc_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_desc_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件或目录的备注

        GET https://proapi.115.com/{app}/files/desc

        :payload:
            - file_id: int | str
            - field: str = <default> 💡 可取示例值："pass"
            - compat: 0 | 1 = 1
            - new_html: 0 | 1 = <default>
        """
        api = complete_url("/files/desc", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        payload = {"compat": 1, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_desc_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        desc: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_desc_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        desc: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_desc_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        desc: str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """为文件或目录设置备注，最多允许 65535 个字节 (64 KB 以内)，此接口是对 `fs_edit` 的封装

        .. hint::
            修改文件备注会更新文件的更新时间，即使什么也没改或者改为空字符串
        """
        return self._fs_edit_set(
            payload,
            "file_desc",
            default=desc,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def fs_desc_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        desc: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_desc_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        desc: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_desc_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        desc: str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """为文件或目录设置备注，最多允许 65535 个字节 (64 KB 以内)，此接口是对 `fs_files_update_app` 的封装

        .. hint::
            修改文件备注会更新文件的更新时间，即使什么也没改或者改为空字符串
        """
        return self._fs_edit_set_app(
            payload,
            "file_desc",
            desc,
            app=app,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def fs_dir_getid(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_dir_getid(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_dir_getid(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """由路径获取对应的 id（但只能获取目录，不能获取文件）

        GET https://webapi.115.com/files/getid

        :payload:
            - path: str
        """
        if isinstance(payload, str):
            payload = {"path": payload}
        if callable(base_url):
            base_url = base_url()
        if "://f.115.com" in base_url or "://n.115.com" in base_url:
            api = complete_url("/files/getid", base_url=base_url, query=payload)
            return self.request(url=api, async_=async_, **request_kwargs)
        api = complete_url("/files/getid", base_url=base_url)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_dir_getid2(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_dir_getid2(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_dir_getid2(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """由路径获取对应的 id（但只能获取目录，不能获取文件）

        GET https://webapi.115.com/files/get_path_id

        :payload:
            - path: str
            - parent_id: int = 0
            - is_create: 0 | 1 = 0 💡 当目录不存在时，是否创建
        """
        if isinstance(payload, str):
            payload = {"path": payload}
        if callable(base_url):
            base_url = base_url()
        if "://f.115.com" in base_url or "://n.115.com" in base_url:
            api = complete_url("/files/get_path_id", base_url=base_url, query=payload)
            return self.request(url=api, async_=async_, **request_kwargs)
        api = complete_url("/files/get_path_id", base_url=base_url)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_dir_getid_app(
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
    def fs_dir_getid_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_dir_getid_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """由路径获取对应的 id（但只能获取目录，不能获取文件）

        GET https://proapi.115.com/{app}/files/getid

        :payload:
            - path: str
        """
        api = complete_url("/files/getid", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"path": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_document(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_document(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_document(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文档的信息和下载链接

        GET https://webapi.115.com/files/document

        .. note::
            即使文件格式不正确或者是一个目录，也可返回一些信息（包括 parent_id）

        :payload:
            - pickcode: str
        """
        api = complete_url("/files/document", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_document_app(
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
    def fs_document_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_document_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文档的信息和下载链接

        GET https://proapi.115.com/{app}/files/document

        .. note::
            即使文件格式不正确或者是一个目录，也可返回一些信息（包括 parent_id）

        :payload:
            - pickcode: str
        """
        api = complete_url("/files/document", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_edit(
        self,
        payload: list | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_edit(
        self,
        payload: list | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_edit(
        self,
        payload: list | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置文件或目录（备注、标签、封面等）

        POST https://webapi.115.com/files/edit

        :payload:
            - fid: int | str
            - fid[]: int | str
            - ...
            - file_desc: str = <default> 💡 可以用 html
            - file_label: int | str = <default> 💡 标签 id，多个用逗号 "," 隔开
            - fid_cover: int | str = <default>  💡 封面图片的文件 id，多个用逗号 "," 隔开，如果要删除，值设为 0 即可
            - show_play_long: 0 | 1 = <default> 💡 文件名称显示时长
            - ...
        """
        api = complete_url("/files/edit", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_export_dir(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_export_dir(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_export_dir(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """导出目录树

        POST https://webapi.115.com/files/export_dir

        .. caution::
            【导出目录树】任务不可并发、不可中止，空目录不会被导出，输出的文件不会产生 life 操作事件

        :payload:
            - file_ids: int | str   💡 多个用逗号 "," 隔开
            - target: str = "U_1_0" 💡 导出目录树到这个目录
            - layer_limit: int = <default> 💡 层级深度，自然数
            - not_suffix: str = <default>
        """
        api = complete_url("/files/export_dir", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_ids": payload}
        payload.setdefault("target", "U_1_0")
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_export_dir_app(
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
    def fs_export_dir_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_export_dir_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """导出目录树

        POST https://proapi.115.com/{app}/2.0/ufile/export_dir

        .. caution::
            【导出目录树】任务不可并发、不可中止，空目录不会被导出，输出的文件不会产生 life 操作事件

        :payload:
            - file_ids: int | str   💡 多个用逗号 "," 隔开
            - target: str = "U_1_0" 💡 导出目录树到这个目录
            - layer_limit: int = <default> 💡 层级深度，自然数
        """
        api = complete_url("/2.0/ufile/export_dir", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"file_ids": payload}
        payload.setdefault("target", "U_1_0")
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_export_dir_status(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_export_dir_status(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_export_dir_status(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取导出目录树的完成情况

        GET https://webapi.115.com/files/export_dir

        :payload:
            - export_id: int | str = 0 💡 任务 id
        """
        api = complete_url("/files/export_dir", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"export_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_export_dir_status_app(
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
    def fs_export_dir_status_app(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_export_dir_status_app(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取导出目录树的完成情况

        GET https://proapi.115.com/{app}/2.0/ufile/export_dir

        :payload:
            - export_id: int | str = 0 💡 任务 id
        """
        api = complete_url("/2.0/ufile/export_dir", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"export_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_file(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_file(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_file(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件或目录的基本信息

        GET https://webapi.115.com/files/get_info

        .. caution::
            仅当文件的 aid 是 1（网盘文件）、12（瞬间文件） 或 120（永久删除文件） 时，才能用此接口获取信息，否则请用 `client.fs_file_skim` 或 `client.fs_supervision` 获取信息（只能获取比较简略的信息）。

            特别的，文件被移入回收站后，就不能用此接口获取信息了，除非将其还原或永久删除。

        :payload:
            - file_id: int | str 💡 文件或目录的 id，不能为 0，只能传 1 个 id，如果有多个只采用第一个
        """
        api = complete_url("/files/get_info", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_file_skim(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        method: str = "GET",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_file_skim(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        method: str = "GET",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_file_skim(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        method: str = "GET",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件或目录的简略信息

        GET https://webapi.115.com/files/file

        .. note::
            如果需要查询的 id 特别多，请指定 `method="POST"`

        :payload:
            - file_id: int | str 💡 文件或目录的 id，不能为 0，多个用逗号 "," 隔开
        """
        api = complete_url("/files/file", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        elif not isinstance(payload, dict):
            payload = {"file_id": ",".join(map(str, payload))}
        if method.upper() == "POST":
            request_kwargs["data"] = payload
        else:
            request_kwargs["params"] = payload
        return self.request(url=api, method=method, async_=async_, **request_kwargs)

    @overload
    def fs_files(
        self,
        payload: None | int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files(
        self,
        payload: None | int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files(
        self,
        payload: None | int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录中的文件列表和基本信息

        GET https://webapi.115.com/files

        .. attention::
            此接口被风控，此域名下的大量接口都会被风控，但重新登录可能恢复（多次登录必定不能恢复，即使更换设备）

        .. hint::
            指定如下条件中任一，且 cur = 0 （默认），即可遍历搜索所在目录树

            1. cid=0 且 star=1
            2. suffix 为非空的字符串
            3. type 为正整数
            4. show_dir=0 且 cur=0（或不指定 cur）

        .. hint::
            如果不指定或者指定的 cid 不存在，则会视为 cid=0 进行处理

            当指定 ``natsort=1`` 时，如果里面的数量较少时，可仅统计某个目录内的文件或目录总数，而不返回具体的文件信息

        .. hint::
            当一个 cookies 被另一个更新的登录所失效，并不意味着这个 cookies 就直接不可用了。

            如果你使用的是 `proapi` 下的接口，则会让你重新登录。但是 `webapi`、`aps` 等之下的接口，却依然可以正常使用。具体哪些失效，哪些还正常，请自行试验总结。这就意味着可以设计一种同一设备多 cookies 做池的分流策略。

        .. hint::
            对于普通的文件系统，我们只允许任何一个目录中不可有相同的名字，但是 115 网盘中却可能有重复：

            - 目录和文件同名：文件和目录同名在 115 中不算是一个冲突
            - 相同的目录名：转存可以导致同一目录下有多个相同名字的目录
            - 相同的文件名：转存、云下载和上传等，可以导致同一目录下有多个相同名字的文件

        .. hint::
            如果文件或目录被置顶，会在整个文件列表的最前面

            在根目录下且 ``fc_mix=0`` 且是特殊名字 ("最近接收", "手机相册", "云下载", "我的时光记录")（即 ``sys_dir``），会在整个文件列表的最前面但在置顶之后，这时可从返回信息的 "sys_count" 字段知道数目

        .. note::
            当 ``type=1`` 时，``suffix_type`` 的取值的含义：

                - (不填): 全部
                - 1: 文字（word，即 doc 和 docx 等）
                - 2: 表格（excel，即 xls 和 xlsx 等）
                - 3: 演示（ppt，即 ppt 和 pptx 等）
                - 4: pdf
                - 5: txt
                - 6: xmind
                - 7: 其它

        .. caution::
            ``fields`` 字段并不以返回的文件列表所有的字段名为准，而是要用其对应的完整名字，例如

            - "file_id": 对应 "cid"
            - "parent_id": 对应 "pid"
            - "area_id": 对应 "aid"
            - "file_name": 对应 "n"

            如果其中有一个是 "cid"，则可能只返回这一个字段，而不管你又指定了其它多少字段。
            由于这个参数的行为太过古怪且难猜，所以不建议使用，如果非要使用，建议换用 ``P115client.fs_files_app()``。

        :payload:
            - cid: int | str = 0 💡 目录 id，对应 parent_id
            - limit: int = 32 💡 分页大小，目前最大值是 1,150，以前是没限制的
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
            - count_folders: 0 | 1 = 1 💡 统计文件数和目录数，好像也可以写成 ``countfolders``
            - cur: 0 | 1 = <default> 💡 是否只搜索当前目录
            - custom_order: 0 | 1 = <default> 💡 启用自定义排序，如果指定了 "asc"、"fc_mix"、"o" 中其一，则此参数会被自动设置为 1

                - 0: 使用记忆排序（自定义排序失效）
                - 1: 使用自定义排序（不使用记忆排序）
                - 2: 自定义排序（非目录置顶）

            - fc_mix: 0 | 1 = <default> 💡 是否目录和文件混合，如果为 0 则目录在前（目录置顶）
            - fields: str = <default> 💡 筛选字段（⚠️ 不建议使用），多个用逗号 "," 隔开，如果存在字段无效，则文件列表为空（但有计数 "count"、"file_count" 和 "folder_count"）
            - hidden: 0 | 1 = <default>
            - is_q: 0 | 1 = <default> 💡 如果为 1，只显示文件
            - is_share: 0 | 1 = <default>
            - last_utime: int | str = <default>
            - min_size: int = 0 💡 最小的文件大小
            - max_size: int = 0 💡 最大的文件大小（含），<= 0 表示不限，因此并不能借此仅筛选出空文件
            - natsort: 0 | 1 = <default> 💡 是否执行自然排序(natural sorting) 💡 natural sorting
            - nf: 0 | 1 = <default> 💡 不要显示文件（即仅显示目录），但如果 show_dir=0，则此参数无效
            - o: str = <default> 💡 用某字段排序

                - "file_name": 文件名
                - "file_size": 文件大小
                - "file_type": 文件种类
                - "user_utime": 修改时间
                - "user_ptime": 创建时间
                - "user_otime": 上一次打开时间

            - oof_token: str = <default>
            - qid: int | str = <default>
            - r_all: 0 | 1 = <default>
            - record_open_time: 0 | 1 = 1 💡 是否要记录目录的打开时间
            - scid: int | str = <default>
            - show_dir: 0 | 1 = 1 💡 是否显示目录，好像也可以写成 showdir
            - snap: 0 | 1 = <default>
            - source: str = <default>
            - sys_dir: int | str = <default>
            - star: 0 | 1 = <default> 💡 是否星标文件
            - stdir: 0 | 1 = <default> 💡 筛选文件时，是否显示目录：1:展示 0:不展示
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
        api = complete_url("/files", base_url=base_url)
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
    def fs_files_app(
        self,
        payload: None | int | str | dict = 0,
        /,
        app: str = "android",
        version: str = "2.0",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_app(
        self,
        payload: None | int | str | dict = 0,
        /,
        app: str = "android",
        version: str = "2.0",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_app(
        self,
        payload: None | int | str | dict = 0,
        /,
        app: str = "android",
        version: str = "2.0",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录中的文件列表和基本信息

        GET https://proapi.115.com/{app}/{version}/ufile/files

        .. hint::
            如果要遍历获取所有文件，需要指定 show_dir=0 且 cur=0（或不指定 cur），这个接口并没有 type=99 时获取所有文件的意义

        .. note::
            一旦此接口被风控，那么同一域名下，所有路径尾部是 /files 的接口都被风控，但是如果你没有携带任何参数，竟然可以避免风控（至少可以用来获得一下文件总数，以及最近的 20 个创建的文件）。
            另外，proapi 之下，指定接口的版本为 2.0，可能会被服务器后台专门的处理，而其它版本（乃至于不指定版本），也往往被视为等同的，由此可以分为两类：2.0 版本和其它版本。

        .. attention::
            此接口存在一些潜在的问题。假如我上传了一个扩展名特别长的文件，越出了这个接口的能力范围，就会直接报错，例如：

            .. code:: python

                client.upload_file_sample(b"", filename="a."+"a"*300)
                # NOTE: 因而下面的请求将不会成功
                client.fs_files_app()

        .. caution::
            这个接口有些问题：

                1. 当 custom_order=1 时，如果设定 limit=1 可能会报错
                2. fc_mix 无论怎么设置，都和 fc_mix=0 的效果相同（即目录总是置顶），设置为 custom_order=2 也没用

        .. hint::
            置顶无效，但可以知道是否置顶了。

            在根目录下且 fc_mix=0 且是特殊名字 ("最近接收", "手机相册", "云下载", "我的时光记录")，会在整个文件列表的最前面，这时可从返回信息的 "sys_count" 字段知道数目

        .. tip::
            这个接口的 ``fields`` 参数可以筛选字段，例如，当你只需要文件 id 时，只需要指定 ``client.fs_files_app({"fields": "fid"})``

        :payload:
            - cid: int | str = 0 💡 目录 id，对应 parent_id
            - limit: int = 32 💡 分页大小，并没有上限，请预估返回的字节数自行调整规模，7,000 是大约安全了，如果用 ``fields`` 筛选了字段，可以增到 10,000，如果报 500 响应，则要适当减小些（或者多次尝试，偶有成功）
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
            - fields: str = <default> 💡 筛选字段，多个用逗号 "," 隔开，如果所有字段都无效，则返回全部
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

            - r_all: 0 | 1 = <default>
            - record_open_time: 0 | 1 = 1 💡 是否要记录目录的打开时间
            - scid: int | str = <default>
            - show_dir: 0 | 1 = 1 💡 是否显示目录
            - snap: 0 | 1 = <default>
            - source: str = <default>
            - sys_dir: int | str = <default> 💡 系统目录编号，0:最近接收 1:手机相册 2:云下载 3:我的时光记录 4,10,20,21,22,30,40,50,60,70:(未知)
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
                - 8-11: 大概相当于 1
                - 12: 文档+图片+视频，相当于 1、2、4
                - 13: ？？？，音频
                - 14: 大概相当于 1
                - 15: 图片+视频，相当于 2、4
                - >= 16: 相当于 8
        """
        api = complete_url("/ufile/files", base_url=base_url, app=app, version=version)
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
    def fs_files_app2(
        self,
        payload: None | int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_app2(
        self,
        payload: None | int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_app2(
        self,
        payload: None | int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录中的文件列表和基本信息

        GET https://proapi.115.com/{app}/files

        .. hint::x
            如果要遍历获取所有文件，需要指定 show_dir=0 且 cur=0（或不指定 cur），这个接口并没有 type=99 时获取所有文件的意义

        .. caution::
            这个接口有些问题：

                1. 当 custom_order=1 时，如果设定 limit=1 可能会报错
                2. fc_mix 无论怎么设置，都和 fc_mix=0 的效果相同（即目录总是置顶），设置为 custom_order=2 也没用

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
            - cur: 0 | 1 = <default> 💡 是否只搜索当前目录
            - custom_order: 0 | 1 | 2 = <default> 💡 启用自定义排序，如果指定了 "asc"、"fc_mix"、"o" 中其一，则此参数会被自动设置为 2

                - 0: 使用记忆排序（自定义排序失效）
                - 1: 使用自定义排序（不使用记忆排序）
                - 2: 自定义排序（非目录置顶）

            - fc_mix: 0 | 1 = <default> 💡 是否目录和文件混合，如果为 0 则目录在前（目录置顶）
            - for: str = <default> 💡 文件格式，例如 "doc"
            - hide_data: str = <default> 💡 是否返回文件数据
            - is_q: 0 | 1 = <default>
            - is_share: 0 | 1 = <default>
            - min_size: int = 0 💡 （⚠️ 似乎不可用）最小的文件大小
            - max_size: int = 0 💡 （⚠️ 似乎不可用）最大的文件大小（含），<= 0 表示不限，因此并不能借此仅筛选出空文件
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

            - r_all: 0 | 1 = <default>
            - record_open_time: 0 | 1 = 1 💡 是否要记录目录的打开时间
            - scid: int | str = <default>
            - show_dir: 0 | 1 = 1 💡 是否显示目录
            - snap: 0 | 1 = <default>
            - source: str = <default>
            - sys_dir: int | str = <default>
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
                - 8-11: 大概相当于 1
                - 12: 文档+图片+视频，相当于 1、2、4
                - 13: ？？？，音频
                - 14: 大概相当于 1
                - 15: 图片+视频，相当于 2、4
                - >= 16: 相当于 8
        """
        api = complete_url(
            "/files", base_url=base_url, app=app, force_app=("wechatmini", "alipaymini")
        )
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
    def fs_files_aps(
        self,
        payload: None | int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_aps(
        self,
        payload: None | int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_aps(
        self,
        payload: None | int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录中的文件列表和基本信息

        GET https://aps.115.com/natsort/files.php

        .. tip::
            这个接口的响应速度极快，在文件数特别多时，是 ``P115Client.fs_files`` 的数倍甚至数十倍的速度，更无论 ``P115Client.fs_files_app`` 了

        .. caution::
            这个函数最多获取任何一种排序条件下的前 ``1200 + n`` 条数据（``n >= 0`` 是一个潜在的不定限制）。

            `o` 参数无效，效果只等于 "file_name"，而 ``fc_mix`` 和 ``asc`` 可用。

            当 ``offset >= 1200 + n``，则相当于 ``offset=0&fc_mix=1``，即从头开始，且置顶项不会置顶

        .. hint::
            从技术上来讲最多可分别获取 ``(1200 + n) * 2`` 个文件和目录，即你可以通过改变顺序（asc 取 0 或者 1），来最多获取两倍于数量上限的不同条目，然后通过指定 ``show_dir=0&cur=1`` 和 ``show_dir=1&nf=1`` 来分别只获取文件或目录。

            不过对于文件，如果利用 ``type``、 ``suffix``、``min_size``、``max_size`` 等参数进行筛选，则可以获得更多，甚至可以是全部。

            注意：如果有置顶的条目，置顶条目总是出现，因此可能会使获取到的不同条目总数变少。

        :payload:
            - cid: int | str = 0 💡 目录 id，对应 parent_id
            - limit: int = 32 💡 分页大小，最大值是 1,200
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
            - cur: 0 | 1 = <default> 💡 是否只搜索当前目录
            - custom_order: 0 | 1 = <default> 💡 启用自定义排序，如果指定了 "asc"、"fc_mix" 中其一，则此参数会被自动设置为 1

                - 0: 使用记忆排序（自定义排序失效）
                - 1: 使用自定义排序（不使用记忆排序）
                - 2: 自定义排序（非目录置顶）

            - fc_mix: 0 | 1 = <default> 💡 是否目录和文件混合，如果为 0 则目录在前（目录置顶）
            - is_asc: 0 | 1 = <default>
            - min_size: int = 0 💡 最小的文件大小
            - max_size: int = 0 💡 最大的文件大小（含），<= 0 表示不限，因此并不能借此仅筛选出空文件
            - natsort: 0 | 1 = <default>
            - order: str = <default>
            - r_all: 0 | 1 = <default>
            - record_open_time: 0 | 1 = 1 💡 是否要记录目录的打开时间
            - scid: int | str = <default>
            - show_dir: 0 | 1 = 1 💡 是否显示目录
            - snap: 0 | 1 = <default>
            - source: str = <default>
            - sys_dir: int | str = <default>
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
                - 8-12: 大概相当于 1
                - 13: ？？？，音频
                - 14-15: 大概相当于 1
                - 16: 字幕
                - 17~98: 大概相当于 1
                - 99: 所有文件
                - >=100: 大概相当于 1
        """
        api = complete_url("/natsort/files.php", base_url=base_url)
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
        if payload.keys() & frozenset(("asc", "fc_mix")):
            payload["custom_order"] = 2
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_files_blank_document(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_blank_document(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_blank_document(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """新建空白 office 文件

        POST https://webapi.115.com/files/blank_document

        :payload:
            - file_name: str      💡 文件名，不含后缀
            - pid: int | str = 0  💡 目录 id，对应 parent_id
            - type: 1 | 2 | 3 = 1 💡 1:Word文档(.docx) 2:Excel表格(.xlsx) 3:PPT文稿(.pptx)
        """
        api = complete_url("/files/blank_document", base_url=base_url)
        if isinstance(payload, str):
            payload = {"file_name": payload}
        payload = {"pid": 0, "type": 1, **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_files_cover(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_cover(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_cover(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """查看是否有封面

        GET https://webapi.115.com/files/cover

        :payload:
            - file_id: int | str 💡 文件或目录 id
            - folder_as_file: 0 | 1 = <default>
        """
        api = complete_url("/files/cover", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_files_cover_set(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_cover_set(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_cover_set(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """是否生成封面

        POST https://webapi.115.com/files/cover

        :payload:
            - file_id: int | str 💡 文件或目录 id，多个用逗号 "," 隔开
            - show: 0 | 1 = 1
        """
        api = complete_url("/files/cover", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        payload.setdefault("show", 1)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_files_image(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_image(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_image(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录中的图片列表和基本信息

        GET https://webapi.115.com/files/imglist

        .. danger::
            这个函数大概是有 bug 的，不推荐使用，请用 ``fs_files_media`` 代替

        .. attention::
            只能获取直属于 `cid` 所在目录的图片，不会遍历整个目录树

        :payload:
            - cid: int | str     💡 目录 id
            - file_id: int | str 💡 不能是 0，可以是任何一个有效的 id（必须在自己网盘中，哪怕已经被删除，此必需参数只为应付检查）
            - limit: int = 32 💡 最多返回数量
            - offset: int = 0 💡 索引偏移，索引从 0 开始计算
            - is_asc: 0 | 1 = <default> 💡 是否升序排列
            - next: 0 | 1 = <default>
            - order: str = <default> 💡 用某字段排序

                - 文件名："file_name"
                - 文件大小："file_size"
                - 文件种类："file_type"
                - 修改时间："user_utime"
                - 创建时间："user_ptime"
                - 上一次打开时间："user_otime"
        """
        api = complete_url("/files/imglist", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"cid": payload}
        payload = {"limit": 32, "offset": 0, "cid": 0, **payload}
        if cid := payload.get("cid"):
            payload.setdefault("file_id", cid)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_files_image_app(
        self,
        payload: None | int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_image_app(
        self,
        payload: None | int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_image_app(
        self,
        payload: None | int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录中的图片列表和基本信息

        GET https://proapi.115.com/{app}/files/imglist

        :payload:
            - cid: int | str = 0 💡 目录 id，对应 parent_id
            - limit: int = 32    💡 一页大小，建议控制在 <= 9000，不然会报错
            - offset: int = 0    💡 索引偏移，索引从 0 开始计算

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
            - cur: 0 | 1 = 1 💡 只罗列当前目录
            - o: str = <default> 💡 用某字段排序

                - 文件名："file_name"
                - 文件大小："file_size"
                - 文件种类："file_type"
                - 修改时间："user_utime"
                - 创建时间："user_ptime"
                - 上一次打开时间："user_otime"
        """
        api = complete_url("/files/imglist", base_url=base_url, app=app)
        if payload is None:
            return self.request(url=api, async_=async_, **request_kwargs)
        if isinstance(payload, (int, str)):
            payload = {"cid": payload}
        payload = {"limit": 32, "offset": 0, "aid": 1, "cid": 0, "cur": 1, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_files_media(
        self,
        payload: None | int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_media(
        self,
        payload: None | int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_media(
        self,
        payload: None | int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录中的文件列表和基本信息（不含目录）

        GET https://webapi.115.com/files/medialist

        .. attention::
            有个 bug，当 ``cid=0&cur=1`` 时，似乎总是拉到空的文件列表，此时建议换成 ``client.fs_files({"cid": 0, "cur": 1, "show_dir": 0})``

        :payload:
            - cid: int | str = 0 💡 目录 id，对应 parent_id
            - limit: int = 32    💡 一页大小，建议控制在 <= 9000，不然会报错
            - offset: int = 0    💡 索引偏移，索引从 0 开始计算

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
            - cur: 0 | 1 = 1 💡 只罗列当前目录
            - o: str = <default> 💡 用某字段排序

                - 文件名："file_name"
                - 文件大小："file_size"
                - 文件种类："file_type"
                - 修改时间："user_utime"
                - 创建时间："user_ptime"
                - 上一次打开时间："user_otime"

            - type: int = -1 💡 文件类型（不传则视为 4）

                - <0: 全部文件（不含目录），响应中的 "type" 为 0
                - 0: 视为 4，响应中的 "type" 为 4
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
        api = complete_url("/files/medialist", base_url=base_url)
        if payload is None:
            return self.request(url=api, async_=async_, **request_kwargs)
        if not isinstance(payload, dict):
            payload = {"cid": payload}
        payload = {
            "limit": 32,
            "offset": 0,
            "aid": 1,
            "cid": 0,
            "cur": 1,
            "type": -1,
            **payload,
        }
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_files_media_app(
        self,
        payload: None | int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_media_app(
        self,
        payload: None | int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_media_app(
        self,
        payload: None | int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录中的文件列表和基本信息（不含目录）

        GET https://proapi.115.com/{app}/files/medialist

        :payload:
            - cid: int | str = 0 💡 目录 id，对应 parent_id
            - limit: int = 32    💡 一页大小，建议控制在 <= 9000，不然会报错
            - offset: int = 0    💡 索引偏移，索引从 0 开始计算

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
            - cur: 0 | 1 = 1 💡 只罗列当前目录
            - o: str = <default> 💡 用某字段排序

                - 文件名："file_name"
                - 文件大小："file_size"
                - 文件种类："file_type"
                - 修改时间："user_utime"
                - 创建时间："user_ptime"
                - 上一次打开时间："user_otime"

            - type: int =  💡 文件类型（不传则视为 4）

                - <0: 全部文件（不含目录），响应中的 "type" 为 0
                - 0: 视为 2，因为响应中的 "type" 为 2
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
        api = complete_url("/files/medialist", base_url=base_url, app=app)
        if payload is None:
            return self.request(url=api, async_=async_, **request_kwargs)
        if isinstance(payload, (int, str)):
            payload = {"cid": payload}
        payload = {
            "limit": 32,
            "offset": 0,
            "aid": 1,
            "cid": 0,
            "cur": 1,
            "type": -1,
            **payload,
        }
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_files_recent_docs(
        self,
        payload: int | dict = 1000,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_recent_docs(
        self,
        payload: int | dict = 1000,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_recent_docs(
        self,
        payload: int | dict = 1000,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取最近上传的文档

        POST https://webapi.115.com/files/recent

        .. todo::
            这个接口可能支持其它参数，但目前暂未搞清楚

        :payload:
            - limit: int
        """
        api = complete_url("/files/recent", base_url=base_url)
        if isinstance(payload, int):
            payload = {"limit": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_files_recent_docs_app(
        self,
        payload: int | dict = 1000,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_recent_docs_app(
        self,
        payload: int | dict = 1000,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_recent_docs_app(
        self,
        payload: int | dict = 1000,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取最近上传的文档

        POST https://proapi.115.com/{app}/2.0/ufile/recent

        .. todo::
            这个接口可能支持其它参数，但目前暂未搞清楚

        :payload:
            - limit: int
        """
        api = complete_url("/2.0/ufile/recent", base_url=base_url, app=app)
        if isinstance(payload, int):
            payload = {"limit": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_files_second_type(
        self,
        payload: Literal[1, 2, 3, 4, 5, 6, 7] | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_second_type(
        self,
        payload: Literal[1, 2, 3, 4, 5, 6, 7] | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_second_type(
        self,
        payload: Literal[1, 2, 3, 4, 5, 6, 7] | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录中某个文件类型的扩展名的（去重）列表

        GET https://webapi.115.com/files/get_second_type

        :payload:
            - cid: int | str = 0 💡 目录 id，对应 parent_id
            - type: int = 1 💡 文件类型

                - 1: 文档
                - 2: 图片
                - 3: 音频
                - 4: 视频
                - 5: 压缩包
                - 6: 软件/应用
                - 7: 书籍

            - file_label: int | str = <default> 💡 标签 id，多个用逗号 "," 隔开
        """
        api = complete_url("/files/get_second_type", base_url=base_url)
        if isinstance(payload, int):
            payload = {"type": payload}
        payload = {"cid": 0, "type": 1, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_files_second_type_app(
        self,
        payload: Literal[1, 2, 3, 4, 5, 6, 7] | dict = 1,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_second_type_app(
        self,
        payload: Literal[1, 2, 3, 4, 5, 6, 7] | dict = 1,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_second_type_app(
        self,
        payload: Literal[1, 2, 3, 4, 5, 6, 7] | dict = 1,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录中某个文件类型的扩展名的（去重）列表

        GET https://proapi.115.com/{app}/2.0/ufile/get_second_type

        :payload:
            - cid: int | str = 0 💡 目录 id，对应 parent_id
            - type: int = 1 💡 文件类型

                - 1: 文档
                - 2: 图片
                - 3: 音频
                - 4: 视频
                - 5: 压缩包
                - 6: 软件/应用
                - 7: 书籍

            - file_label: int | str = <default> 💡 标签 id，多个用逗号 "," 隔开
        """
        api = complete_url("/2.0/ufile/get_second_type", base_url=base_url, app=app)
        if isinstance(payload, int):
            payload = {"type": payload}
        payload = {"cid": 0, "type": 1, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_files_update_app(
        self,
        payload: int | str | tuple[int | str] | list | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_files_update_app(
        self,
        payload: int | str | tuple[int | str] | list | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_files_update_app(
        self,
        payload: int | str | tuple[int | str] | list | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置（若干个）文件或目录（名字、备注、标签等）

        POST https://proapi.115.com/{app}/files/update

        :payload:
            - file_id: int | str
            - file_id[]: int | str
            - ...
            - file_id[0]: int | str
            - file_id[1]: int | str
            - ...
            - file_desc: str = <default> 💡 可以用 html
            - file_label: int | str = <default> 💡 标签 id，多个用逗号 "," 隔开
            - file_name: str = <default>        💡 文件或目录名
            - fid_cover: int | str = <default>  💡 封面图片的文件 id，多个用逗号 "," 隔开，如果要删除，值设为 0 即可
            - show_play_long: 0 | 1 = <default> 💡 文件名称显示时长
            - ...
        """
        api = complete_url("/files/update", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        elif isinstance(payload, tuple):
            payload = {"file_id[i]": p for i, p in enumerate(payload)}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_folder_app(
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
    def fs_folder_app(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_folder_app(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录列表（不含文件）

        GET https://proapi.115.com/{app}/folder/update

        :payload:
            - p_id: int
            - offset: int = 0
            - limit: int = 1150
            - user_id: int | str = <default> 💡 用户 id，不必是自己 🤪
            - ...
        """
        api = complete_url("/folder/update", base_url=base_url, app=app)
        if not isinstance(payload, dict):
            payload = {"p_id": payload}
        payload = {
            "limit": 1150,
            "offset": 0,
            "p_id": 0,
            "user_id": self.user_id,
            **payload,
        }
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_folder_app2(
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
    def fs_folder_app2(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_folder_app2(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录列表（不含文件）

        GET https://proapi.115.com/{app}/folder

        :payload:
            - p_id: int
            - offset: int = 0
            - limit: int = 1150
            - user_id: int | str = <default> 💡 用户 id，不必是自己 🤪
            - aid: int = 1
            - ...
        """
        api = complete_url("/folder", base_url=base_url, app=app)
        if not isinstance(payload, dict):
            payload = {"p_id": payload}
        payload = {
            "aid": 1,
            "limit": 1150,
            "offset": 0,
            "p_id": 0,
            "user_id": self.user_id,
            **payload,
        }
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_folder_file(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_folder_file(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_folder_file(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录中的文件列表（不含目录）

        GET https://webapi.115.com/folder/file

        .. todo::
            ``limit`` 参数无效，即不能设定分页大小，此接口还需继续挖掘 ⛏️

        :payload:
            - cid: int | str
            - offset: int = 0
            - limit: int = 1150 💡 ⚠️ 无效，只能是默认获取 15 条
            - user_id: int | str = <default> 💡 用户 id，不必是自己 🤪
            - aid: int = 1
            - ...
        """
        api = complete_url("/folder/file", base_url=base_url)
        if not isinstance(payload, dict):
            payload = {"cid": payload}
        payload = {
            "aid": 1,
            "limit": 1150,
            "offset": 0,
            "cid": 0,
            "user_id": self.user_id,
            **payload,
        }
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_folder_playlong(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_folder_playlong(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_folder_playlong(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录内文件总的播放时长

        POST https://aps.115.com/getFolderPlaylong

        :payload:
            - folder_ids: int | str 💡 目录 id，多个用逗号 "," 隔开
        """
        api = complete_url("/getFolderPlaylong", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"folder_ids": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_folder_playlong_set(
        self,
        /,
        ids: int | str | Iterable[int | str],
        is_set: Literal[0, 1] = 1,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_folder_playlong_set(
        self,
        /,
        ids: int | str | Iterable[int | str],
        is_set: Literal[0, 1] = 1,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_folder_playlong_set(
        self,
        /,
        ids: int | str | Iterable[int | str],
        is_set: Literal[0, 1] = 1,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """显示或取消目录内文件总的播放时长，此接口是对 `fs_batch_edit` 的封装

        :param ids: 一个或多个文件或目录的 id
        :param is_set: 是否显示时长

        :return: 返回成功状态
        """
        if isinstance(ids, (int, str)):
            payload = {f"show_play_long[{ids}]": is_set}
        else:
            payload = {f"show_play_long[{id}]": is_set for id in ids}
        return self.fs_batch_edit(
            payload, base_url=base_url, async_=async_, **request_kwargs
        )

    @overload
    def fs_folder_update_app(
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
    def fs_folder_update_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_folder_update_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置文件或目录，或者创建目录

        POST https://proapi.115.com/{app}/folder/update

        .. note::
            如果提供了 `cid` 和 `name`，则表示对 `cid` 对应的文件或目录进行改名，否则创建目录

        :payload:
            - name: str 💡 名字
            - pid: int | str = 0 💡 在此目录 id 下创建目录
            - aid: int = 1 💡 area_id
            - cid: int = <default> 💡 文件或目录的 id，优先级高于 `pid`
            - user_id: int | str = <default> 💡 用户 id
            - ...
        """
        api = complete_url("/folder/update", base_url=base_url, app=app)
        payload = {"aid": 1, "pid": 0, "user_id": self.user_id, **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_folder_update_app2(
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
    def fs_folder_update_app2(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_folder_update_app2(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置文件或目录，或者创建目录

        POST https://proapi.115.com/{app}/folder

        .. note::
            如果提供了 `cid` 和 `name`，则表示对 `cid` 对应的文件或目录进行改名，否则创建目录

        :payload:
            - name: str 💡 名字
            - pid: int | str = 0 💡 在此目录 id 下创建目录
            - aid: int = 1 💡 area_id
            - cid: int = <default> 💡 文件或目录的 id，优先级高于 `pid`
            - user_id: int | str = <default> 💡 用户 id
            - ...
        """
        api = complete_url("/folder", base_url=base_url, app=app)
        payload = {"aid": 1, "pid": 0, "user_id": self.user_id, **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_hide(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        hidden: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_hide(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        hidden: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_hide(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        hidden: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """隐藏或者取消隐藏某些文件或目录

        POST https://webapi.115.com/files/hiddenfiles

        :payload:
            - fid[0]: int | str
            - fid[1]: int | str
            - ...
            - hidden: 0 | 1 = 1
        """
        api = complete_url("/files/hiddenfiles", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"fid[0]": payload}
        elif not isinstance(payload, dict):
            payload = {f"fid[{i}]": f for i, f in enumerate(payload)}
        payload.setdefault("hidden", int(hidden))
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_hide_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        hidden: bool = True,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_hide_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        hidden: bool = True,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_hide_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        hidden: bool = True,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """隐藏或者取消隐藏某些文件或目录

        POST https://proapi.115.com/{app}/files/hiddenfiles

        :payload:
            - fid: int | str 💡 文件或目录的 id，多个用逗号 "," 隔开
            - hidden: 0 | 1 = 1
        """
        api = complete_url("/files/hiddenfiles", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"fid": payload}
        elif not isinstance(payload, dict):
            payload = {"fid": ",".join(map(str, payload))}
        cast(dict, payload).setdefault("hidden", int(hidden))
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_hidden_switch(
        self,
        payload: bool | int | str | dict = False,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_hidden_switch(
        self,
        payload: bool | int | str | dict = False,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_hidden_switch(
        self,
        payload: bool | int | str | dict = False,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """切换隐藏模式

        POST https://115.com/?ct=hiddenfiles&ac=switching

        .. tip::
            开启隐藏模式时，需要提供安全密钥，关闭时则不需要

        .. tip::
            这个接口必须提供安全密钥。如果不提供，则默认使用 "000000"，在不必要的情况下，完全可以把安全密钥设为这个值

        .. note::
            这个接口会返回一个 "token" 字段，可以提供给某些接口，作为通过安全密钥验证的凭证

        :payload:
            - safe_pwd: str = "000000" 💡 安全密钥
            - show: 0 | 1 = <default>  💡 是否开启隐藏模式：0:关闭 1:开启
            - valid_type: int = <default>
        """
        api = complete_url(
            base_url=base_url, query={"ct": "hiddenfiles", "ac": "switching"}
        )
        if payload in (0, 1):
            payload = {"show": int(cast(int, payload))}
        elif isinstance(payload, (int, str)):
            payload = {"show": 1, "safe_pwd": f"{payload:>06}"}
        payload["safe_pwd"] = format(payload.get("safe_pwd") or "", ">06")
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_hidden_switch_app(
        self,
        payload: bool | int | str | dict = False,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_hidden_switch_app(
        self,
        payload: bool | int | str | dict = False,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_hidden_switch_app(
        self,
        payload: bool | int | str | dict = False,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """切换隐藏模式

        GET https://proapi.115.com/{app}/files/hiddenswitch

        .. note::
            可以在设置中的【账号安全/安全密钥】页面下，关闭【文件(隐藏模式/清空删除回收站)】的按钮，就不需要传安全密钥了

        :payload:
            - safe_pwd: str = "000000" 💡 安全密钥，值为实际安全密钥的 md5 哈希值
            - show: 0 | 1 = <default>  💡 是否开启隐藏模式：0:关闭 1:开启
            - token: str = <default>   💡 令牌，调用 `P115client.user_security_key_check()` 获得，可以不传
        """
        api = complete_url("/files/hiddenswitch", base_url=base_url, app=app)
        if payload in (0, 1):
            payload = {"show": int(cast(int, payload))}
        elif isinstance(payload, (int, str)):
            payload = {"show": 1, "safe_pwd": payload}
        payload["safe_pwd"] = md5_secret_password(payload.get("safe_pwd"))
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_history(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_history(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件的观看历史，主要用于视频

        GET https://webapi.115.com/files/history

        :payload:
            - pick_code: str
            - fetch: str = "one"
            - category: int = 1 💡 类型：1:视频 3:音频
            - share_id: int | str = <default>
        """
        api = complete_url("/files/history", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        payload = {"category": 1, "fetch": "one", **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    fs_video_history = fs_history

    @overload
    def fs_history_app(
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
    def fs_history_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取历史记录

        GET https://proapi.115.com/{app}/history

        :payload:
            - pick_code: str
            - fetch: str = "one"
            - category: int = 1
            - share_id: int | str = <default>
        """
        api = complete_url("/history", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        payload = {"category": 1, "action": "get_one", **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    fs_video_history_app = fs_history_app

    @overload
    def fs_history_clean(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_history_clean(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_clean(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """清空历史记录

        POST https://webapi.115.com/history/clean

        :payload:
            - type: int | str = 0 💡 类型（？？表示还未搞清楚），多个用逗号 "," 隔开

                - 全部: 0
                - ？？: 1（大概和接收有关）
                - 云下载: 2
                - 播放视频: 3
                - 上传: 4
                - ？？: 5
                - ？？: 6（大概和名称冲突有关）
                - 接收: 7
                - 移动: 8

            - with_file: 0 | 1 = 0 💡 是否同时删除文件
        """
        api = complete_url("/history/clean", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"type": payload}
        payload = {"with_file": 0, "type": 0, **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_history_delete(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_history_delete(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_delete(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除历史记录

        POST https://webapi.115.com/history/delete

        :payload:
            - id: int | str 💡 多个用逗号 "," 隔开
            - type: int = 0
            - with_file: 0 | 1 = 0
        """
        api = complete_url("/history/delete", base_url=base_url)
        if not isinstance(payload, dict):
            payload = {"id": payload}
        payload.setdefault("with_file", 0)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_history_delete_app(
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
    def fs_history_delete_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_delete_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除历史记录

        POST https://proapi.115.com/{app}/history/delete

        :payload:
            - id: int | str 💡 多个用逗号 "," 隔开
            - with_file: 0 | 1 = 0
        """
        api = complete_url("/history/delete", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"id": payload}
        payload.setdefault("with_file", 0)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_history_clean_app(
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
    def fs_history_clean_app(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_clean_app(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """清空历史记录

        POST https://proapi.115.com/{app}/history/clean

        :payload:
            - type: int | str = 0 💡 类型（？？表示还未搞清楚），多个用逗号 "," 隔开

                - 全部: 0
                - ？？: 1（大概和接收有关）
                - 云下载: 2
                - 播放视频: 3
                - 上传: 4
                - ？？: 5
                - ？？: 6（大概和名称冲突有关）
                - 接收: 7
                - 移动: 8

            - with_file: 0 | 1 = 0
        """
        api = complete_url("/history/clean", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"type": payload}
        payload = {"with_file": 0, "type": 0, **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_history_list(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_history_list(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_list(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """历史记录列表

        GET https://webapi.115.com/history/list

        :payload:
            - offset: int = 0
            - limit: int = 1150
            - order: str = <default>
            - played_end: 0 | 1 = <default> 💡 是否已经播放完
            - search_value: str = ""
            - type: int = <default> 💡 类型（？？表示还未搞清楚），多个用逗号 "," 隔开

                - 全部: 0
                - ？？: 1（大概和接收有关）
                - 云下载: 2
                - 播放视频: 3
                - 上传: 4
                - ？？: 5
                - ？？: 6（大概和名称冲突有关）
                - 接收: 7
                - 移动: 8
        """
        api = complete_url("/history/list", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"offset": payload}
        payload = {"limit": 1150, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_history_list_app(
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
    def fs_history_list_app(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_list_app(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """历史记录列表

        GET https://proapi.115.com/{app}/history/list

        :payload:
            - offset: int = 0
            - limit: int = 1150
            - played_end: 0 | 1 = <default>
            - type: int = <default> 💡 类型（？？表示还未搞清楚），多个用逗号 "," 隔开

                - 全部: 0
                - ？？: 1（大概和接收有关）
                - 云下载: 2
                - 播放视频: 3
                - 上传: 4
                - ？？: 5
                - ？？: 6（大概和名称冲突有关）
                - 接收: 7
                - 移动: 8
        """
        api = complete_url("/history/list", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"offset": payload}
        payload = {"limit": 1150, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_history_move_target_list(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_history_move_target_list(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_move_target_list(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """最近移动记录

        GET https://webapi.115.com/history/move_target_list

        .. tip::
            使用这个方法，甚至可以随时获取近期有文件移入的目录，可以部分代替 115 生活的移动事件的使用

        :payload:
            - cid: int | str = 0 💡 目录 id，对应 parent_id
            - limit: int = 1150 💡 分页大小，最大值不一定，看数据量，7,000 应该总是安全的，10,000 有可能报错，但有时也可以 20,000 而成功
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
            - custom_order: 0 | 1 | 2 = <default> 💡 是否使用记忆排序。如果指定了 "asc"、"fc_mix"、"o" 中其一，则此参数会被自动设置为 2

                - 0: 使用记忆排序（自定义排序失效）
                - 1: 使用自定义排序（不使用记忆排序）
                - 2: 自定义排序（非目录置顶）

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
            - search_value: str = <default> 💡 搜索文本
            - show_dir: 0 | 1 = 1 💡 是否显示目录
            - snap: 0 | 1 = <default>
            - source: str = <default>
        """
        api = complete_url("/history/move_target_list", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"offset": payload}
        payload = {
            "cid": 0,
            "limit": 1150,
            "offset": 0,
            "aid": 1,
            "show_dir": 1,
            **payload,
        }
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_history_receive_list(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_history_receive_list(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_receive_list(
        self,
        payload: int | str | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """接收列表

        GET https://webapi.115.com/history/receive_list

        :payload:
            - offset: int = 0
            - limit: int = 1150
        """
        api = complete_url("/history/receive_list", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"offset": payload}
        payload = {"limit": 1150, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_history_receive_list_app(
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
    def fs_history_receive_list_app(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_receive_list_app(
        self,
        payload: int | str | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """接收列表

        GET https://proapi.115.com/{app}/history/receive_list

        :payload:
            - offset: int = 0
            - limit: int = 1150
        """
        api = complete_url("/history/receive_list", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"offset": payload}
        payload = {"limit": 1150, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_history_rename_list(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_history_rename_list(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_rename_list(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        method: str = "POST",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """重命名历史记录

        POST https://webapi.115.com/history/renamelist

        :payload:
            - file_ids: int | str 💡 文件 id，多个用逗号 "," 隔开
            - offset: int = 0
            - limit: int = <default>
            - type: int = <default>
        """
        api = complete_url("/history/renamelist", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_ids": str(payload)}
        elif not isinstance(payload, dict):
            payload = {"file_ids": ",".join(map(str, payload))}
        return self.request(
            url=api, method=method, payload=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_history_rename_list_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        method: str = "POST",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_history_rename_list_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        method: str = "POST",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_rename_list_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        method: str = "POST",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """重命名历史记录

        POST https://proapi.115.com/files/history/renamelist

        :payload:
            - file_ids: int | str 💡 文件 id，多个用逗号 "," 隔开
            - offset: int = 0
            - limit: int = <default>
            - type: int = <default>
        """
        api = complete_url("/files/history/renamelist", base_url=base_url, app=app)
        if isinstance(payload, (int,)):
            payload = {"file_ids": payload}
        elif not isinstance(payload, dict):
            payload = {"file_ids": ",".join(map(str, payload))}
        return self.request(
            url=api, method=method, payload=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_history_set(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_history_set(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_set(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """更新文件的观看历史，主要用于视频和音频

        POST https://webapi.115.com/files/history

        :payload:
            - pick_code: str     💡 文件的提取码
            - op: str = "update" 💡 操作类型，具体有哪些还需要再研究
            - category: int = 1  💡 类型：1:视频 3:音频
            - definition: int = <default> 💡 视频清晰度
            - share_id: int | str = <default>
            - time: int = <default> 💡 播放时间点（用来向服务器同步播放进度）
            - watch_end: int = <default> 💡 视频是否播放播放完毕 0:未完毕 1:完毕
            - ...（其它未找全的参数）
        """
        api = complete_url("/files/history", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        payload = {"category": 1, "op": "update", **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    fs_video_history_set = fs_history_set

    @overload
    def fs_history_set_app(
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
    def fs_history_set_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_history_set_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """更新文件的观看历史，主要用于视频

        POST https://proapi.115.com/{app}/history

        :payload:
            - pick_code: str     💡 文件的提取码
            - op: str = "update" 💡 操作类型，具体有哪些还需要再研究
            - category: int = 1
            - definition: int = <default> 💡 视频清晰度
            - share_id: int | str = <default>
            - time: int = <default> 💡 播放时间点（用来向服务器同步播放进度）
            - watch_end: int = <default> 💡 视频是否播放播放完毕 0:未完毕 1:完毕
            - ...（其它未找全的参数）
        """
        api = complete_url("/files/hiddenswitch", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        payload = {"category": 1, "op": "update", **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    fs_video_history_set_app = fs_history_set_app

    @overload
    def fs_image(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_image(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_image(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取图片的各种链接

        GET https://webapi.115.com/files/image

        :payload:
            - pickcode: str  💡 同 ``pick_code``，优先级较高
            - pick_code: str 💡 同 ``pickcode``
            - share_id: int | str = <default>
        """
        api = complete_url("/files/image", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_imagedata(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://imgjump.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_imagedata(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://imgjump.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_imagedata(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://imgjump.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取图片的分辨率等信息

        POST https://imgjump.115.com/getimgdata_url

        :payload:
            - imgurl: str 💡 图片的访问链接
        """
        api = complete_url("/getimgdata_url", base_url=base_url)
        if isinstance(payload, str):
            payload = {"imgurl": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_index_info(
        self,
        payload: Literal[0, 1] | bool | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_index_info(
        self,
        payload: Literal[0, 1] | bool | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_index_info(
        self,
        payload: Literal[0, 1] | bool | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取当前已用空间、可用空间、登录设备等信息

        GET https://webapi.115.com/files/index_info

        :payload:
            - count_space_nums: 0 | 1 = 0 💡 是否获取明细：0:包含各种类型文件的数量统计 1:包含登录设备列表
        """
        api = complete_url("/files/index_info", base_url=base_url)
        if not isinstance(payload, dict):
            payload = {"count_space_nums": int(payload)}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_label_add(
        self,
        payload: str | Iterable[str] | dict | list[tuple],
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_label_add(
        self,
        payload: str | Iterable[str] | dict | list[tuple],
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_label_add(
        self,
        payload: str | Iterable[str] | dict | list[tuple],
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """添加标签（可以接受多个）

        POST https://webapi.115.com/label/add_multi

        :payload:
            - name: str 💡 格式为 "{label_name}" 或 "{label_name}\x07{color}"，例如 "tag\x07#FF0000"（中间有个 "\\x07"）
            - name[]: str
            - ...
        """
        api = complete_url("/label/add_multi", base_url=base_url)
        if isinstance(payload, str):
            payload = [("name[]", payload)]
        elif (
            not isinstance(payload, dict)
            or not isinstance(payload, list)
            and payload
            and not isinstance(payload[0], tuple)
        ):
            payload = [("name[]", label) for label in payload if label]
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_label_add_app(
        self,
        payload: str | Iterable[str] | dict | list[tuple],
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_label_add_app(
        self,
        payload: str | Iterable[str] | dict | list[tuple],
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_label_add_app(
        self,
        payload: str | Iterable[str] | dict | list[tuple],
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """添加标签（可以接受多个）

        POST https://proapi.115.com/{app}/label/add_multi

        :payload:
            - name: str 💡 格式为 "{label_name}" 或 "{label_name}\x07{color}"，例如 "tag\x07#FF0000"（中间有个 "\\x07"）
            - name[]: str
            - ...
        """
        api = complete_url("/label/add_multi", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = [("name[]", payload)]
        elif (
            not isinstance(payload, dict)
            or not isinstance(payload, list)
            and payload
            and not isinstance(payload[0], tuple)
        ):
            payload = [("name[]", label) for label in payload if label]
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_label_del(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_label_del(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_label_del(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除标签

        POST https://webapi.115.com/label/delete

        :payload:
            - id: int | str 💡 标签 id，多个用逗号 "," 隔开
        """
        api = complete_url("/label/delete", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"id": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_label_del_app(
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
    def fs_label_del_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_label_del_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """删除标签

        POST https://proapi.115.com/{app}/label/delete

        :payload:
            - id: int | str 💡 标签 id，多个用逗号 "," 隔开
        """
        api = complete_url("/label/delete", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"id": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_label_edit(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_label_edit(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_label_edit(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """编辑标签

        POST https://webapi.115.com/label/edit

        :payload:
            - id: int | str 💡 标签 id
            - name: str = <default>  💡 标签名
            - color: str = <default> 💡 标签颜色，支持 css 颜色语法
            - sort: int = <default>  💡 序号
        """
        api = complete_url("/label/edit", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_label_edit_app(
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
    def fs_label_edit_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_label_edit_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """编辑标签

        POST https://proapi.115.com/{app}/label/edit

        :payload:
            - id: int | str 💡 标签 id
            - name: str = <default>  💡 标签名
            - color: str = <default> 💡 标签颜色，支持 css 颜色语法
            - sort: int = <default>  💡 序号
        """
        api = complete_url("/label/edit", base_url=base_url, app=app)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_label_files(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_label_files(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_label_files(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列标签的文件列表

        GET https://webapi.115.com/label/files

        :payload:
            - label_id: int
            - offset: 0
            - limit: int = 1150

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
            - cid: int | str = 0 💡 目录 id
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
        api = complete_url("/label/files", base_url=base_url)
        if not isinstance(payload, dict):
            payload = {"label_id": payload}
        payload = {"offset": 0, "limit": 1150, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_label_list(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_label_list(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_label_list(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列标签列表（如果要获取做了标签的文件列表，用 `fs_search` 接口）

        GET https://webapi.115.com/label/list

        :payload:
            - offset: int = 0 💡 索引偏移，从 0 开始
            - limit: int = 11500 💡 最多返回数量
            - keyword: str = <default> 💡 搜索关键词
            - sort: "name" | "update_time" | "create_time" = <default> 💡 排序字段

                - 名称: "name"
                - 添加时间: "create_time"
                - 修改时间: "update_time"

            - order: "asc" | "desc" = <default> 💡 排序顺序："asc"(升序), "desc"(降序)
            - count_file: 0 | 1 = <default>
        """
        api = complete_url("/label/list", base_url=base_url)
        if isinstance(payload, str):
            payload = {"keyword": payload}
        payload = {"offset": 0, "limit": 11500, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_label_list_app(
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
    def fs_label_list_app(
        self,
        payload: str | dict = "",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_label_list_app(
        self,
        payload: str | dict = "",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列标签列表（如果要获取做了标签的文件列表，用 `fs_search` 接口）

        GET https://proapi.115.com/{app}/label/list

        :payload:
            - offset: int = 0 💡 索引偏移，从 0 开始
            - limit: int = 11500 💡 最多返回数量
            - keyword: str = <default> 💡 搜索关键词
            - sort: "name" | "update_time" | "create_time" = <default> 💡 排序字段

                - 名称: "name"
                - 创建时间: "create_time"
                - 更新时间: "update_time"

            - order: "asc" | "desc" = <default> 💡 排序顺序："asc"(升序), "desc"(降序)
        """
        api = complete_url("/label/list", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"keyword": payload}
        payload = {"offset": 0, "limit": 11500, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_label_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        label: int | str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_label_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        label: int | str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_label_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        label: int | str = "",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """为文件或目录设置标签，此接口是对 `fs_edit` 的封装

        .. attention::
            这个接口会把标签列表进行替换，而不是追加

        .. hint::
            为单个文件或目录，设置一个不存在的标签 id，比如 1，会清空标签，但可产生事件（批量设置时无事件，可能是 bug）

            .. code:: python

                client.fs_label_set(id, 1)
        """
        return self._fs_edit_set(
            payload,
            "file_label",
            default=label,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def fs_label_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        label: int | str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_label_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        label: int | str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_label_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        label: int | str = "",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """为文件或目录设置标签，此接口是对 `fs_files_update_app` 的封装

        .. attention::
            这个接口会把标签列表进行替换，而不是追加
        """
        return self._fs_edit_set_app(
            payload,
            "file_label",
            default=label,
            app=app,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def fs_label_batch(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_label_batch(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_label_batch(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量设置标签

        POST https://webapi.115.com/files/batch_label

        :payload:
            - action: "add" | "remove" | "reset" | "replace" 💡 操作名

                - "add": 添加
                - "remove": 移除
                - "reset": 重设
                - "replace": 替换

            - file_ids: int | str 💡 文件或目录 id，多个用逗号 "," 隔开
            - file_label: int | str = <default> 💡 标签 id，多个用逗号 "," 隔开
            - file_label[{file_label}]: int | str = <default> 💡 action 为 replace 时使用此参数，file_label[{原标签id}]: {目标标签id}，例如 file_label[123]: 456，就是把 id 是 123 的标签替换为 id 是 456 的标签
        """
        api = complete_url("/files/batch_label", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_label_batch_app(
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
    def fs_label_batch_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_label_batch_app(
        self,
        payload: dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量设置标签

        POST https://proapi.115.com/{app}/files/batch_label

        :payload:
            - action: "add" | "remove" | "reset" | "replace" 💡 操作名

                - "add": 添加
                - "remove": 移除
                - "reset": 重设
                - "replace": 替换

            - file_ids: int | str 💡 文件或目录 id，多个用逗号 "," 隔开
            - file_label: int | str = <default> 💡 标签 id，多个用逗号 "," 隔开
            - file_label[{file_label}]: int | str = <default> 💡 action 为 replace 时使用此参数，file_label[{原标签id}]: {目标标签id}，例如 file_label[123]: 456，就是把 id 是 123 的标签替换为 id 是 456 的标签
        """
        api = complete_url("/files/batch_label", base_url=base_url, app=app)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_makedirs(
        self,
        payload: str | dict,
        /,
        pid: int | str = 0,
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_makedirs(
        self,
        payload: str | dict,
        /,
        pid: int | str = 0,
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_makedirs(
        self,
        payload: str | dict,
        /,
        pid: int | str = 0,
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """新建目录（会尝试创建所有的中间节点）

        .. note::
            0. 此接口是对 ``fs_dir_getid2`` 的封装
            1. 目录层级最多 25 级（不算文件节点的话）
            2. 名字不能包含 3 个字符之一 "<>，如果包含，则会被替换为 _
            3. 单个目录内最多 5 万个文件（用网页上传、创建 Office 文档此限制）

        .. attention::
            这个方法并不产生 115 生活的操作事件

        :payload:
            - path: str
            - parent_id: int | str = 0
        """
        if isinstance(payload, str):
            payload = {"path": payload}
        payload.setdefault("parent_id", pid)
        payload["is_create"] = 1
        return self.fs_dir_getid2(payload, async_=async_, **request_kwargs)

    @overload
    def fs_makedirs_app(
        self,
        payload: str | dict,
        /,
        pid: int | str = 0,
        app: str = "chrome",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_makedirs_app(
        self,
        payload: str | dict,
        /,
        pid: int | str = 0,
        app: str = "chrome",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_makedirs_app(
        self,
        payload: str | dict,
        /,
        pid: int | str = 0,
        app: str = "chrome",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """新建目录（会尝试创建所有的中间节点）

        POST https://proapi.115.com/app/chrome/add_path

        .. note::
            1. 目录层级最多 25 级（不算文件节点的话）
            2. 名字不能包含 3 个字符之一 "<>，如果包含，则会被替换为 _
            3. 单个目录内最多 5 万个文件（用网页上传、创建 Office 文档此限制）

        .. attention::
            这个方法并不产生 115 生活的操作事件

        :payload:
            - path: str
            - parent_id: int | str = 0
        """
        if app in ("", "chrome"):
            api = complete_url("/app/chrome/add_path", base_url)
        else:
            api = complete_url("/2.0/ufile/add_path", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"path": payload}
        payload.setdefault("parent_id", pid)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_mkdir(
        self,
        payload: str | dict,
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
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
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_mkdir(
        self,
        payload: str | dict,
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """新建目录

        POST https://webapi.115.com/files/add

        .. note::
            1. 目录层级最多 25 级（不算文件节点的话）
            2. 名字不能包含 3 个字符之一 "<>，但是文件可以通过上传来突破此限制
            3. 单个目录内最多 5 万个文件（用网页上传、创建 Office 文档此限制）

        :payload:
            - cname: str         💡 新建目录名称，限制 255 个字符
            - pid: int | str = 0 💡 上级目录的 id
        """
        api = complete_url("/files/add", base_url=base_url)
        if isinstance(payload, str):
            payload = {"cname": payload}
        payload.setdefault("pid", pid)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_mkdir_app(
        self,
        payload: dict | str,
        /,
        pid: int | str = 0,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_mkdir_app(
        self,
        payload: dict | str,
        /,
        pid: int | str = 0,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_mkdir_app(
        self,
        payload: dict | str,
        /,
        pid: int | str = 0,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """新建目录，此接口是对 `fs_folder_update_app` 的封装

        :payload:
            - name: str          💡 新建目录名称，限制 255 个字符
            - pid: int | str = 0 💡 上级目录的 id
        """
        if isinstance(payload, str):
            payload = {"name": payload}
        payload.setdefault("pid", pid)
        return self.fs_folder_update_app(
            payload,
            app=app,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def fs_move(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_move(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_move(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """移动文件或目录

        POST https://webapi.115.com/files/move

        .. caution::
            ⚠️ 请不要并发执行，限制在 5 万个文件和目录以内

        .. caution::
            你可以把文件或目录移动到其它目录 id 下，即使是不存在的 id

            因此，我定义了一个概念，悬空节点，此节点的 aid=1，但它有一个祖先节点，要么不存在，要么 aid != 1

            你可以用 ``P115Client.tool_space()`` 方法，使用【校验空间】功能，把所有悬空节点找出来，放到根目录下的【修复文件】目录，此接口一天只能用一次

        :payload:
            - fid: int | str 💡 文件或目录 id，只接受单个 id
            - fid[]: int | str
            - ...
            - fid[0]: int | str
            - fid[1]: int | str
            - ...
            - pid: int | str = 0 💡 目标目录 id
            - move_proid: str = <default> 💡 任务 id
            - conflict_policy: str = <default>
        """
        api = complete_url("/files/move", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"fid": payload}
        elif not isinstance(payload, dict):
            payload = {f"fid[{i}]": fid for i, fid in enumerate(payload)}
        payload.setdefault("pid", pid)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_move_app(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_move_app(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_move_app(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """移动文件或目录

        POST https://proapi.115.com/{app}/files/move

        .. caution::
            ⚠️ 请不要并发执行，限制在 5 万个文件和目录以内

        :payload:
            - ids: int | str    💡 文件或目录 id，多个用逗号 "," 隔开
            - to_cid: int | str 💡 目标目录 id
            - user_id: int | str = <default> 💡 用户 id
        """
        api = complete_url("/files/move", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"ids": payload}
        elif not isinstance(payload, dict):
            payload = {"ids": ",".join(map(str, payload))}
        payload = {"to_cid": pid, "user_id": self.user_id, **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_move_check_conflict(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_move_check_conflict(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_move_check_conflict(
        self,
        payload: int | str | dict | Iterable[int | str],
        /,
        pid: int | str = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """检查移动文件或目录时，是否有冲突

        POST https://webapi.115.com/files/move_check_conflict

        :payload:
            - move_fids: int | str 💡 文件或目录 id，只接受单个 id
            - move_fids[]: int | str
            - ...
            - move_fids[0]: int | str
            - move_fids[1]: int | str
            - ...
            - pid: int | str = 0 💡 目标目录 id
        """
        api = complete_url("/files/move_check_conflict", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"move_fids": payload}
        elif not isinstance(payload, dict):
            payload = {f"move_fids[{i}]": fid for i, fid in enumerate(payload)}
        payload.setdefault("pid", pid)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_move_progress(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_move_progress(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_move_progress(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """移动任务的进度

        GET https://webapi.115.com/files/move_progress

        :payload:
            - move_proid: str = <default> 💡 任务 id
        """
        api = complete_url("/files/move_progress", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"move_proid": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取音乐信息（其实只有一个下载链接）

        GET https://webapi.115.com/files/music

        :payload:
            - pickcode: str 💡 提取码
            - topic_id: int = <default>
            - music_id: int = <default>
            - download: int = <default>
            - platform: str = <default> 💡 如果取值为 "weixin"，则会多一个字段 "audio_url"
            - share_id: int | str = 0
        """
        api = complete_url("/files/music", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        request_kwargs.setdefault("follow_redirects", False)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_app(
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
    def fs_music_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取音乐信息

        GET https://proapi.115.com/{app}/music/musicplay

        .. note::
            即使文件格式不正确或者过大（超过 200 MB），也可返回一些信息（包括 parent_id），但如果是目录则信息匮乏（但由此也可判定一个目录）

        :payload:
            - pickcode: str 💡 提取码
            - music_id: int = <default>
            - topic_id: int = <default>
        """
        api = complete_url("/music/musicplay", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_file_exist(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_file_exist(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_file_exist(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """检查音乐文件是否存在

        GET https://webapi.115.com/files/music_file_exist

        :payload:
            - pickcode: str 💡 提取码
            - topic_id: int = <default>
            - music_id: int = <default>
            - download: int = <default>
        """
        api = complete_url("/files/music_file_exist", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_fond_list(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_fond_list(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_fond_list(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列星标听单

        GET https://webapi.115.com/files/music_fond_list
        """
        api = complete_url("/files/music_fond_list", base_url=base_url)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def fs_music_fond_list_app(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_fond_list_app(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_fond_list_app(
        self,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列星标听单

        GET https://proapi.115.com/{app}/music/music_fond_list
        """
        api = complete_url("/music/music_fond_list", base_url=base_url, app=app)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def fs_music_fond_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_fond_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_fond_set(
        self,
        payload: int | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """给听单加减星标

        POST https://webapi.115.com/files/music_topic_fond

        :payload:
            - topic_id: int
            - fond: 0 | 1 = 1
        """
        api = complete_url("/files/music_topic_fond", base_url=base_url)
        if isinstance(payload, int):
            payload = {"topic_id": payload}
        payload.setdefault("fond", 1)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_music_include_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_include_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_include_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """包含音乐的目录列表（专属文件）

        GET https://webapi.115.com/files/include_music_list

        :payload:
            - asc: 0 | 1 = 0
            - limit: int = 1150
            - offset: int = 0
            - order: str = "user_etime"
        """
        api = complete_url("/files/include_music_list", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload = {"asc": 0, "limit": 1150, "order": "user_etime", **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_include_list_app(
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
    def fs_music_include_list_app(
        self,
        payload: int | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_include_list_app(
        self,
        payload: int | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """包含音乐的目录列表（专属文件）

        GET https://proapi.115.com/{app}/music/include_music_list

        :payload:
            - asc: 0 | 1 = 0
            - limit: int = 1150
            - offset: int = 0
            - order: str = "user_etime"
        """
        api = complete_url("/music/include_music_list", base_url=base_url, app=app)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload = {"asc": 0, "limit": 1150, "order": "user_etime", **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_info(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_info(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_info(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取音乐封面等信息

        GET https://webapi.115.com/files/music_info

        :payload:
            - pickcode: str 💡 提取码
        """
        api = complete_url("/files/music_info", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_info_app(
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
    def fs_music_info_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_info_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取音乐封面等信息

        GET https://proapi.115.com/{app}/music/musicdetail

        :payload:
            - pickcode: str 💡 提取码
        """
        api = complete_url("/music/musicdetail", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_list(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_list(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_list(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列听单中的文件

        GET https://webapi.115.com/files/music_list

        :payload:
            - topic_id: int = 1 💡 听单 id。-1:星标 1:最近听过 2:最近接收
            - start: int = 0
            - limit: int = 1150
        """
        api = complete_url("/files/music_list", base_url=base_url)
        if isinstance(payload, int):
            payload = {"topic_id": payload}
        payload = {"start": 0, "limit": 1150, "topic_id": 1, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_list_app(
        self,
        payload: int | dict = 1,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_list_app(
        self,
        payload: int | dict = 1,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_list_app(
        self,
        payload: int | dict = 1,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列听单中的文件

        GET https://proapi.115.com/{app}/music/music_list

        :payload:
            - topic_id: int = 1 💡 听单 id。-1:星标 1:最近听过 2:最近接收
            - start: int = 0
            - limit: int = 1150
        """
        api = complete_url("/music/music_list", base_url=base_url, app=app)
        if isinstance(payload, int):
            payload = {"topic_id": payload}
        payload = {"start": 0, "limit": 1150, "topic_id": 1, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_new(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_new(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_new(
        self,
        payload: int | dict = 1,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列听单或听单中的文件

        GET https://webapi.115.com/files/musicnew

        :payload:
            - topic_id: int = 1 💡 听单 id。-1:星标 1:最近听过 2:最近接收
            - type: 0 | 1 = 0   💡 类型：0:文件 1:目录
            - start: int = 0
            - limit: int = 1150
        """
        api = complete_url("/files/musicnew", base_url=base_url)
        if isinstance(payload, int):
            payload = {"topic_id": payload}
        payload = {"start": 0, "limit": 1150, "type": 0, "topic_id": 1, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_new_app(
        self,
        payload: int | dict = 1,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_new_app(
        self,
        payload: int | dict = 1,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_new_app(
        self,
        payload: int | dict = 1,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列听单或听单中的文件

        GET https://proapi.115.com/{app}/music/musicnew

        :payload:
            - topic_id: int = 1 💡 听单 id。-1:星标 1:最近听过 2:最近接收
            - type: 0 | 1 = 0   💡 类型：0:文件 1:目录
        """
        api = complete_url("/music/musicnew", base_url=base_url, app=app)
        if isinstance(payload, int):
            payload = {"topic_id": payload}
        payload = {"type": 0, "topic_id": 1, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """从听单添加或移除音乐，或者给音乐加减星标

        POST https://webapi.115.com/files/music

        .. caution::
            文件超过500MB，暂不支持添加到我听

        :payload:
            - file_id: int      💡 文件 id，多个用逗号 "," 隔开（op 为 "add" 和 "delete" 时需要）
            - music_id: int = 1 💡 音乐 id（op 为 "fond" 时需要）
            - topic_id: int = 1 💡 听单 id，默认为【最近听过】
            - op: str = "add"   💡 操作类型："add": 添加到听单, "delete": 从听单删除, "fond": 设置星标
            - fond: 0 | 1 = 1   💡 是否星标（op 为 "fond" 时需要），这个星标和 music_id 有关，和 file_id 无关
        """
        api = complete_url("/files/music", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        elif not isinstance(payload, dict):
            payload = {"file_id": ",".join(map(str, payload))}
        payload = {"op": "add", "fond": 1, "music_id": 1, "topic_id": 1, **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_music_status(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_status(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_status(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """音乐状态

        GET https://webapi.115.com/files/music_status

        :payload:
            - pickcode: str 💡 提取码
        """
        api = complete_url("/files/music_status", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_topic_listnew(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_topic_listnew(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_topic_listnew(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列听单

        GET https://webapi.115.com/files/music_topic_listnew

        .. caution::
            似乎查询参数并没有效果

        :payload:
            - fond: 0 | 1 = 0   💡 是否星标
            - start: int = 0    💡 开始索引
            - limit: int = 1150 💡 最多返回数量
            - hidden: 0 | 1 = 0
        """
        api = complete_url("/files/music_topic_listnew", base_url=base_url)
        if isinstance(payload, int):
            payload = {"start": payload}
        payload = {"fond": 0, "hidden": 0, "limit": 1150, "start": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_topic_listnew_app(
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
    def fs_music_topic_listnew_app(
        self,
        payload: int | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_topic_listnew_app(
        self,
        payload: int | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列听单

        GET https://proapi.115.com/{app}/music/musiclistnew

        .. caution::
            似乎查询参数并没有效果

        :payload:
            - fond: 0 | 1 = 0   💡 是否星标
            - start: int = 0    💡 开始索引
            - limit: int = 1150 💡 最多返回数量
        """
        api = complete_url("/music/musiclistnew", base_url=base_url, app=app)
        if isinstance(payload, int):
            payload = {"start": payload}
        payload = {"fond": 0, "limit": 1150, "start": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_music_topic_set(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_music_topic_set(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_music_topic_set(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """修改听单

        POST https://webapi.115.com/files/music_topic

        :payload:
            - op: "edit" | "delete" | "add" 💡 操作类型："edit":改名 "delete":删除 "add":添加
            - topic_id: int = <default> 💡 听单 id（op 不为 "add" 时需要）
            - topic_name: str = <default> 💡 听单名字（op 为 "add" 和 "edit" 时需要）
        """
        api = complete_url("/files/music_topic", base_url=base_url)
        if isinstance(payload, str):
            payload = {"op": "add", "topic_name": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_office_check_complete(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_office_check_complete(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_office_check_complete(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """检查 office 保存任务完成情况

        POST https://webapi.115.com/files/office?act=check_complete

        :payload:
            - office_id: int | str
        """
        api = complete_url(
            "/files/office", base_url=base_url, query={"act": "check_complete"}
        )
        if isinstance(payload, (int, str)):
            payload = {"office_id": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_office_init(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_office_init(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_office_init(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """初始化 office

        POST https://webapi.115.com/files/office?act=office_init

        :payload:
            - pickcode: str
        """
        api = complete_url(
            "/files/office", base_url=base_url, query={"act": "office_init"}
        )
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_office_save(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_office_save(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_office_save(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """保存 office，即提交一个 office 的保存任务

        POST https://webapi.115.com/files/office?act=save

        .. todo::
            临时数据需要经过 AES-128 加密，并用 WPS 的（类似如下）接口提交，以后等需要用到了再进行破解

            https://kmon.kdocs.cn/api/relay/store/57QKSwAPhwr/log

        .. caution::
            用 office 来编辑文件，可以在 id 不变的情况下，修改文件数据，打破了文件一旦上传完成，内容就不会改变的固有认知

        :payload:
            - office_id: int | str
        """
        api = complete_url("/files/office", base_url=base_url, query={"act": "save"})
        if isinstance(payload, (int, str)):
            payload = {"office_id": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_order_set(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_order_set(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_order_set(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置某个目录内文件的默认排序

        POST https://webapi.115.com/files/order

        :payload:
            - user_order: str 💡 用某字段排序

                - "file_name": 文件名
                - "file_size": 文件大小
                - "file_type": 文件种类
                - "user_utime": 修改时间
                - "user_ptime": 创建时间
                - "user_otime": 上一次打开时间

            - file_id: int | str = 0 💡 目录 id，对应 parent_id
            - user_asc: 0 | 1 = <default> 💡 是否升序排列
            - fc_mix: 0 | 1 = <default> 💡 是否目录和文件混合，如果为 0 则目录在前（目录置顶）
            - module: str = <default> 💡 "label_search" 表示用于搜索的排序
        """
        api = complete_url("/files/order", base_url=base_url)
        if isinstance(payload, str):
            payload = {"user_order": payload}
        payload = {"file_id": 0, "user_asc": 1, "user_order": "user_ptime", **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_order_set_app(
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
    def fs_order_set_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_order_set_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置某个目录内文件的默认排序

        POST https://proapi.115.com/{app}/2.0/ufile/order

        .. error::
            这个接口暂时并不能正常工作，应该是参数构造有问题，暂时请用 ``P115Client.fs_order_set()``

        :payload:
            - user_order: str 💡 用某字段排序

                - "file_name": 文件名
                - "file_size": 文件大小
                - "file_type": 文件种类
                - "user_utime": 修改时间
                - "user_ptime": 创建时间
                - "user_otime": 上一次打开时间

            - file_id: int | str = 0 💡 目录 id，对应 parent_id
            - user_asc: 0 | 1 = <default> 💡 是否升序排列
            - fc_mix: 0 | 1 = <default> 💡 是否目录和文件混合，如果为 0 则目录在前（目录置顶）
            - module: str = <default> 💡 "label_search" 表示用于搜索的排序
        """
        api = complete_url("/2.0/ufile/order", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"user_order": payload}
        payload = {"file_id": 0, "user_asc": 1, "user_order": "user_ptime", **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_preview(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_preview(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_preview(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """文档预览

        POST  https://webapi.115.com/files/preview

        :payload:
            - pickcode: str 💡 提取码
            - share_id: int | str = <default>
        """
        api = complete_url("/files/preview", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_rename(
        self,
        payload: tuple[int | str, str] | dict | Iterable[tuple[int | str, str]],
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_rename(
        self,
        payload: tuple[int | str, str] | dict | Iterable[tuple[int | str, str]],
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_rename(
        self,
        payload: tuple[int | str, str] | dict | Iterable[tuple[int | str, str]],
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """重命名文件或目录

        POST https://webapi.115.com/files/batch_rename

        .. caution::
            改名时，虽然不能修改扩展名，但是一定要带上扩展名（无论是啥），不然会把最后一个句点 . 及其之后文字截断

        :payload:
            - files_new_name[{file_id}]: str 💡 值为新的文件名（basename）
        """
        api = complete_url("/files/batch_rename", base_url=base_url)
        if (
            isinstance(payload, tuple)
            and len(payload) == 2
            and isinstance(payload[0], (int, str))
        ):
            payload = {f"files_new_name[{payload[0]}]": payload[1]}
        elif not isinstance(payload, dict):
            payload = {f"files_new_name[{fid}]": name for fid, name in payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_rename_app(
        self,
        payload: tuple[int | str, str] | dict | Iterable[tuple[int | str, str]],
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_rename_app(
        self,
        payload: tuple[int | str, str] | dict | Iterable[tuple[int | str, str]],
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_rename_app(
        self,
        payload: tuple[int | str, str] | dict | Iterable[tuple[int | str, str]],
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """重命名文件或目录

        POST https://proapi.115.com/{app}/files/batch_rename

        .. caution::
            改名时，虽然不能修改扩展名，但是一定要带上扩展名（无论是啥），不然会把最后一个句点 . 及其之后文字截断

        :payload:
            - files_new_name[{file_id}]: str 💡 值为新的文件名（basename）
        """
        api = complete_url("/files/batch_rename", base_url=base_url, app=app)
        if (
            isinstance(payload, tuple)
            and len(payload) == 2
            and isinstance(payload[0], (int, str))
        ):
            payload = {f"files_new_name[{payload[0]}]": payload[1]}
        elif not isinstance(payload, dict):
            payload = {f"files_new_name[{fid}]": name for fid, name in payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_rename_set_names(
        self,
        payload: dict | list[tuple[str, str | int]],
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_rename_set_names(
        self,
        payload: dict | list[tuple[str, str | int]],
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_rename_set_names(
        self,
        payload: dict | list[tuple[str, str | int]],
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """提交模拟批量重命名请求（提示：较为复杂，自己抓包研究）

        POST https://aps.115.com/rename/set_names.php
        """
        api = complete_url("/rename/set_names.php", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_rename_reset_names(
        self,
        payload: dict | list[tuple[str, str | int]],
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_rename_reset_names(
        self,
        payload: dict | list[tuple[str, str | int]],
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_rename_reset_names(
        self,
        payload: dict | list[tuple[str, str | int]],
        /,
        base_url: str | Callable[[], str] = "https://aps.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取批量重命名的模拟结果（提示：较为复杂，自己抓包研究）

        POST https://aps.115.com/rename/reset_names.php
        """
        api = complete_url("/rename/reset_names.php", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_repeat_sha1(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_repeat_sha1(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_repeat_sha1(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """查找重复文件（罗列除此以外的 sha1 相同的文件）

        GET https://webapi.115.com/files/get_repeat_sha

        :payload:
            - file_id: int | str
            - offset: int = 0
            - limit: int = 1150
            - source: str = ""
        """
        api = complete_url("/files/get_repeat_sha", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        payload = {"offset": 0, "limit": 1150, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_repeat_sha1_app(
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
    def fs_repeat_sha1_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_repeat_sha1_app(
        self,
        payload: int | str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """查找重复文件（罗列除此以外的 sha1 相同的文件）

        GET https://proapi.115.com/{app}/2.0/ufile/get_repeat_sha

        :payload:
            - file_id: int | str
            - offset: int = 0
            - limit: int = 1150
            - source: str = ""
        """
        api = complete_url("/2.0/ufile/get_repeat_sha", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload}
        payload = {"offset": 0, "limit": 1150, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_score_set(
        self,
        file_id: int | str | Iterable[int | str],
        /,
        score: int = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_score_set(
        self,
        file_id: int | str | Iterable[int | str],
        /,
        score: int = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_score_set(
        self,
        file_id: int | str | Iterable[int | str],
        /,
        score: int = 0,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """给文件或目录评分

        POST https://webapi.115.com/files/score

        :payload:
            - file_id: int | str   💡 文件或目录 id，多个用逗号 "," 隔开
            - score: int | str = 0 💡 任意整数，<= 0 时网页上不会显示星星，如果是字符串，会尝试解析为整数，失败的话得到 0
        """
        api = complete_url("/files/score", base_url=base_url)
        if not isinstance(file_id, (int, str)):
            file_id = ",".join(map(str, file_id))
        payload = {"file_id": file_id, "score": score}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_search(
        self,
        payload: str | dict = ".",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_search(
        self,
        payload: str | dict = ".",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_search(
        self,
        payload: str | dict = ".",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """搜索文件或目录

        GET https://webapi.115.com/files/search

        .. attention::
            最多只能取回前 10,000 条数据，也就是 `limit + offset <= 10_000`，不过可以一次性取完

            不过就算正确设置了 `limit` 和 `offset`，并且总数据量大于 `limit + offset`，可能也不足 `limit`，这应该是 bug，也就是说，就算数据总量足够你也取不到足量

            它返回数据中的 `count` 字段的值表示总数据量（即使你只能取前 10,000 条），往往并不准确，最多能当作一个可参考的估计值

            这个接口实际上不支持在查询中直接设置排序，只能由 ``P115Client.fs_order_set()`` 设置

        .. note::
            搜索接口甚至可以把上级 id 关联错误的文件或目录都搜索出来。一般是因为把文件或目录移动到了一个不存在的 id 下，你可以用某些关键词把他们搜索出来，然后移动到一个存在的目录中，就可以恢复他们了，或者使用 ``P115Client.tool_space()`` 接口来批量恢复

        .. important::
            一般使用的话，要提供 "search_value" 或 "file_label"，不然返回数据里面看不到任何一条数据，即使你指定了其它参数

            下面指定的很多参数其实是一点效果都没有的，具体可以实际验证

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
            - cid: int | str = 0 💡 目录 id，对应 parent_id
            - count_folders: 0 | 1 = <default> 💡 是否统计目录数，这样就会增加 "folder_count" 和 "file_count" 字段作为统计
            - date: str = <default> 💡 筛选日期，格式为 YYYY-MM-DD（或者 YYYY-MM 或者 YYYY 或者 时间戳（限定在当天）），最小单位是天，其次是月，具体可以看文件信息中的 "t" 字段的值
            - distance: int | str = <default>
            - fc: 0 | 1 = <default> 💡 只显示文件或目录。1:只显示目录 2:只显示文件
            - fc_mix: 0 | 1 = <default> 💡 是否目录和文件混合，如果为 0 则目录在前（目录置顶）
            - file_label: int | str = <default> 💡 标签 id
            - gte_day: str 💡 搜索结果匹配的开始时间；格式：YYYY-MM-DD
            - limit: int = 32 💡 一页大小，意思就是 page_size
            - location: str = <default>
            - lte_day: str 💡 搜索结果匹配的结束时间；格式：YYYY-MM-DD
            - natsort: 0 | 1 = <default> 💡 是否执行自然排序(natural sorting)
            - nf: 0 | 1 = <default> 💡 不要显示文件（即仅显示目录）
            - o: str = <default> 💡 用某字段排序

                - "file_name": 文件名
                - "file_size": 文件大小
                - "file_type": 文件种类
                - "user_utime": 修改时间
                - "user_ptime": 创建时间
                - "user_otime": 上一次打开时间

            - offset: int = 0  💡 索引偏移，索引从 0 开始计算
            - qid: int | str = <default>
            - resp_ver: int | str = <default>
            - search_value: str = "." 💡 搜索文本，可以是 sha1
            - show_dir: 0 | 1 = 1 💡 是否显示目录
            - source: str = <default> 💡 来源
            - star: 0 | 1 = <default> 💡 是否打星标
            - stdir: 0 | 1 = <default> 💡 筛选文件时，是否显示目录：1:展示 0:不展示
            - suffix: str = <default> 💡 文件后缀（扩展名），优先级高于 `type`
            - type: int = <default>   💡 文件类型

                - 0: 全部（仅当前目录）
                - 1: 文档
                - 2: 图片
                - 3: 音频
                - 4: 视频
                - 5: 压缩包
                - 6: 软件/应用
                - 7: 书籍
                - 99: 所有文件
        """
        api = complete_url("/files/search", base_url=base_url)
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
    def fs_search_app(
        self,
        payload: str | dict = ".",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_search_app(
        self,
        payload: str | dict = ".",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_search_app(
        self,
        payload: str | dict = ".",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """搜索文件或目录

        GET https://proapi.115.com/{app}/2.0/ufile/search

        .. attention::
            最多只能取回前 10,000 条数据，也就是 `limit + offset <= 10_000`，不过可以一次性取完

            不过就算正确设置了 `limit` 和 `offset`，并且总数据量大于 `limit + offset`，可能也不足 `limit`，这应该是 bug，也就是说，就算数据总量足够你也取不到足量

            它返回数据中的 `count` 字段的值表示总数据量（即使你只能取前 10,000 条），往往并不准确，最多能当作一个可参考的估计值

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
            - date: str = <default> 💡 筛选日期，格式为 YYYY-MM-DD（或者 YYYY-MM 或者 YYYY 或者 时间戳（限定在当天）），最小单位是天，其次是月，具体可以看文件信息中的 "t" 字段的值
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
        api = complete_url("/2.0/ufile/search", base_url=base_url, app=app)
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
    def fs_search_app2(
        self,
        payload: str | dict = ".",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_search_app2(
        self,
        payload: str | dict = ".",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_search_app2(
        self,
        payload: str | dict = ".",
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """搜索文件或目录

        GET https://proapi.115.com/{app}/files/search

        .. attention::
            最多只能取回前 10,000 条数据，也就是 `limit + offset <= 10_000`，不过可以一次性取完

            不过就算正确设置了 `limit` 和 `offset`，并且总数据量大于 `limit + offset`，可能也不足 `limit`，这应该是 bug，也就是说，就算数据总量足够你也取不到足量

            它返回数据中的 `count` 字段的值表示总数据量（即使你只能取前 10,000 条），往往并不准确，最多能当作一个可参考的估计值

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
            - date: str = <default> 💡 筛选日期，格式为 YYYY-MM-DD（或者 YYYY-MM 或者 YYYY 或者 时间戳（限定在当天）），最小单位是天，其次是月，具体可以看文件信息中的 "t" 字段的值
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
        api = complete_url("/files/search", base_url=base_url, app=app)
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
    def fs_shasearch(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_shasearch(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_shasearch(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """通过 sha1 搜索文件

        GET https://webapi.115.com/files/shasearch

        .. note::
            这是个非常早期的接口，高级功能请直接使用 `client.fs_search`。这个方法最多只能获得一条记录，并且不支持指定搜索目录，而且当未搜索到时，返回的信息为 '{"state": false, "error": "文件错误"}'

        :payload:
            - sha1: str
        """
        api = complete_url("/files/shasearch", base_url=base_url)
        if isinstance(payload, str):
            payload = {"sha1": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_show_play_long_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        show: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_show_play_long_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        show: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_show_play_long_set(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        show: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """为目录设置显示时长，此接口是对 `fs_edit` 的封装"""
        return self._fs_edit_set(
            payload,
            "show_play_long",
            default=int(show),
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def fs_show_play_long_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        show: bool = True,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_show_play_long_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        show: bool = True,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_show_play_long_set_app(
        self,
        payload: int | str | Iterable[int | str] | list[tuple] | dict,
        /,
        show: bool = True,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """为目录设置显示时长，此接口是对 `fs_files_update_app` 的封装"""
        return self._fs_edit_set_app(
            payload,
            "show_play_long",
            default=int(show),
            app=app,
            base_url=base_url,
            async_=async_,
            **request_kwargs,
        )

    @overload
    def fs_space_report(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_space_report(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_space_report(
        self,
        payload: str | dict = "",
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取数据报告（截至月末数据，分组聚合）

        GET https://webapi.115.com/user/report

        :payload:
            - month: str 💡 年月，格式为 YYYYMM
        """
        api = complete_url("/user/report", base_url=base_url)
        if not payload:
            now = datetime.now()
            year, month = now.year, now.month
            if month == 1:
                ym = f"{year - 1}12"
            else:
                ym = f"{year}{month - 1:02d}"
            payload = {"month": ym}
        elif isinstance(payload, str):
            payload = {"month": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_space_summury(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_space_summury(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_space_summury(
        self,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取数据报告（当前数据，分组聚合，但并不精确）

        POST https://webapi.115.com/user/space_summury
        """
        api = complete_url("/user/space_summury", base_url=base_url)
        return self.request(url=api, method="POST", async_=async_, **request_kwargs)

    @overload
    def fs_star_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        star: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
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
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_star_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        star: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """为文件或目录设置或取消星标

        POST https://webapi.115.com/files/star

        .. note::
            如果其中任何一个 id 目前已经被删除，则会直接返回错误信息

        :payload:
            - file_id: int | str 💡 文件或目录 id，多个用逗号 "," 隔开
            - star: 0 | 1 = 1
        """
        api = complete_url("/files/star", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload, "star": int(star)}
        elif not isinstance(payload, dict):
            payload = {"file_id": ",".join(map(str, payload)), "star": int(star)}
        else:
            payload = {"star": int(star), **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_star_set_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        star: bool = True,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_star_set_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        star: bool = True,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_star_set_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        star: bool = True,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """为文件或目录设置或取消星标

        POST https://proapi.115.com/{app}/files/star

        .. note::
            如果其中任何一个 id 目前已经被删除，则会直接返回错误信息

        :payload:
            - ids: int | str 💡 文件或目录 id，多个用逗号 "," 隔开
            - star: 0 | 1 = 1
            - user_id: int | str = <default> 💡 用户 id
        """
        api = complete_url("/files/star", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"ids": payload, "star": int(star)}
        elif not isinstance(payload, dict):
            payload = {"ids": ",".join(map(str, payload)), "star": int(star)}
        else:
            payload = {"star": int(star), **payload}
        payload["user_id"] = self.user_id
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_storage_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_storage_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_storage_info(
        self,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取使用空间的统计数据（最简略，如需更详细，请用 `fs.user_space_info()`）

        GET https://115.com/index.php?ct=ajax&ac=get_storage_info
        """
        api = complete_url(
            "/index.php",
            base_url=base_url,
            query={"ct": "ajax", "ac": "get_storage_info"},
        )
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def fs_supervision(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_supervision(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_supervision(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """通过 pickcode 获取文件信息

        POST https://webapi.115.com/files/supervision

        :payload:
            - pickcode: str
            - preview_type: str = "file" 💡 file:文件 doc:文档 video:视频 music:音乐 pic:图片
            - module: int = 10
            - share_id: int | str = <default>
        """
        api = complete_url("/files/supervision", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        payload = {"preview_type": "file", "module": 10, **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_supervision_app(
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
    def fs_supervision_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_supervision_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """通过 pickcode 获取文件信息

        POST https://proapi.115.com/{app}/files/supervision

        :payload:
            - pickcode: str
            - preview_type: str = "file" 💡 file:文件 doc:文档 video:视频 music:音乐 pic:图片
            - module: int = 10
            - share_id: int | str = <default>
        """
        api = complete_url("/files/supervision", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        payload = {"preview_type": "file", "module": 10, **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_sys_dir(
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
    def fs_sys_dir(
        self,
        payload: int | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_sys_dir(
        self,
        payload: int | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取系统目录（在根目录下，使用 `fs_files` 接口罗列时，数目体现在返回值的 `sys_count` 字段）

        GET https://proapi.115.com/{app}/files/getpackage

        :payload:
            - sys_dir: int 💡 0:最近接收 1:手机相册 2:云下载 3:我的时光记录 4,10,20,21,22,30,40,50,60,70:(未知)
        """
        api = complete_url("/files/getpackage", base_url=base_url, app=app)
        if isinstance(payload, int):
            payload = {"sys_dir": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_top_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        top: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_top_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        top: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_top_set(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        top: bool = True,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """文件或目录置顶

        POST https://webapi.115.com/files/top

        :payload:
            - file_id: int | str 💡 文件或目录的 id，多个用逗号 "," 隔开
            - top: 0 | 1 = 1
        """
        api = complete_url("/files/top", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"file_id": payload, "top": int(top)}
        elif not isinstance(payload, dict):
            payload = {"file_id": ",".join(map(str, payload)), "top": int(top)}
        else:
            payload = {"top": int(top), **payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_video(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_video(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_video(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取视频信息和 m3u8 链接列表

        GET https://webapi.115.com/files/video

        .. caution::
            `local` 在有些视频上不起作用，无论如何，都相当于 `local=0`，可能是因为文件超过 200 MB

            但如果 `local=1` 有效，则返回仅可得到下载链接，key 为 "download_url"

        .. note::
            如果返回信息中有 "queue_url"，则可用于查询转码状态

            如果视频从未被转码过，则会自动推送转码

        :payload:
            - pickcode: str 💡 提取码
            - share_id: int | str = <default> 💡 共享 id
            - local: 0 | 1 = <default> 💡 是否本地，如果为 1，则不包括 m3u8
        """
        api = complete_url("/files/video", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_video_app(
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
    def fs_video_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_video_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取视频信息和 m3u8 链接列表

        POST https://proapi.115.com/{app}/2.0/video/play

        :payload:
            - pickcode: str 💡 提取码
            - share_id: int | str = <default> 💡 共享 id
            - local: 0 | 1 = 0 💡 是否本地，如果为 1，则不包括 m3u8
            - user_id: int | str = <default> 💡 用户 id
        """
        api = complete_url("/2.0/video/play", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"pickcode": payload, "user_id": self.user_id}
        else:
            payload = dict(payload, user_id=self.user_id)

        def parse(_, content: bytes, /) -> dict:
            json = json_maybe_decrypt_loads(content)
            if json["state"] or json.get("errno") == 409:
                json["data"] = json_loads(_rsa_decrypt(json["data"]))
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
    def fs_video_add_caption_map(
        self,
        payload: dict | int | str,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_video_add_caption_map(
        self,
        payload: dict | int | str,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_video_add_caption_map(
        self,
        payload: dict | int | str,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """关联字幕

        POST https://webapi.115.com/movies/add_caption_map

        :payload:
            - file_ids: int | str 💡 多个用逗号 "," 隔开
            - type: int = 2
        """
        api = complete_url("/movies/add_caption_map", base_url=base_url)
        if not isinstance(payload, dict):
            payload = {"file_ids": payload}
        payload.setdefault("type", 2)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_video_def_set(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_video_def_set(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_video_def_set(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """切换视频清晰度

        POST https://webapi.115.com/files/video_def

        :payload:
            - definition: str
        """
        api = complete_url("/files/video_def", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"definition": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_video_is_transcode(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_video_is_transcode(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_video_is_transcode(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取视频的转码进度

        POST https://webapi.115.com/files/is_transcoded

        :payload:
            - pick_code: str
        """
        api = complete_url("/files/is_transcoded", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pick_code": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_video_m3u8(
        self,
        /,
        pickcode: str,
        definition: int = 0,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> bytes: ...

    @overload
    def fs_video_m3u8(
        self,
        /,
        pickcode: str,
        definition: int = 0,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, bytes]: ...

    def fs_video_m3u8(
        self,
        /,
        pickcode: str,
        definition: int = 0,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> bytes | Coroutine[Any, Any, bytes]:
        """获取视频的 m3u8 文件列表，此接口必须使用 web 的 cookies

        GET https://115.com/api/video/m3u8/{pickcode}.m3u8?definition={definition}

        .. attention::
            这个接口只支持 web 的 cookies，其它设备会返回空数据，而且获取得到的 m3u8 里的链接，也是 m3u8，会绑定前一次请求时的 user-agent

        :param pickcode: 视频文件的 pickcode
        :param definition: 画质，默认列出所有画质。但可进行筛选，常用的为：
            - 0: 各种分辨率（默认）
            - 1: SD 标清（约为 480p）
            - 3: HD 超清（约为 720p）
            - 4: UD 1080P（约为 1080p）
            - 5: BD 4K
            - 100: 原画（尺寸和原始的相同）
        :param async_: 是否异步
        :param request_kwargs: 其余请求参数

        :return: 接口返回值
        """
        api = complete_url(
            f"/api/video/m3u8/{pickcode}.m3u8",
            base_url=base_url,
            query={"definition": definition},
        )
        request_kwargs.setdefault("parse", False)
        return self.request(url=api, async_=async_, **request_kwargs)

    @overload
    def fs_video_multitrack_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_video_multitrack_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_video_multitrack_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置视频音轨

        POST https://webapi.115.com/movies/user_multitrack

        :payload:
            - pick_code: str
            - track_id: str
            - user_id: int = <default>
        """
        api = complete_url("/movies/user_multitrack", base_url=base_url)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_video_push(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_video_push(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_video_push(
        self,
        payload: dict | str,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """提交视频转码

        POST https://115.com/?ct=play&ac=push

        :payload:
            - pickcode: str
            - sha1: str = <default>
            - op: str = "vip_push" 💡 提交视频加速转码方式

                - "vip_push": 根据；vip 等级加速
                - "pay_push": 枫叶加速
        """
        api = complete_url(base_url=base_url, query={"ct": "play", "ac": "push"})
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        payload.setdefault("op", "vip_push")
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_video_push_batch(
        self,
        payload: dict | int | str,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_video_push_batch(
        self,
        payload: dict | int | str,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_video_push_batch(
        self,
        payload: dict | int | str,
        /,
        base_url: str | Callable[[], str] = "https://115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """提交视频转码

        POST https://115.com/?ctl=play&ac=batch_push

        :payload:
            - file_ids: int | str 💡 多个用逗号 "," 隔开
            - folder_ids: int | str 💡 多个用逗号 "," 隔开
        """
        api = complete_url(base_url=base_url, query={"ctl": "play", "ac": "batch_push"})
        if not isinstance(payload, dict):
            payload = {"file_ids": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_video_push_batch2(
        self,
        payload: dict | int | str,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_video_push_batch2(
        self,
        payload: dict | int | str,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_video_push_batch2(
        self,
        payload: dict | int | str,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """提交视频转码

        POST https://webapi.115.com/movies/batch_push

        :payload:
            - file_ids: int | str 💡 多个用逗号 "," 隔开
            - folder_ids: int | str 💡 多个用逗号 "," 隔开
        """
        api = complete_url("/movies/batch_push", base_url=base_url)
        if not isinstance(payload, dict):
            payload = {"file_ids": payload}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_video_subtitle(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_video_subtitle(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_video_subtitle(
        self,
        payload: str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取视频字幕

        GET https://webapi.115.com/movies/subtitle

        :payload:
            - pickcode: str
        """
        api = complete_url("/movies/subtitle", base_url=base_url)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_video_subtitle_app(
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
    def fs_video_subtitle_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_video_subtitle_app(
        self,
        payload: str | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取视频字幕

        GET https://proapi.115.com/{app}/2.0/video/subtitle

        :payload:
            - pickcode: str
        """
        api = complete_url("/2.0/video/subtitle", base_url=base_url, app=app)
        if isinstance(payload, str):
            payload = {"pickcode": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def fs_video_subtitle_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_video_subtitle_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_video_subtitle_set(
        self,
        payload: dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """设置视频字幕

        POST https://webapi.115.com/movies/user_subtitle

        :payload:
            - pick_code: str
            - sid: str 💡 字幕的 id，通过 ``P115Client.fs_video_subtitle()`` 接口获得
            - action: str = "set" 💡 操作："set":设置 "delete":删除
        """
        api = complete_url("/movies/user_subtitle", base_url=base_url)
        payload.setdefault("action", "set")
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def fs_video_transcode(
        self,
        payload: dict | str,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://transcode.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def fs_video_transcode(
        self,
        payload: dict | str,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://transcode.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def fs_video_transcode(
        self,
        payload: dict | str,
        /,
        app: str = "web",
        base_url: str | Callable[[], str] = "https://transcode.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取视频的转码进度

        GET https://transcode.115.com/api/1.0/{app}/1.0/trans_code/check_transcode_job

        :payload:
            - sha1: str
            - priority: int = 100 💡 优先级
        """
        api = complete_url(
            f"/api/1.0/{app}/1.0/trans_code/check_transcode_job", base_url=base_url
        )
        if isinstance(payload, str):
            payload = {"sha1": payload}
        payload.setdefault("priority", 100)
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def recyclebin_clean(
        self,
        payload: int | str | Iterable[int | str] | dict = "",
        /,
        password: str = "000000",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def recyclebin_clean(
        self,
        payload: int | str | Iterable[int | str] | dict = "",
        /,
        password: str = "000000",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def recyclebin_clean(
        self,
        payload: int | str | Iterable[int | str] | dict = "",
        /,
        password: str = "000000",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """回收站：删除或清空

        POST https://webapi.115.com/rb/secret_del

        .. note::
            只要不指定 `tid`，就会清空回收站，如果有目录正在删除中则会被阻止

        .. note::
            可以在设置中的【账号安全/安全密钥】页面下，关闭【文件(隐藏模式/清空删除回收站)】的按钮，就不需要传安全密钥了

        :payload:
            - tid: int | str = "" 💡 不传就是清空，多个用逗号 "," 隔开
            - password: int | str = "000000" 💡 安全密钥，是 6 位数字
        """
        api = complete_url("/rb/secret_del", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"tid": payload}
        elif not isinstance(payload, dict):
            payload = {"tid": ",".join(map(str, payload))}
        payload.setdefault("password", password)
        payload["password"] = format(payload.get("password") or "", ">06")
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def recyclebin_clean2(
        self,
        payload: int | str | Iterable[int | str] | dict = "",
        /,
        password: str = "000000",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def recyclebin_clean2(
        self,
        payload: int | str | Iterable[int | str] | dict = "",
        /,
        password: str = "000000",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def recyclebin_clean2(
        self,
        payload: int | str | Iterable[int | str] | dict = "",
        /,
        password: str = "000000",
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """回收站：删除或清空

        POST https://webapi.115.com/rb/clean

        .. note::
            如果没有指定任一 `rid`，就是清空回收站，如果有目录正在删除中则会被阻止

        .. tip::
            这个接口必须提供安全密钥。如果不提供，则默认使用 "000000"，在不必要的情况下，完全可以把安全密钥设为这个值

        :payload:
            - rid[0]: int | str 💡 不传就是清空
            - rid[1]: int | str
            - ...
            - password: int | str = "000000" 💡 安全密钥
        """
        api = complete_url("/rb/clean", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"rid[0]": payload}
        elif not isinstance(payload, dict):
            payload = {f"rid[{i}]": rid for i, rid in enumerate(payload)}
        payload.setdefault("password", password)
        payload["password"] = format(payload.get("password") or "", ">06")
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def recyclebin_clean_app(
        self,
        payload: int | str | Iterable[int | str] | dict = "",
        /,
        password: str = "000000",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def recyclebin_clean_app(
        self,
        payload: int | str | Iterable[int | str] | dict = "",
        /,
        password: str = "000000",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def recyclebin_clean_app(
        self,
        payload: int | str | Iterable[int | str] | dict = "",
        /,
        password: str = "000000",
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """回收站：删除或清空

        POST https://proapi.115.com/{app}/rb/secret_del

        .. note::
            只要不指定 `tid`，就是清空回收站，如果有目录正在删除中则会被阻止

        .. note::
            可以在设置中的【账号安全/安全密钥】页面下，关闭【文件(隐藏模式/清空删除回收站)】的按钮，就不需要传安全密钥了

        :payload:
            - tid: int | str = "" 💡 不传就是清空，多个用逗号 "," 隔开
            - password: int | str = "000000" 💡 安全密钥，是 6 位数字
            - user_id: int | str = <default> 💡 用户 id
        """
        api = complete_url("/rb/secret_del", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"tid": payload}
        elif not isinstance(payload, dict):
            payload = {"tid": ",".join(map(str, payload))}
        payload.setdefault("user_id", self.user_id)
        payload.setdefault("password", password)
        payload["password"] = format(payload.get("password") or "", ">06")
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def recyclebin_info(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def recyclebin_info(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def recyclebin_info(
        self,
        payload: int | str | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """回收站：文件信息

        POST https://webapi.115.com/rb/rb_info

        :payload:
            - rid: int | str
        """
        api = complete_url("/rb/rb_info", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"rid": payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def recyclebin_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def recyclebin_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def recyclebin_list(
        self,
        payload: int | dict = 0,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """回收站：列表

        GET https://webapi.115.com/rb

        :payload:
            - aid: int = 7 💡 area_id

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

            - cid: int | str = 0
            - limit: int = 32
            - offset: int = 0
            - o: str = <default> 💡 排序依据：dtime:删除时间
            - asc: 0 | 1 = <default>
            - source: str = <default>
        """
        api = complete_url("/rb", base_url=base_url)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload = {"aid": 7, "cid": 0, "limit": 32, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def recyclebin_list_app(
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
    def recyclebin_list_app(
        self,
        payload: int | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def recyclebin_list_app(
        self,
        payload: int | dict = 0,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """回收站：列表

        GET https://proapi.115.com/{app}/rb

        :payload:
            - aid: int = 7 💡 area_id

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

            - cid: int | str = 0
            - limit: int = 32
            - offset: int = 0
            - source: str = <default>
        """
        api = complete_url("/rb", base_url=base_url, app=app)
        if isinstance(payload, int):
            payload = {"offset": payload}
        payload = {"aid": 7, "cid": 0, "limit": 32, "offset": 0, **payload}
        return self.request(url=api, params=payload, async_=async_, **request_kwargs)

    @overload
    def recyclebin_revert(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False] = False,
        **request_kwargs,
    ) -> dict: ...

    @overload
    def recyclebin_revert(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def recyclebin_revert(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        base_url: str | Callable[[], str] = "https://webapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """回收站：还原

        POST https://webapi.115.com/rb/revert

        :payload:
            - rid[0]: int | str
            - rid[1]: int | str
            - ...
        """
        api = complete_url("/rb/revert", base_url=base_url)
        if isinstance(payload, (int, str)):
            payload = {"rid[0]": payload}
        elif not isinstance(payload, dict):
            payload = {f"rid[{i}]": rid for i, rid in enumerate(payload)}
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )

    @overload
    def recyclebin_revert_app(
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
    def recyclebin_revert_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[True],
        **request_kwargs,
    ) -> Coroutine[Any, Any, dict]: ...

    def recyclebin_revert_app(
        self,
        payload: int | str | Iterable[int | str] | dict,
        /,
        app: str = "android",
        base_url: str | Callable[[], str] = "https://proapi.115.com",
        *,
        async_: Literal[False, True] = False,
        **request_kwargs,
    ) -> dict | Coroutine[Any, Any, dict]:
        """回收站：还原

        POST https://proapi.115.com/{app}/rb/revert

        .. caution::
            ⚠️ 请不要并发执行，限制在 5 万个文件和目录以内

        :payload:
            - tid: int | str 💡 多个用逗号 "," 隔开
            - user_id: int | str = <default> 💡 用户 id
        """
        api = complete_url("/rb/revert", base_url=base_url, app=app)
        if isinstance(payload, (int, str)):
            payload = {"tid": payload}
        elif not isinstance(payload, dict):
            payload = {"tid": ",".join(map(str, payload))}
        payload.setdefault("user_id", self.user_id)
        return self.request(
            url=api, method="POST", data=payload, async_=async_, **request_kwargs
        )
