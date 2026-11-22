"""HTTP Cookie / 响应解析 / httpx 请求层 / 下载断点续传 / HTTPFileReader 综合验证。"""

from __future__ import annotations

import asyncio
import gzip
import io
import time
import zlib
from http.cookiejar import CookieJar
from http.cookies import SimpleCookie
from urllib.error import HTTPError

import httpx
import pytest

from fundrives.pan115._download import download, download_async
from fundrives.pan115._http import (
    complete_url,
    cookie_header_for_url,
    cookies_to_dict,
    cookies_to_str,
    decompress_response,
    extract_cookies,
    get_charset,
    get_filename,
    get_length,
    get_mimetype,
    get_range,
    get_status_code,
    get_total_length,
    headers_get,
    is_chunked,
    is_range_request,
    is_timeouterror,
    normalize_request_args,
    parse_response,
    update_cookies,
)
from fundrives.pan115._request import request
from fundrives.pan115._vendor.httpfile import AsyncHTTPFileReader, HTTPFileReader


def test_cookie_conversion_filtering_and_expiry():
    # 字符串 -> dict / str + predicate 过滤
    raw = "UID=1_A1_1; CID=abc; SEID=def"
    assert cookies_to_dict(raw) == {"UID": "1_A1_1", "CID": "abc", "SEID": "def"}
    assert cookies_to_dict(raw, predicate={"UID", "SEID"}) == {
        "UID": "1_A1_1",
        "SEID": "def",
    }
    assert cookies_to_str({"A": "1", "B": "2"}, predicate={"B"}) == "B=2"

    # SimpleCookie <-> CookieJar 双向更新与域名/过期过滤
    sc = SimpleCookie()
    update_cookies(sc, {"SID": "live", "OLD": "dead"})
    sc["SID"]["domain"] = ".115.com"
    sc["SID"]["path"] = "/api"
    sc["OLD"]["expires"] = "Thu, 01-Jan-1970 00:00:00 GMT"

    hdrs_match = cookie_header_for_url(sc, "https://webapi.115.com/api/files")
    assert hdrs_match == {"SID": "live"}
    hdrs_other = cookie_header_for_url(sc, "https://other.example.com/api/files")
    assert hdrs_other == {}

    jar = CookieJar()
    update_cookies(jar, {"UID": "42", "KID": "99"}, domain=".115.com", path="/")
    assert cookies_to_dict(jar) == {"UID": "42", "KID": "99"}
    assert cookie_header_for_url(jar, "https://proapi.115.com/files") == {
        "UID": "42",
        "KID": "99",
    }

    # extract_cookies 从响应头提取 Set-Cookie
    sc2 = SimpleCookie()
    extract_cookies(
        sc2,
        "https://webapi.115.com/",
        {"Set-Cookie": "TOKEN=xyz; Path=/; Max-Age=3600"},
    )
    assert sc2["TOKEN"].value == "xyz"
    assert int(time.time()) > 0


def test_http_response_parsing_headers_range_and_compression():
    resp = type(
        "Resp",
        (),
        {
            "status_code": 206,
            "url": "https://cdn.115.com/dl/abc?filename=fallback.bin",
            "headers": {
                "Content-Type": "application/json; charset=UTF-8",
                "Content-Range": "bytes 10-19/100",
                "Accept-Ranges": "bytes",
                "Transfer-Encoding": "chunked",
            },
        },
    )()
    assert get_status_code(resp) == 206
    assert headers_get(resp, "content-type") == "application/json; charset=UTF-8"
    assert get_mimetype("application/json; charset=UTF-8") == "application/json"
    assert get_charset("application/json; charset=UTF-8") == "utf-8"
    assert get_range(resp) == (10, 19, 100)
    assert get_length(resp) == 10
    assert get_total_length(resp) == 100
    assert is_chunked(resp) is True
    assert is_range_request(resp) is True
    assert parse_response(resp, b'{"ok":true}') == {"ok": True}
    assert is_timeouterror(TimeoutError("t")) is True
    assert is_timeouterror(httpx.ReadTimeout("t")) is True
    assert is_timeouterror(ValueError("v")) is False

    # get_filename 覆盖 RFC5987 filename*= / quoted filename= / query / Content-Type 扩展名
    r_star = type(
        "R",
        (),
        {
            "url": "https://cdn.test/x",
            "headers": {
                "content-disposition": "attachment; filename*=UTF-8''%E6%B5%8B%E8%AF%95.txt"
            },
        },
    )()
    assert get_filename(r_star) == "测试.txt"

    r_quoted = type(
        "R",
        (),
        {
            "url": "https://cdn.test/x",
            "headers": {"content-disposition": 'attachment; filename="demo.zip"'},
        },
    )()
    assert get_filename(r_quoted) == "demo.zip"
    assert get_filename(resp) == "fallback.bin"

    # gzip / zlib deflate / raw deflate 解压
    raw_data = b"compress-me-1234567890" * 5
    assert decompress_response(gzip.compress(raw_data), "gzip") == raw_data
    assert decompress_response(zlib.compress(raw_data), "deflate") == raw_data
    comp = zlib.compressobj(wbits=-zlib.MAX_WBITS)
    raw_deflate = comp.compress(raw_data) + comp.flush()
    assert decompress_response(raw_deflate, "deflate") == raw_data


