"""fundrive-p115 基础冒烟与契约测试。"""

import importlib
import pathlib

import fundrives
from fundrives.p115 import (
    P115AuthenticationError,
    P115Client,
    P115Error,
    P115FileNotFoundError,
    P115OSError,
    check_response,
)


def test_pep420_namespace_has_no_init_file():
    """src/fundrives/ 不能有 __init__.py，否则会遮蔽其他 fundrives.* 驱动包。"""
    src_ns = pathlib.Path(__file__).resolve().parents[1] / "src" / "fundrives"
    assert not (src_ns / "__init__.py").exists()
    assert fundrives.__file__ is None


def test_public_exports_and_subpackages():
    """核心导出和子包都应可正常导入。"""
    assert P115Client is not None
    assert importlib.import_module("fundrives.p115.client") is not None
    assert importlib.import_module("fundrives.p115.const") is not None
    assert importlib.import_module("fundrives.p115.exception") is not None
    assert importlib.import_module("fundrives.p115.fs") is not None
    assert importlib.import_module("fundrives.p115.tool") is not None
    assert importlib.import_module("fundrives.p115.util") is not None


def test_exception_hierarchy():
    """Pan115Drive 依赖 P115FileNotFoundError 继承内置 FileNotFoundError。"""
    assert issubclass(P115FileNotFoundError, FileNotFoundError)
    assert issubclass(P115FileNotFoundError, P115OSError)
    assert issubclass(P115AuthenticationError, P115OSError)
    assert issubclass(P115OSError, P115Error)


def test_pan115_drive_required_client_methods_exist():
    """确保 Pan115Drive 依赖的全部 P115Client 方法都在公开 API 中。"""
    required_methods = (
        "login",
        "fs_mkdir",
        "fs_file",
        "fs_delete",
        "fs_files",
        "download_url_app",
        "upload_file",
        "fs_search",
        "fs_move",
        "fs_rename",
        "user_space_info",
    )
    for name in required_methods:
        assert callable(getattr(P115Client, name, None)), f"缺少方法: {name}"


def test_client_init_with_cookies_without_network():
    """传入 cookies 构造客户端不应触发网络请求，且正确解析 cookies。"""
    client = P115Client(cookies="UID=1_A1_1; CID=abc; SEID=def; KID=ghi")
    assert "UID=1_A1_1" in client.cookies_str
    assert "CID=abc" in client.cookies_str


def test_check_response_passes_through_ok_payload():
    payload = {"state": True, "data": [{"fid": "1"}]}
    assert check_response(payload) == payload
