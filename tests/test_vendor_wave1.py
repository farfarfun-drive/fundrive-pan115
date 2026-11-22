"""全部内联微包（_vendor）单元测试与零上游微包依赖守卫。"""

import ast
import io
import pathlib
import tomllib
from http.cookies import SimpleCookie

from fundrives.pan115._hash import ed2k_hash, file_digest
from fundrives.pan115._http import (
    complete_url,
    cookies_to_dict,
    get_status_code,
    update_cookies,
)
from fundrives.pan115._path import (
    IdToDirnode,
    escape,
    joinpath,
    normpath,
    splits,
    translate_iter,
)
from fundrives.pan115._sqlite import connect, query
from fundrives.pan115._utils import (
    AttrDict,
    KeyLowerDict,
    LRUDict,
    Undefined,
    argcount,
    dict_key_to_lower_merge,
    dict_map,
    ensure_bytes,
    errno,
    errno2error,
    format_time,
    get_first,
    grouped_mapping,
    is_undefined,
    iter_keyed_dups,
    locked_cacheproperty,
    startfile,
    startfile_async,
    try_parse_int,
    undefined,
)
from fundrives.pan115._vendor.asynctools import ensure_async
from fundrives.pan115._vendor.concurrenttools import threadpool_map
from fundrives.pan115._vendor.filewrap import to_bytes_view
from fundrives.pan115._vendor.iterutils import chunked
from fundrives.pan115._vendor.p115cipher import (
    AES_IV,
    AES_KEY,
    ecdh_aes_decrypt,
    ecdh_aes_encrypt,
    ecdh_encode_token,
    rsa_decrypt,
    rsa_encrypt,
)
from fundrives.pan115._vendor.p115cipher.util import aes_cbc_decrypt
from fundrives.pan115._vendor.p115pickcode import (
    is_valid_pickcode,
    pickcode_to_id,
    to_id,
    to_pickcode,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "fundrives" / "pan115"

ELIMINATED_DISTS = {
    "brotli",
    "cachedict",
    "ed2k",
    "errno2",
    "glob_pattern",
    "http_response",
    "id2dirnode",
    "integer_tool",
    "iter_collect",
    "iterdir",
    "p115cipher",
    "p115oss",
    "p115pickcode",
    "posixpatht",
    "python-argtools",
    "python-asynctools",
    "python-concurrenttools",
    "python-cookietools",
    "python-decotools",
    "python-dictattr",
    "python-dicttools",
    "python-download",
    "python-encode_uri",
    "python-ensure",
    "python-filewrap",
    "python-hashtools",
    "python-http_request",
    "python-httpfile",
    "python-iterutils",
    "python-property",
    "python-startfile",
    "python-temporary",
    "python-texttools",
    "python-undefined",
    "socket-keepalive",
    "sqlitetools",
    "sqlparse",
    "urllib3-future",
    "urllib3_future_request",
    "wcwidth",
    "zstandard",
}

ELIMINATED_MODULES = {
    "argtools",
    "asynctools",
    "cachedict",
    "concurrenttools",
    "cookietools",
    "decotools",
    "dictattr",
    "dicttools",
    "download",
    "ed2k",
    "encode_uri",
    "ensure",
    "errno2",
    "filewrap",
    "glob_pattern",
    "hashtools",
    "http_request",
    "http_response",
    "httpfile",
    "id2dirnode",
    "integer_tool",
    "iter_collect",
    "iterdir",
    "iterutils",
    "p115cipher",
    "p115oss",
    "p115pickcode",
    "posixpatht",
    "property",
    "socket_keepalive",
    "sqlitetools",
    "startfile",
    "temporary",
    "texttools",
    "undefined",
    "urllib3_future",
    "urllib3_future_request",
}


def test_zero_upstream_micropackages_in_pyproject():
    """全部 36 个上游微包（含传递微包）均不得出现在 pyproject.toml。"""
    deps = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]["dependencies"]
    declared = {d.split(">=")[0].split("<")[0].split("==")[0].strip() for d in deps}
    leaked = sorted(declared & ELIMINATED_DISTS)
    assert not leaked, f"已内联的依赖又出现在 pyproject.toml: {leaked}"


def test_source_does_not_import_eliminated_external_modules():
    """src/fundrives/pan115/ 内不得再直接 import 任何已内联的外部微包。"""
    leaks = []
    for py in sorted(SRC.rglob("*.py")):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top in ELIMINATED_MODULES:
                        leaks.append(f"{py.relative_to(SRC)}: import {alias.name}")
            elif (
                isinstance(node, ast.ImportFrom)
                and node.level == 0
                and node.module
                and node.module.split(".")[0] in ELIMINATED_MODULES
            ):
                leaks.append(f"{py.relative_to(SRC)}: from {node.module}")
    assert not leaks, "\n".join(leaks)


