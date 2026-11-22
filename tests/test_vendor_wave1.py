"""阶段 1 内联微包（_vendor）单元测试与依赖收敛守卫。"""

import ast
import pathlib
import tomllib

from fundrives.pan115._vendor.argtools import argcount
from fundrives.pan115._vendor.cachedict import LRUDict
from fundrives.pan115._vendor.cookietools import cookies_to_dict, update_cookies
from fundrives.pan115._vendor.dictattr import AttrDict
from fundrives.pan115._vendor.dicttools import (
    KeyLowerDict,
    dict_key_to_lower_merge,
    dict_map,
    get_first,
)
from fundrives.pan115._vendor.ensure import ensure_bytes
from fundrives.pan115._vendor.errno2 import errno, errno2error
from fundrives.pan115._vendor.glob_pattern import translate_iter
from fundrives.pan115._vendor.id2dirnode import IdToDirnode
from fundrives.pan115._vendor.integer_tool import try_parse_int
from fundrives.pan115._vendor.iter_collect import grouped_mapping, iter_keyed_dups
from fundrives.pan115._vendor.p115pickcode import (
    is_valid_pickcode,
    pickcode_to_id,
    to_id,
    to_pickcode,
)
from fundrives.pan115._vendor.posixpatht import escape, joinpath, normpath, splits
from fundrives.pan115._vendor.property import locked_cacheproperty
from fundrives.pan115._vendor.startfile import startfile, startfile_async
from fundrives.pan115._vendor.temporary import temp_globals
from fundrives.pan115._vendor.undefined import Undefined, is_undefined, undefined

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "fundrives" / "pan115"

ELIMINATED_DISTS = {
    "cachedict",
    "errno2",
    "glob_pattern",
    "id2dirnode",
    "integer_tool",
    "iter_collect",
    "p115pickcode",
    "posixpatht",
    "python-argtools",
    "python-cookietools",
    "python-dictattr",
    "python-dicttools",
    "python-encode_uri",
    "python-ensure",
    "python-property",
    "python-startfile",
    "python-temporary",
    "python-undefined",
}

ELIMINATED_MODULES = {
    "argtools",
    "cachedict",
    "cookietools",
    "dictattr",
    "dicttools",
    "encode_uri",
    "ensure",
    "errno2",
    "glob_pattern",
    "id2dirnode",
    "integer_tool",
    "iter_collect",
    "p115pickcode",
    "posixpatht",
    "property",
    "startfile",
    "temporary",
    "undefined",
}


def test_eliminated_deps_not_in_pyproject():
    """阶段 1 已剥离的 18 个外部微包不能再回到 pyproject.toml。"""
    deps = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]["dependencies"]
    declared = {d.split(">=")[0].split("<")[0].split("==")[0].strip() for d in deps}
    leaked = sorted(declared & ELIMINATED_DISTS)
    assert not leaked, f"已内联的依赖又出现在 pyproject.toml: {leaked}"


def test_source_does_not_import_eliminated_external_modules():
    """src/fundrives/pan115/ 内不得再直接 import 已内联的外部微包。"""
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
    from http.cookies import SimpleCookie

    cookies = cookies_to_dict("UID=1; CID=2")
    assert cookies == {"UID": "1", "CID": "2"}
    jar = SimpleCookie("UID=1")
    update_cookies(jar, {"SEID": "3"})
    assert jar["SEID"].value == "3"


def test_cache_and_node_helpers():
    cache = LRUDict(2)
    cache["a"] = 1
    cache["b"] = 2
    cache["c"] = 3
    assert "a" not in cache and list(cache) == ["b", "c"]

    nodes = IdToDirnode()
    nodes[1] = ("docs", 0)
    assert nodes[1] == ("docs", 0)


def test_misc_utilities():
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

    ns = {"x": 1}
    with temp_globals(ns, x=2):
        assert ns["x"] == 2
    assert ns["x"] == 1