def test_complete_url_and_normalize_request_args_sync_and_async():
    assert complete_url("/files", default_port=8080, params={"cid": 0, "ok": True}) == (
        "http://localhost:8080/files?cid=0&ok=true"
    )
    assert complete_url("//example.com/a") == "http://example.com/a"

    # form-urlencoded
    form_args = normalize_request_args(
        "post", "https://api.test/submit", data={"k": "v 1", "flag": False}
    )
    assert form_args["headers"]["content-type"] == "application/x-www-form-urlencoded"
    assert form_args["data"] == b"k=v%201&flag=false"

    # multipart sync
    mp_args = normalize_request_args(
        "post",
        "https://api.test/upload",
        data={"field": "val"},
        files={"file": ("hello.txt", io.BytesIO(b"FILEBODY"))},
    )
    assert mp_args["headers"]["content-type"].startswith(
        "multipart/form-data; boundary="
    )
    mp_bytes = b"".join(bytes(chunk) for chunk in mp_args["data"])
    assert b'name="field"' in mp_bytes and b"val" in mp_bytes
    assert b'filename="hello.txt"' in mp_bytes and b"FILEBODY" in mp_bytes

    # multipart async
    async def _check_async_mp():
        amp_args = normalize_request_args(
            "post",
            "https://api.test/upload",
            data={"field": "aval"},
            files={"file": ("a.txt", io.BytesIO(b"ASYNCBODY"))},
            async_=True,
        )
        chunks = [bytes(c) async for c in amp_args["data"]]
        joined = b"".join(chunks)
        assert b"aval" in joined and b"ASYNCBODY" in joined

    asyncio.run(_check_async_mp())


def test_httpx_request_layer_errors_cookies_and_streaming():
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path == "/fail":
            return httpx.Response(403, content=b"forbidden")
        if req.url.path == "/echo":
            return httpx.Response(
                200,
                json={
                    "method": req.method,
                    "cookie": req.headers.get("cookie", ""),
                    "body": req.content.decode("utf-8"),
                },
            )
        if req.url.path == "/stream":
            return httpx.Response(200, content=b"0123456789abcdef")
        return httpx.Response(200, text="plain-text")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        # 4xx 抛 HTTPError
        with pytest.raises(HTTPError) as exc_info:
            request("https://api.test/fail", session=client, raise_for_status=True)
        assert exc_info.value.code == 403

        # httpx.Cookies 传递与 POST JSON
        hcookies = httpx.Cookies()
        hcookies.set("UID", "777", domain="api.test")
        res = request(
            "https://api.test/echo",
            method="POST",
            json={"hello": "world"},
            session=client,
            cookies=hcookies,
            parse=True,
        )
        assert res["method"] == "POST"
        assert "UID=777" in res["cookie"]
        assert res["body"] == '{"hello":"world"}'

        # parse=None 流式分段读尽不重复
        raw = request("https://api.test/stream", session=client, parse=None)
        assert raw.read(4) == b"0123"
        assert raw.read(4) == b"4567"
        assert raw.read() == b"89abcdef"
        assert raw.read() == b""
        raw.close()

        # text/plain 自动解码
        assert (
            request("https://api.test/txt", session=client, parse=True) == "plain-text"
        )