def test_pickcode_roundtrip():
    pc = to_pickcode(123456)
    assert is_valid_pickcode(pc)
    assert pickcode_to_id(pc) == 123456
    assert to_id(pc) == 123456


def test_p115cipher_roundtrip():
    payload = b"hello-fundrive-pan115"
    enc_rsa = rsa_encrypt(payload)
    assert isinstance(enc_rsa, (bytes, bytearray, str)) and len(enc_rsa) > 0
    assert callable(rsa_decrypt) and callable(ecdh_aes_decrypt)
    enc_ecdh = ecdh_aes_encrypt(payload)
    assert aes_cbc_decrypt(enc_ecdh, AES_KEY, AES_IV) == payload
    assert len(ecdh_encode_token(1700000000)) > 0


def test_hash_and_ed2k_and_filewrap():
    size, digest = file_digest(io.BytesIO(b"abc"), "sha1")
    assert size == 3
    assert digest.hexdigest() == "a9993e364706816aba3e25717850c26c9cd0d89d"
    size2, ed2k_val = ed2k_hash(io.BytesIO(b"abc"))
    assert size2 == 3 and len(ed2k_val) == 32
    assert bytes(to_bytes_view(b"xyz")) == b"xyz"


def test_errno2_and_exceptions():
    assert issubclass(errno2error[errno.ENOENT], FileNotFoundError)


def test_posixpatht_and_glob():
    assert normpath("/a/b/../c/") == "/a/c"
    assert joinpath("/a", "b", "c.txt") == "/a/b/c.txt"
    parts, _ = splits("/a/b/c")
    assert parts == ["", "a", "b", "c"]
    assert escape("a/b") == r"a\/b"
    assert list(translate_iter("*.txt"))


def test_dict_and_cookie_helpers():
    d = AttrDict(a=1)
    assert d.a == 1
    assert get_first({"a": 1, "b": 2}, "x", "b") == 2
    assert dict_map({"a": 2}, value=lambda v: v * 2) == {"a": 4}
    lower = KeyLowerDict()
    lower["Content-Type"] = "json"
    assert lower["content-type"] == "json"
    assert dict_key_to_lower_merge({"A": 1}, {"B": 2}) == {"a": 1, "b": 2}
    cookies = cookies_to_dict("UID=1; CID=2")
    assert cookies == {"UID": "1", "CID": "2"}
    jar = SimpleCookie("UID=1")
    update_cookies(jar, {"SEID": "3"})
    assert jar["SEID"].value == "3"


def test_cache_sqlite_and_http_helpers():
    cache = LRUDict(2)
    cache["a"] = 1
    cache["b"] = 2
    cache["c"] = 3
    assert "a" not in cache and list(cache) == ["b", "c"]

    nodes = IdToDirnode()
    nodes[1] = ("docs", 0)
    assert nodes[1] == ("docs", 0)

    con = connect(":memory:")
    con.execute("CREATE TABLE t (id INT, name TEXT)")
    con.execute("INSERT INTO t VALUES (1, 'ok')")
    assert list(query(con, "SELECT name FROM t")) == [("ok",)]
    con.close()

    assert complete_url("example.com/a") == "http://example.com/a"
    assert get_status_code(type("Resp", (), {"status_code": 200})()) == 200


