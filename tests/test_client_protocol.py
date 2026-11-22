"""P115Client 核心协议路径回归测试（基于 httpx.MockTransport，零真实网络请求）。"""

import subprocess
import sys

import httpx
import pytest

from fundrives.pan115 import (
    P115AuthenticationError,
    P115Client,
    P115FileNotFoundError,
    P115OSError,
    check_response,
)
from fundrives.pan115._vendor.urllib3_future_request import request as httpx_request
from fundrives.pan115.util import share_extract_payload

COOKIES = "UID=100_A1_1; CID=cid_val; SEID=seid_val; KID=kid_val"


def _make_client(handler):
    """构造绑定 httpx.MockTransport 的 P115Client。"""
    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = P115Client(cookies=COOKIES)

    def _bound_request(url, *args, **kwargs):
        kwargs["session"] = http_client
        return httpx_request(url, *args, **kwargs)

    return client, http_client, _bound_request


def test_import_does_not_mutate_global_warnings_formatwarning():
    """import fundrives.pan115 不应劫持进程全局的 warnings.formatwarning。"""
    code = (
        "import warnings; "
        "before = warnings.formatwarning; "
        "import fundrives.pan115; "
        "assert warnings.formatwarning is before, 'formatwarning was mutated!'"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr


def test_fs_files_and_fs_file_over_mock_httpx():
    seen = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append((req.method, req.url.path, dict(req.url.params)))
        if req.url.path == "/files":
            return httpx.Response(
                200,
                json={
                    "state": True,
                    "path": [{"cid": 0, "name": "根目录"}],
                    "data": [
                        {
                            "fid": "101",
                            "n": "demo.txt",
                            "s": 12,
                            "sha": "abcd",
                            "t": "1700000000",
                            "pc": "pick123",
                            "fc": 1,
                        }
                    ],
                },
            )
        if req.url.path == "/files/get_info":
            return httpx.Response(
                200,
                json={
                    "state": True,
                    "data": [
                        {
                            "fid": "101",
                            "n": "demo.txt",
                            "s": 12,
                            "fc": 1,
                            "pc": "pick123",
                        }
                    ],
                },
            )
        return httpx.Response(404, json={"state": False})

    client, http_client, bound_req = _make_client(handler)
    try:
        listing = client.fs_files(0, request=bound_req)
        assert listing["state"] is True
        assert listing["data"][0]["n"] == "demo.txt"

        info = client.fs_file("101", request=bound_req)
        assert info["data"][0]["fid"] == "101"
        assert any(path == "/files" for _, path, _ in seen)
        assert any(path == "/files/get_info" for _, path, _ in seen)
    finally:
        http_client.close()


def test_fs_mkdir_delete_move_rename_search_and_quota():
    calls = []

    def handler(req: httpx.Request) -> httpx.Response:
        calls.append((req.method, req.url.path))
        if req.url.path == "/files/add":
            return httpx.Response(200, json={"state": True, "cid": "999"})
        if req.url.path == "/rb/delete":
            return httpx.Response(200, json={"state": True})
        if req.url.path == "/files/move":
            return httpx.Response(200, json={"state": True})
        if req.url.path == "/files/batch_rename":
            return httpx.Response(200, json={"state": True})
        if req.url.path == "/files/search":
            return httpx.Response(
                200, json={"state": True, "data": [{"fid": "1", "n": "hit.txt"}]}
            )
        if req.url.path == "/files/index_info":
            return httpx.Response(
                200,
                json={
                    "state": True,
                    "data": {
                        "space_info": {
                            "all_total": {"size": 1000},
                            "all_use": {"size": 250},
                        }
                    },
                },
            )
        return httpx.Response(200, json={"state": True})

    client, http_client, bound_req = _make_client(handler)
    try:
        assert client.fs_mkdir("docs", 0, request=bound_req)["cid"] == "999"
        assert client.fs_delete("101", request=bound_req)["state"] is True
        assert client.fs_move("101", "999", request=bound_req)["state"] is True
        assert client.fs_rename(("101", "new.txt"), request=bound_req)["state"] is True
        assert client.fs_search("hit", request=bound_req)["data"][0]["n"] == "hit.txt"
        quota = client.user_space_info(request=bound_req)
        assert quota["state"] is True
        assert len(calls) == 6
    finally:
        http_client.close()


def test_check_response_error_mapping():
    with pytest.raises(P115AuthenticationError):
        check_response({"state": False, "errno": 99, "error": "please login"})
    with pytest.raises(P115FileNotFoundError):
        check_response({"state": False, "errno": 50003, "error": "file not found"})
    with pytest.raises(P115OSError):
        check_response({"state": False, "errno": 999999, "error": "unknown error"})


def test_share_extract_payload():
    parsed = share_extract_payload("https://115cdn.com/s/sw123456789?password=abcd")
    assert parsed["share_code"] == "sw123456789"
    assert parsed["receive_code"] == "abcd"
