# fundrive-pan115

115 网盘 Python API 封装（`fundrives.pan115`），从上游 [`p115client`](https://github.com/ChenyangGao/p115client)（`0.0.9.6.5.1`）完整迁入并自主维护，供 [fundrive](https://github.com/farfarfun-drive/fundrive) 及其他项目以统一命名空间稳定接入 115 网盘，避免受上游高频破坏性变更影响。

## 安装

本项目要求 Python 3.12 或更高版本。

```bash
pip install fundrive-pan115
# 或
uv add fundrive-pan115
```

## 快速开始

```python
from pathlib import Path
from fundrives.pan115 import P115Client

# 方式一：使用 Cookie 字符串
client = P115Client(cookies="UID=...; CID=...; SEID=...; KID=...")

# 方式二：使用 Cookie 文件并支持扫码/续期
client = P115Client(Path("~/115-cookies.txt").expanduser(), app="qandroid")
client.login()

# 列出根目录文件
resp = client.fs_files(0)
print(resp)
```

## 开发

安装开发依赖并运行检查与测试：

```bash
uv sync --group dev
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest -v
```

构建发行包：

```bash
uv build
```

## 演进路线

1. **阶段 0（已完成）**：完整迁入 `p115client 0.0.9.6.5.1` 至 `fundrives.pan115` 命名空间，保持 API 100% 兼容，隔离上游高频改动。
2. **阶段 1 & 2（已完成）**：移除未使用的 `python-encode_uri`，并将全部 35 个上游微包（`p115cipher` / `p115oss` / `p115pickcode` / `python-*` / `urllib3_future_request` 等）内联至 `fundrives.pan115._vendor/`，直接依赖从 37 个收敛至 **10 个主流标准生态包**，实现 **0 个上游作者微包依赖**。
3. **后续持续演进**：按需精简未用模块、将 `urllib3-future` 替换为标准 `requests`/`httpx` 并逐步收紧 `per-file-ignores`。

## 命名空间说明

本包与 `fundrive-alipan`、`fundrive-baidu`、`fundrive-lanzou`、`fundrive-quark` 共用 PEP 420 隐式命名空间包 `fundrives`，**不得**在 `src/fundrives/` 下添加 `__init__.py`。

## 来源说明与第三方协议

`src/fundrives/pan115/` 源码派生自 [p115client](https://github.com/ChenyangGao/p115client)（版本 `0.0.9.6.5.1`），原始协议为 **MIT，Copyright (c) 2024 ChenyangGao**。完整声明见 [THIRD_PARTY_NOTICE.md](THIRD_PARTY_NOTICE.md)。

---

## 关于 farfarfun-drive

[farfarfun](https://github.com/farfarfun) 的网盘 / 云存储产品线：以
[fundrive](https://github.com/farfarfun-drive/fundrive) 的统一 `BaseDrive` 接口为核心，
配套各网盘的独立驱动包与蓝奏云 SDK / 桌面客户端。

- 🏠 组织主页：<https://github.com/farfarfun-drive>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
