# 第三方代码来源与协议

本仓库在 MIT 协议下发布（见 [LICENSE](LICENSE)），其中 `src/fundrives/pan115/` 下的源码完整派生自下列第三方项目，按协议要求保留其原始版权与许可声明。

## p115client

- 上游项目：<https://github.com/ChenyangGao/p115client>
- PyPI 包名：[`p115client`](https://pypi.org/project/p115client/)
- 迁入基准版本：`0.0.9.6.5.1`
- 原始协议：MIT（与本仓库的 MIT 兼容）
- 涉及的文件：`src/fundrives/pan115/` 下的核心模块

## 内置与已瘦身替换的纯 Python 工具模块

本包早期曾将同作者（ChenyangGao）的 35 个 MIT 协议微包内联至 `src/fundrives/pan115/_vendor/`。经过瘦身重构，目前已有 **27 个微包**（`cachedict`、`dictattr`、`dicttools`、`ensure`、`integer_tool`、`iter_collect`、`property`、`socket_keepalive`、`startfile`、`temporary`、`texttools`、`undefined`、`argtools`、`decotools`、`errno2`、`posixpatht`、`glob_pattern`、`id2dirnode`、`ed2k`、`hashtools`、`sqlitetools`、`cookietools`、`http_response`、`http_request`、`urllib3_future_request`、`iterdir`、`download`）从 `_vendor/` 移除，其实际用到的最小子集已重写/归并为 8 个自主维护的内部模块（`_utils.py`、`_path.py`、`_hash.py`、`_sqlite.py`、`_http.py`、`_request.py`、`_iterdir.py`、`_download.py`），并移除 `p115cipher/aes.py` 冗余纯 Python AES 实现。

当前 `src/fundrives/pan115/_vendor/` 仅保留 8 个派生模块：

- 115 协议与加密：`p115cipher` (`0.0.5.4`)、`p115oss` (`0.1.2`)、`p115pickcode` (`0.0.5.4`)
- 异步、并发与流式文件：`python-asynctools` (`0.2.2`)、`python-concurrenttools` (`0.1.8`)、`python-iterutils` (`0.3.1.1`)、`python-filewrap` (`0.3.1.1`)、`python-httpfile` (`0.0.6.1`)

以上模块及派生代码均采用与下述相同的 MIT 许可证。

### 原始许可证全文

```
MIT License

Copyright (c) 2024 ChenyangGao <https://github.com/ChenyangGao>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
