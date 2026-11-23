"""P115Client 同步/异步协议、加密链路、Cookie 文件落盘、P115FileSystem 与 tool 端到端验证。"""

from __future__ import annotations

import asyncio
import hashlib
from urllib.parse import parse_qs

import httpx
import orjson

from fundrives.pan115 import P115Client
from fundrives.pan115._request import request as httpx_request
from fundrives.pan115._vendor.p115cipher import (
    AES_IV,
    AES_KEY,
    ecdh_aes_encrypt,
    rsa_encrypt,
)
from fundrives.pan115._vendor.p115cipher.util import aes_cbc_decrypt
from fundrives.pan115._vendor.p115pickcode import to_id, to_pickcode
from fundrives.pan115.const import CLIENT_API_METHODS_MAP, CLIENT_METHOD_API_MAP
from fundrives.pan115.fs import P115FileSystem
from fundrives.pan115.tool.attr import normalize_attr
from fundrives.pan115.tool.iterdir import iter_files

COOKIES = "UID=12345_A1_1; CID=cid_abc; SEID=seid_def; KID=kid_ghi"


def _lz4_frame(payload: bytes) -> bytes:
    """将小块字节编码为 115 服务端使用的 2 字节长度前缀 LZ4 literal 帧。"""
    n = len(payload)
    if n < 15:
        block = bytes([n << 4]) + payload
    else:
        rem = n - 15
        block = bytes([0xF0]) + b"\xff" * (rem // 255) + bytes([rem % 255]) + payload
    return len(block).to_bytes(2, "little") + block


def test_client_api_maps_populated_without_global_leaks():
    """验证 client/ 分域子包结构、API 映射表正常填充且无全局泄漏。"""
    import fundrives.pan115.client as client_mod

    assert hasattr(client_mod, "__path__"), "client 应已拆分为分域子包"
    assert len(CLIENT_METHOD_API_MAP) >= 480
    assert len(CLIENT_API_METHODS_MAP) >= 470
    assert "P115Client.fs_files" in CLIENT_METHOD_API_MAP
    assert not hasattr(client_mod, "CRE_CLIENT_API_search")
    assert not hasattr(client_mod, "temp_globals")
    for sub in (
        "_common",
        "open_client",
        "fs_mixin",
        "transfer_mixin",
        "share_mixin",
        "account_mixin",
        "extra_mixin",
    ):
        assert (
            hasattr(client_mod, sub)
            or f"fundrives.pan115.client.{sub}" in __import__("sys").modules
        )


def test_cookie_file_persistence_and_user_id(tmp_path):
    """验证通过 Path 构造 P115Client 时 Cookie 读取、user_id 解析与更新落盘。"""
    cookie_file = tmp_path / "115-cookies.txt"
    cookie_file.write_text(COOKIES, encoding="utf-8")

    client = P115Client(cookie_file)
    assert client.user_id == 12345
    assert "CID=cid_abc" in client.cookies_str

    # pickcode 与 id 双向转换（离线传入 stable_point）
    pc = client.to_pickcode(987654, stable_point="0000")
    assert client.to_id(pc) == 987654
    assert to_id(to_pickcode(987654)) == 987654


def test_client_async_api_and_share_workflow():
    """验证 P115Client 在 async_=True 下的文件列表、目录创建、分享快照与转存全链路。"""
    seen: list[tuple[str, str]] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append((req.method, req.url.path))
        if req.url.path == "/files":
            return httpx.Response(
                200,
                json={
                    "state": True,
                    "count": 1,
                    "path": [{"cid": 0, "name": "根目录"}],
                    "data": [
                        {
                            "fid": "201",
                            "cid": "0",
                            "n": "async.txt",
                            "s": 64,
                            "sha": "0" * 40,
                            "t": "1700000000",
                            "pc": to_pickcode(201),
                            "fc": 1,
                        }
                    ],
                },
            )
        if req.url.path == "/files/add":
            return httpx.Response(200, json={"state": True, "cid": "500"})
        if req.url.path == "/share/snap":
            return httpx.Response(
                200,
                json={
                    "state": True,
                    "data": {"count": 1, "list": [{"fid": "701", "n": "shared.pdf"}]},
                },
            )
        if req.url.path == "/share/receive":
            return httpx.Response(200, json={"state": True})
        return httpx.Response(404, json={"state": False})

    async def _run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as ahc:
            client = P115Client(cookies=COOKIES)

            def bound_req(url, *args, **kwargs):
                kwargs["session"] = ahc
                return httpx_request(url, *args, **kwargs)

            listing = await client.fs_files(0, async_=True, request=bound_req)
            assert listing["data"][0]["n"] == "async.txt"

            mk = await client.fs_mkdir("newdir", 0, async_=True, request=bound_req)
            assert mk["cid"] == "500"

            snap = await client.share_snap(
                {"share_code": "sw123", "receive_code": "abcd"},
                async_=True,
                request=bound_req,
            )
            assert snap["data"]["list"][0]["fid"] == "701"

            recv = await client.share_receive(
                {
                    "share_code": "sw123",
                    "receive_code": "abcd",
                    "file_id": "701",
                    "cid": "500",
                },
                async_=True,
                request=bound_req,
            )
            assert recv["state"] is True

    asyncio.run(_run())
    assert ("GET", "/files") in seen
    assert ("POST", "/files/add") in seen
    assert ("GET", "/share/snap") in seen
    assert ("POST", "/share/receive") in seen


def test_encrypted_download_url_app_and_upload_init_fast_pass(monkeypatch):
    """验证 115 加密协议闭环：download_url_app (RSA) 与 upload_file_init (ECDH-AES 秒传)。"""
    import fundrives.pan115.client as client_mod

    pc = to_pickcode(301)
    dl_payload = orjson.dumps(
        {
            "301": {
                "file_name": "movie.mp4",
                "file_size": 1024,
                "url": {"url": "https://cdn.115.test/movie.mp4"},
            }
        }
    )
    upload_fast_resp = orjson.dumps(
        {"status": 2, "statuscode": 0, "pickcode": pc, "file_id": "301"}
    )

    captured: dict[str, object] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path == "/app/chrome/downurl":
            form = parse_qs(req.content.decode("utf-8"))
            # 确认客户端发出的请求体确实经过真实 rsa_encrypt 加密
            assert "data" in form and len(form["data"][0]) > 20
            captured["downurl_req"] = form["data"][0]
            return httpx.Response(
                200,
                json={"state": True, "data": "MOCK_RSA_SERVER_SIGNED_PAYLOAD"},
            )
        if req.url.path == "/app/2.0/pro/uploadinfo":
            return httpx.Response(
                200, json={"user_id": 12345, "userkey": "MOCK_USER_KEY"}
            )
        if req.url.path == "/4.0/initupload.php":
            # 校验请求体确实经过真实 ECDH-AES 加密且可解出预期表单字段
            dec = aes_cbc_decrypt(req.content, AES_KEY, AES_IV)
            captured["upload_init_plain"] = dec.decode("utf-8")
            return httpx.Response(
                200, content=ecdh_aes_encrypt(_lz4_frame(upload_fast_resp))
            )
        return httpx.Response(404, json={"state": False})

    # 115 下载响应由服务端私钥签名、客户端公钥验签；此处替身解签以验证完整响应解析链
    monkeypatch.setattr(
        client_mod,
        "rsa_decrypt",
        lambda cipher: (
            dl_payload if cipher == "MOCK_RSA_SERVER_SIGNED_PAYLOAD" else b""
        ),
    )
    assert len(rsa_encrypt(b"probe")) > 20

    with httpx.Client(transport=httpx.MockTransport(handler)) as hc:
        client = P115Client(cookies=COOKIES)

        def bound_req(url, *args, **kwargs):
            kwargs["session"] = hc
            return httpx_request(url, *args, **kwargs)

        # 1. RSA 加密下载链接获取（同步 + 解密校验）
        down = client.download_url_app(pc, request=bound_req)
        assert down["state"] is True
        assert down["data"]["301"]["url"]["url"] == "https://cdn.115.test/movie.mp4"
        assert "headers" in down

        # 2. ECDH-AES 上传初始化（秒传命中 status == 2）
        sha1 = hashlib.sha1(b"hello-115").hexdigest().upper()
        init_res = client.upload_file_init(
            filename="hello.txt",
            filesha1=sha1,
            filesize=9,
            pid=0,
            payload={"userkey": "MOCK_USER_KEY"},
            request=bound_req,
        )
        assert init_res["status"] == 2
        assert init_res["pickcode"] == pc
        assert "filename=hello.txt" in str(captured["upload_init_plain"])


def test_filesystem_and_tool_attr_and_iter_files_integration():
    """串联验证 P115FileSystem (LRUDict + IdToDirnode + _path + _iterdir) 与 tool 模块。"""
    # 模拟一个 2 层目录树：/ -> docs(10) -> sub(20) -> report.txt(201), /readme.md(101)
    pc_10 = to_pickcode(10, prefix="fa")
    pc_20 = to_pickcode(20, prefix="fa")
    pc_101 = to_pickcode(101)
    pc_201 = to_pickcode(201)

    dir_data = {
        "0": {
            "path": [{"cid": 0, "name": "根目录"}],
            "data": [
                {
                    "cid": "10",
                    "pid": "0",
                    "n": "docs",
                    "pc": pc_10,
                    "t": "1700000001",
                    "te": "1700000001",
                    "tp": "1700000001",
                },
                {
                    "fid": "101",
                    "cid": "0",
                    "n": "readme.md",
                    "s": 128,
                    "sha": "A" * 40,
                    "pc": pc_101,
                    "t": "1700000002",
                    "te": "1700000002",
                    "tp": "1700000002",
                },
            ],
        },
        "10": {
            "path": [
                {"cid": 0, "pid": 0, "name": "根目录"},
                {"cid": 10, "pid": 0, "name": "docs"},
            ],
            "data": [
                {
                    "cid": "20",
                    "pid": "10",
                    "n": "sub",
                    "pc": pc_20,
                    "t": "1700000003",
                    "te": "1700000003",
                    "tp": "1700000003",
                },
            ],
        },
        "20": {
            "path": [
                {"cid": 0, "pid": 0, "name": "根目录"},
                {"cid": 10, "pid": 0, "name": "docs"},
                {"cid": 20, "pid": 10, "name": "sub"},
            ],
            "data": [
                {
                    "fid": "201",
                    "cid": "20",
                    "n": "report.txt",
                    "s": 512,
                    "sha": "B" * 40,
                    "pc": pc_201,
                    "t": "1700000004",
                    "te": "1700000004",
                    "tp": "1700000004",
                },
            ],
        },
    }

    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/files"):
            cid = req.url.params.get("cid", "0")
            cur = req.url.params.get("cur", "1")
            show_dir = req.url.params.get("show_dir", "1")
            offset = int(req.url.params.get("offset", "0"))
            entry = dir_data.get(cid, {"path": [], "data": []})
            if cur == "0" and cid == "0":
                items = [
                    it
                    for d in dir_data.values()
                    for it in d["data"]
                    if show_dir != "0" or "fid" in it
                ]
            else:
                items = [it for it in entry["data"] if show_dir != "0" or "fid" in it]
            page = items[offset:]
            return httpx.Response(
                200,
                json={
                    "state": True,
                    "cid": int(cid),
                    "offset": offset,
                    "count": len(items),
                    "path": entry["path"],
                    "data": page,
                },
            )
        return httpx.Response(404, json={"state": False})

    with httpx.Client(transport=httpx.MockTransport(handler)) as hc:
        client = P115Client(cookies=COOKIES)
        orig_request = client.request

        def patched_request(*args, **kwargs):
            kwargs.setdefault(
                "request", lambda *a, **kw: httpx_request(*a, session=hc, **kw)
            )
            return orig_request(*args, **kwargs)

        client.request = patched_request  # type: ignore[method-assign]

        # 1. tool.attr.normalize_attr 验证
        norm_file = normalize_attr(dir_data["0"]["data"][1])
        assert norm_file["id"] == 101
        assert norm_file["name"] == "readme.md"
        assert norm_file["size"] == 128
        assert norm_file["is_dir"] is False
        assert norm_file.id == 101  # AttrDict 属性访问

        norm_dir = normalize_attr(dir_data["0"]["data"][0])
        assert norm_dir["id"] == 10 and norm_dir["is_dir"] is True

        # 2. tool.iterdir.iter_files 递归遍历验证
        files = list(iter_files(client, 0, max_workers=0))
        assert sorted(f["name"] for f in files) == ["readme.md", "report.txt"]

        # 3. P115FileSystem 使用 LRUDict (id_to_readdir=32) 与路径解析/glob/walk 验证
        fs = P115FileSystem(client, id_to_readdir=32)
        assert fs.getcwd() == "/"
        assert sorted(p.name for p in fs.listdir("/")) == ["docs", "readme.md"]
        assert fs.exists("/docs/sub/report.txt") is True
        assert fs.isfile("/docs/sub/report.txt") is True
        assert fs.isdir("/docs/sub") is True
        assert fs.exists("/docs/nonexistent.txt") is False

        # chdir + 相对路径
        fs.chdir("/docs")
        assert fs.getcwd() == "/docs"
        assert [p.name for p in fs.listdir("sub")] == ["report.txt"]

        # glob 匹配
        matched = [p.path for p in fs.glob("**/*.txt")]
        assert matched == ["/docs/sub/report.txt"]