def test_concurrency_iter_and_misc_utilities():
    assert is_undefined(undefined)
    assert isinstance(undefined, Undefined)
    assert not bool(undefined)
    assert argcount(lambda a, b, c=1: a) == 3
    assert try_parse_int("42") == 42
    assert ensure_bytes("abc") == b"abc"
    assert grouped_mapping([(1, "a"), (1, "b"), (2, "c")]) == {1: ["a", "b"], 2: ["c"]}
    assert list(iter_keyed_dups([(1, "a"), (2, "b"), (1, "c")])) == [
        (1, "a"),
        (1, "c"),
    ]
    assert list(chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert sorted(threadpool_map(lambda x: x * 2, [1, 2, 3], max_workers=2)) == [
        2,
        4,
        6,
    ]
    assert callable(ensure_async(lambda x: x))
    assert callable(startfile) and callable(startfile_async)

    class Demo:
        def __init__(self):
            self.calls = 0

        @locked_cacheproperty
        def value(self):
            self.calls += 1
            return 99

    demo = Demo()
    assert demo.value == 99 and demo.value == 99 and demo.calls == 1

    # LRUDict with default_factory & LRU eviction order
    lru_locks: LRUDict[str, list[int]] = LRUDict(2, default_factory=list)
    lru_locks["a"].append(1)
    lru_locks["b"].append(2)
    _ = lru_locks["a"]  # touch "a" so "b" is evicted next
    lru_locks["c"].append(3)
    assert "b" not in lru_locks and list(lru_locks) == ["a", "c"]

    # time formatting helper
    assert format_time(3661) == "01:01:01"

    # async iter_keyed_dups & grouped_mapping
    import asyncio

    async def _aiter(items):
        for item in items:
            yield item

    async def _check_async_iter():
        g = await grouped_mapping(_aiter([(1, "a"), (1, "b"), (2, "c")]))
        assert g == {1: ["a", "b"], 2: ["c"]}
        dups = [
            x
            async for x in iter_keyed_dups(
                _aiter([(1, "a"), (2, "b"), (1, "c")]), keep_first=True
            )
        ]
        assert dups == [(1, "c")]

    asyncio.run(_check_async_iter())


def test_httpx_backed_request_sync_and_async():
    """验证基于 httpx 的同步/异步请求适配层（JSON 解析、重定向、Cookie 传递与流式读取）。"""
    import asyncio
    from http.cookiejar import CookieJar

    import httpx

    from fundrives.pan115._request import request

    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path == "/redirect":
            return httpx.Response(
                302,
                headers={"location": "/target", "set-cookie": "SID=abc; Path=/"},
            )
        if req.url.path == "/target":
            return httpx.Response(
                200,
                json={"cookie": req.headers.get("cookie", ""), "method": req.method},
            )
        return httpx.Response(200, content=b"stream-body")

    jar = CookieJar()
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        data = request(
            "https://example.test/redirect",
            session=client,
            cookies=jar,
            parse=True,
        )
        assert data == {"cookie": "SID=abc", "method": "GET"}
        raw = request("https://example.test/raw", session=client, parse=None)
        assert raw.read(6) == b"stream"
        assert raw.read() == b"-body"
        raw.close()

    async def _run_async():
        jar2 = CookieJar()
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as aclient:
            adata = await request(
                "https://example.test/redirect",
                session=aclient,
                cookies=jar2,
                parse=True,
                async_=True,
            )
            assert adata == {"cookie": "SID=abc", "method": "GET"}

    asyncio.run(_run_async())


def test_slimming_guard_and_owned_modules():
    """验证已瘦身移除的 27 个 _vendor 微包不再回归，且自维护模块行为正确。"""
    import gzip
    import zlib

    from fundrives.pan115._download import download
    from fundrives.pan115._http import (
        decompress_response,
        get_filename,
        normalize_request_args,
    )
    from fundrives.pan115._iterdir import iterdir_generic, walk_generic

    vendor_entries = sorted(
        p.name
        for p in (SRC / "_vendor").iterdir()
        if p.name not in ("__init__.py", "__pycache__")
    )
    assert vendor_entries == [
        "asynctools",
        "concurrenttools",
        "filewrap.py",
        "httpfile.py",
        "iterutils",
        "p115cipher",
        "p115oss",
        "p115pickcode.py",
    ]
    assert not (SRC / "_vendor" / "p115cipher" / "aes.py").exists()

    # _http: decompress_response (gzip & deflate) + get_filename + normalize_request_args
    assert decompress_response(gzip.compress(b"hello"), "gzip") == b"hello"
    assert decompress_response(zlib.compress(b"hello"), "deflate") == b"hello"
    fake_resp = type(
        "Resp",
        (),
        {
            "url": "https://example.test/download/report",
            "headers": {"content-type": "text/plain; charset=utf-8"},
        },
    )()
    assert get_filename(fake_resp) == "report.txt"
    req_args = normalize_request_args(
        "post", "example.test/api", json={"a": 1}, headers={"X-Test": "ok"}
    )
    assert req_args["method"] == "POST"
    assert req_args["url"] == "http://example.test/api"
    assert req_args["headers"]["x-test"] == "ok"
    assert req_args["data"] == b'{"a":1}'

    # _iterdir: iterdir_generic & walk_generic
    tree = {"root": ["dir1", "f0"], "dir1": ["f1"]}
    items = list(
        iterdir_generic(
            "root",
            iterdir=lambda n: tree.get(n, []),
            isdir=lambda n: n in tree,
            max_depth=-1,
        )
    )
    assert items == ["dir1", "f1", "f0"]
    walked = list(
        walk_generic(
            "root",
            iterdir=lambda n: tree.get(n, []),
            isdir=lambda n: n in tree,
            max_depth=-1,
        )
    )
    assert walked == [("root", ["dir1"], ["f0"]), ("dir1", [], ["f1"])]

    # _download: download into BytesIO via mock urlopen
    class _FakeResp:
        headers = {"content-length": "5"}

        def __init__(self):
            self._buf = io.BytesIO(b"12345")

        def read(self, n=-1):
            return self._buf.read(n)

        def close(self):
            pass

    out = io.BytesIO()
    prog = download(
        "https://example.test/file.bin",
        out,
        urlopen=lambda _url, headers=None: _FakeResp(),
    )
    assert out.getvalue() == b"12345"
    assert prog.downloaded == 5 and prog.task_done
