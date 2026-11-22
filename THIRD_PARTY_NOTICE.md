# 第三方代码来源与协议

本仓库在 MIT 协议下发布（见 [LICENSE](LICENSE)），其中 `src/fundrives/pan115/` 下的源码完整派生自下列第三方项目，按协议要求保留其原始版权与许可声明。

## p115client

- 上游项目：<https://github.com/ChenyangGao/p115client>
- PyPI 包名：[`p115client`](https://pypi.org/project/p115client/)
- 迁入基准版本：`0.0.9.6.5.1`
- 原始协议：MIT（与本仓库的 MIT 兼容）
- 涉及的文件：`src/fundrives/pan115/` 下的核心模块

## 内置纯 Python 工具微包（`src/fundrives/pan115/_vendor/`）

为彻底摆脱上游微包高频不兼容变更，下列同作者（ChenyangGao）的 35 个 MIT 协议工具模块已全部内联至 `src/fundrives/pan115/_vendor/` 并随本仓库自主维护：

- 核心协议与加密：`p115cipher` (`0.0.5.4`)、`p115oss` (`0.1.2`)、`p115pickcode` (`0.0.5.4`)、`ed2k` (`0.0.2.2`)
- HTTP 与下载：`http_response` (`0.0.9`)、`python-http_request` (`0.1.7.1`)、`python-httpfile` (`0.0.6.1`)、`python-download` (`0.0.4.1`)、`urllib3_future_request` (`0.0.2`)、`socket_keepalive` (`0.0.1`)
- 异步、并发与迭代：`python-asynctools` (`0.2.2`)、`python-concurrenttools` (`0.1.8`)、`python-iterutils` (`0.3.1.1`)、`iter_collect` (`0.0.6`)、`iterdir` (`0.0.10`)、`python-decotools` (`0.0.4`)
- 文件、路径与数据工具：`python-filewrap` (`0.3.1.1`)、`python-hashtools` (`0.0.6`)、`sqlitetools` (`0.1.3`)、`errno2` (`0.0.5`)、`posixpatht` (`0.0.4`)、`glob_pattern` (`0.0.2`)、`id2dirnode` (`0.0.2`)、`python-texttools` (`0.0.6`)
- 通用小工具：`cachedict` (`0.0.7`)、`python-cookietools` (`0.1.5`)、`python-dictattr` (`0.0.4`)、`python-dicttools` (`0.0.5`)、`python-argtools` (`0.0.4`)、`integer_tool` (`0.0.6.1`)、`python-ensure` (`0.0.2`)、`python-property` (`0.0.3`)、`python-startfile` (`0.0.3`)、`python-temporary` (`0.0.1`)、`python-undefined` (`0.0.4`)

以上模块均采用与下述相同的 MIT 许可证。

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