def test_download_sync_and_async_with_resume_and_reporthook(tmp_path):
    content = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 100  # 2600 bytes

    def make_handler(*, support_range: bool):
        def handler(req: httpx.Request) -> httpx.Response:
            rng = req.headers.get("range")
            if support_range and rng and rng.startswith("bytes="):
                start = int(rng.removeprefix("bytes=").split("-")[0])
                part = content[start:]
                return httpx.Response(
                    206,
                    content=part,
                    headers={
                        "Content-Length": str(len(part)),
                        "Content-Range": f"bytes {start}-{len(content) - 1}/{len(content)}",
                        "Accept-Ranges": "bytes",
                    },
                )
            hdrs = {
                "Content-Length": str(len(content)),
                "Content-Disposition": 'attachment; filename="sample.bin"',
            }
            if support_range:
                hdrs["Accept-Ranges"] = "bytes"
            return httpx.Response(200, content=content, headers=hdrs)

        return handler

    # 1. 同步下载到目录 + 自动取文件名 + reporthook 进度统计
    with httpx.Client(
        transport=httpx.MockTransport(make_handler(support_range=True))
    ) as hc:

        def opener(u, headers=None):
            return request(u, headers=headers, session=hc, parse=None)

        increments: list[int] = []
        prog = download(
            "https://dl.test/file",
            tmp_path,
            urlopen=opener,
            make_reporthook=lambda _total: increments.append,
        )
        saved = tmp_path / "sample.bin"
        assert saved.read_bytes() == content
        assert prog.downloaded == len(content) and prog.task_done
        assert sum(increments) == len(content)

        # 2. Range 断点续传（已有前 500 字节）
        partial_file = tmp_path / "resume_range.bin"
        partial_file.write_bytes(content[:500])
        prog2 = download(
            "https://dl.test/file",
            partial_file,
            resume=True,
            urlopen=opener,
        )
        assert partial_file.read_bytes() == content
        assert prog2.skipped == 500 and prog2.downloaded == len(content) - 500

        # 3. 已完整文件再次 resume 直接跳过
        prog3 = download(
            "https://dl.test/file",
            partial_file,
            resume=True,
            urlopen=opener,
        )
        assert prog3.skipped == len(content) and prog3.downloaded == 0

        # 4. 本地文件大于远端抛 OSError
        oversized = tmp_path / "oversized.bin"
        oversized.write_bytes(content + b"extra")
        with pytest.raises(OSError):
            download("https://dl.test/file", oversized, resume=True, urlopen=opener)

    # 5. 不支持 Range 时通过 bio_skip_iter 跳过已下载字节
    with httpx.Client(
        transport=httpx.MockTransport(make_handler(support_range=False))
    ) as hc2:

        def opener2(u, headers=None):
            return request(u, headers=headers, session=hc2, parse=None)

        no_range_file = tmp_path / "resume_norange.bin"
        no_range_file.write_bytes(content[:400])
        prog_nr = download(
            "https://dl.test/file",
            no_range_file,
            resume=True,
            urlopen=opener2,
        )
        assert no_range_file.read_bytes() == content
        assert prog_nr.skipped == 400 and prog_nr.downloaded == len(content) - 400

    # 6. 异步下载 + Range 断点续传
    async def _verify_async_download():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(make_handler(support_range=True))
        ) as ahc:

            def aopener(u, headers=None):
                return request(u, headers=headers, session=ahc, parse=None, async_=True)

            dst = tmp_path / "async_dl.bin"
            dst.write_bytes(content[:300])
            aprog = await download_async(
                "https://dl.test/file",
                dst,
                resume=True,
                urlopen=aopener,
            )
            assert dst.read_bytes() == content
            assert aprog.skipped == 300 and aprog.downloaded == len(content) - 300

    asyncio.run(_verify_async_download())


def test_httpfile_reader_sync_and_async_seek_and_read():
    data = b"line0\nline1\nline2\n0123456789"

    def handler(req: httpx.Request) -> httpx.Response:
        rng = req.headers.get("range")
        if rng and rng.startswith("bytes="):
            spec = rng.removeprefix("bytes=")
            start_s, _, end_s = spec.partition("-")
            start = int(start_s)
            end = int(end_s) if end_s else len(data) - 1
            chunk = data[start : end + 1]
            return httpx.Response(
                206,
                content=chunk,
                headers={
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {start}-{start + len(chunk) - 1}/{len(data)}",
                    "Accept-Ranges": "bytes",
                },
            )
        return httpx.Response(
            200,
            content=data,
            headers={
                "Content-Length": str(len(data)),
                "Accept-Ranges": "bytes",
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as hc:

        def mock_req(url, *args, **kwargs):
            kwargs["session"] = hc
            return request(url, *args, **kwargs)

        with HTTPFileReader("https://cdn.test/doc.txt", request=mock_req) as reader:
            assert len(reader) == len(data)
            assert reader.readline() == b"line0\n"
            assert reader.tell() == 6
            reader.seek(18)
            assert reader.read(5) == b"01234"
            reader.seek(-5, io.SEEK_END)
            assert reader.read() == b"56789"

    async def _verify_async_reader():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as ahc:

            def mock_areq(url, *args, **kwargs):
                kwargs["session"] = ahc
                kwargs["async_"] = True
                return request(url, *args, **kwargs)

            async with AsyncHTTPFileReader(
                "https://cdn.test/doc.txt", request=mock_areq
            ) as areader:
                await areader._init_info()
                assert len(areader) == len(data)
                assert await areader.readline() == b"line0\n"
                await areader.seek(18)
                assert await areader.read(5) == b"01234"

    asyncio.run(_verify_async_reader())
