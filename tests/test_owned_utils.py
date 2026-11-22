"""自维护基础模块深度单测：_utils / _path / _hash / _sqlite / _iterdir。"""

from __future__ import annotations

import asyncio
import hashlib
import io
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from fundrives.pan115._hash import (
    Ed2kHash,
    ed2k_hash,
    ed2k_hash_async,
    file_digest,
    file_digest_async,
    file_mdigest,
    file_mdigest_async,
)
from fundrives.pan115._iterdir import iterdir_generic, walk_generic
from fundrives.pan115._path import (
    IdToDirnode,
    escape,
    joinpath,
    joins,
    normpath,
    path_is_dir_form,
    splitext,
    splits,
    translate_iter,
    unescape,
)
from fundrives.pan115._sqlite import (
    FetchType,
    connect,
    enclose,
    execute,
    executescript,
    find,
    query,
    upsert_items,
)
from fundrives.pan115._utils import (
    AttrDict,
    KeyLowerDict,
    LRUDict,
    Undefined,
    argcount,
    decorated,
    dict_key_to_lower_merge,
    dict_key_to_lower_update,
    dict_map,
    dict_merge,
    dict_update,
    ensure_buffer,
    ensure_bytes,
    ensure_str,
    errno,
    errno2error,
    format_time,
    funcproperty,
    get,
    get_first,
    grouped_mapping,
    has_keyword_arg,
    int_to_bytes,
    is_undefined,
    iter_items,
    iter_keyed_dups,
    locked_cacheproperty,
    optional,
    try_parse_int,
    undefined,
)

# ---------------------------------------------------------------------------
# _utils: Undefined / Property / Dict / LRU / Iter / Arg / Deco / Errno
# ---------------------------------------------------------------------------


def test_undefined_singleton_and_semantics():
    assert Undefined() is undefined
    assert is_undefined(undefined)
    assert not is_undefined(None)
    assert not bool(undefined)
    assert repr(undefined) == "undefined"
    assert hash(undefined) == 0
    assert undefined == Undefined()
    assert undefined != None  # noqa: E711
    assert undefined is not False
    assert (undefined == 0) is False


def test_funcproperty_and_locked_cacheproperty_thread_safety():
    class Box:
        def __init__(self, x: int):
            self.x = x
            self.calls = 0

        @funcproperty
        def doubled(self) -> int:
            return self.x * 2

        @locked_cacheproperty
        def expensive(self) -> int:
            time.sleep(0.02)
            self.calls += 1
            return self.x * 10

    assert isinstance(Box.doubled, funcproperty)
    assert isinstance(Box.expensive, locked_cacheproperty)
    box = Box(7)
    assert box.doubled == 14
    box.x = 9
    assert box.doubled == 18

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: box.expensive, range(16)))
    assert results == [90] * 16
    assert box.calls == 1


def test_lru_dict_eviction_default_factory_copy_and_update():
    # maxsize=0 表示不淘汰
    unbounded: LRUDict[str, int] = LRUDict(0)
    for i in range(20):
        unbounded[f"k{i}"] = i
    assert len(unbounded) == 20

    # 读取刷新热点顺序，更新已有键同样刷新热点
    lru: LRUDict[str, int] = LRUDict(3)
    lru["a"] = 1
    lru["b"] = 2
    lru["c"] = 3
    assert lru["a"] == 1  # order: b, c, a
    lru["d"] = 4  # evicts b -> order: c, a, d
    assert list(lru) == ["c", "a", "d"]
    lru["c"] = 30  # refresh c -> order: a, d, c
    lru["e"] = 5  # evicts a -> order: d, c, e
    assert list(lru) == ["d", "c", "e"] and lru["c"] == 30

    # popitem 弹出最旧键；空字典抛 KeyError
    assert lru.popitem() == ("d", 4)
    lru.discard("nonexistent")
    lru.discard("e")
    assert list(lru) == ["c"]
    lru.clear()
    with pytest.raises(KeyError):
        lru.popitem()

    # default_factory + copy + update
    locks: LRUDict[int, threading.Lock] = LRUDict(2, default_factory=threading.Lock)
    l1 = locks[1]
    l2 = locks[2]
    assert locks[1] is l1  # refresh 1
    _ = locks[3]  # evicts 2
    assert 2 not in locks and 1 in locks and 3 in locks
    assert locks[2] is not l2

    copied = locks.copy()
    assert copied.maxsize == 2 and copied.default_factory is threading.Lock
    copied.update({"x": threading.Lock(), "y": threading.Lock(), "z": threading.Lock()})
    assert len(copied) == 2 and list(copied) == ["y", "z"]


def test_dict_helpers_and_key_lower_dict():
    ad = AttrDict(a=1, b=2)
    assert ad.a == 1 and ad["b"] == 2
    ad.c = 3
    assert ad["c"] == 3 and ad == {"a": 1, "b": 2, "c": 3}
    assert hash(ad) == id(ad)

    kd: KeyLowerDict[str, str] = KeyLowerDict({"Content-Type": "text/plain"}, X_Id="1")
    assert "CONTENT-TYPE" in kd and kd["content-type"] == "text/plain"
    assert kd.get("X_ID") == "1" and kd.get("missing", "def") == "def"
    assert kd.setdefault("Accept", "*/*") == "*/*"
    assert kd.setdefault("ACCEPT", "ignored") == "*/*"
    assert kd.pop("X_ID") == "1"
    assert kd.pop("X_ID", None) is None
    del kd["ACCEPT"]
    assert "accept" not in kd

    # dict_merge 先来优先，原地修改；dict_update 后来覆盖
    base = {"a": 1}
    merged = dict_merge(base, {"a": 99, "b": 2}, [("c", 3)], b=200, d=4)
    assert merged is base and merged == {"a": 1, "b": 2, "c": 3, "d": 4}
    updated = dict_update({"a": 1}, {"a": 2, "b": 3}, b=4)
    assert updated == {"a": 2, "b": 4}

    assert dict_key_to_lower_merge({"A": 1}, {"a": 2, "B": 3}, b=4, C=5) == {
        "a": 1,
        "b": 3,
        "c": 5,
    }
    assert dict_key_to_lower_update({"A": 1}, {"a": 2, "B": 3}, b=4, C=5) == {
        "a": 2,
        "b": 4,
        "c": 5,
    }
    assert dict_map({"a": 1, "b": 2}, key={"a": "x"}, value=lambda v: v * 10) == {
        "x": 10,
        "b": 20,
    }
    assert list(iter_items([("k", 1)])) == [("k", 1)]
    assert get([("k", 1), ("m", 2)], "m") == 2
    assert get({"a": 1}, "x", default=0) == 0
    with pytest.raises(KeyError):
        get({"a": 1}, "x")
    assert get_first({"b": 2}, "a", "b") == 2
    assert get_first({"b": 2}, "a", default=None) is None
    with pytest.raises(KeyError):
        get_first({"b": 2}, "a", "c")


def test_parse_ensure_and_format_time():
    assert try_parse_int(10) == 10
    assert try_parse_int("0") == 0
    assert try_parse_int("42") == 42
    assert try_parse_int("007") == "007"  # 前导零保留字符串
    assert try_parse_int("true") is True
    assert try_parse_int("false") is False
    assert try_parse_int("abc") == "abc"
    assert try_parse_int(b"\x01\x00", check_types=None) == 256
    assert int_to_bytes(256) == b"\x01\x00"

    assert ensure_str(b"hi") == "hi"
    assert ensure_str(123) == "123"
    assert ensure_bytes("hi") == b"hi"
    assert ensure_bytes(memoryview(b"mv")) == b"mv"
    assert ensure_bytes(256) == b"\x01\x00"
    assert bytes(ensure_buffer("buf")) == b"buf"

    assert format_time(5) == "00:05"
    assert format_time(65) == "01:05"
    assert format_time(3661) == "01:01:01"
    assert format_time(90061) == "1d01:01:01"
    assert format_time(1.5).startswith("00:01.5")


def test_grouped_mapping_and_iter_keyed_dups_sync_and_async():
    data = [(1, "a"), (2, "x"), (1, "b"), (1, "c"), (2, "y")]
    assert grouped_mapping(data) == {1: ["a", "b", "c"], 2: ["x", "y"]}
    assert grouped_mapping(["aa", "ab", "ba"], key=lambda s: s[0]) == {
        "a": ["aa", "ab"],
        "b": ["ba"],
    }

    # keep_first 四种模式：None / True / False / callable
    assert list(iter_keyed_dups(data, keep_first=None)) == [
        (1, "a"),
        (1, "b"),
        (1, "c"),
        (2, "x"),
        (2, "y"),
    ]
    assert list(iter_keyed_dups(data, keep_first=True)) == [
        (1, "b"),
        (1, "c"),
        (2, "y"),
    ]
    assert list(iter_keyed_dups(data, keep_first=False)) == [
        (1, "a"),
        (1, "b"),
        (2, "x"),
    ]
    scored = [("k", 30), ("k", 10), ("k", 20)]
    # 保留最小分数 10，其余 30 和 20 作为重复项产出
    assert list(iter_keyed_dups(scored, keep_first=lambda v: v)) == [
        ("k", 30),
        ("k", 20),
    ]

    async def _aiter(items):
        for item in items:
            yield item

    async def _verify_async():
        assert await grouped_mapping(_aiter(data)) == {
            1: ["a", "b", "c"],
            2: ["x", "y"],
        }
        assert [x async for x in iter_keyed_dups(_aiter(data), keep_first=None)] == [
            (1, "a"),
            (1, "b"),
            (1, "c"),
            (2, "x"),
            (2, "y"),
        ]
        assert [x async for x in iter_keyed_dups(_aiter(data), keep_first=False)] == [
            (1, "a"),
            (1, "b"),
            (2, "x"),
        ]
        assert [
            x async for x in iter_keyed_dups(_aiter(scored), keep_first=lambda v: v)
        ] == [("k", 30), ("k", 20)]

    asyncio.run(_verify_async())


def test_argtools_decotools_and_errno():
    from functools import partial

    def fn(a, b, *, c=1):
        return a + b + c

    assert argcount(fn) == 2
    assert argcount(partial(fn, 1)) == 1
    assert has_keyword_arg(fn, "b") is True
    assert has_keyword_arg(fn, "c") is True
    assert has_keyword_arg(fn, "z") is False
    assert has_keyword_arg(lambda **kw: kw, "anything") is True

    @decorated
    def add_one(f, /, *args, **kw):
        return f(*args, **kw) + 1

    @add_one
    def mul(x, y):
        return x * y

    assert mul(3, 4) == 13

    @optional
    def scale(f, /, factor=2):
        def wrapper(x):
            return f(x) * factor

        return wrapper

    @scale
    def f1(x):
        return x + 1

    @scale(factor=5)
    def f2(x):
        return x + 1

    assert f1(3) == 8 and f2(3) == 20

    assert errno.of("ENOENT") is errno.ENOENT
    assert errno.of(2) is errno.ENOENT
    assert isinstance(errno.ENOENT.error("missing"), FileNotFoundError)
    with pytest.raises(PermissionError):
        errno.EACCES.throw("denied")
    assert errno2error[errno.ETIMEDOUT] is TimeoutError


# ---------------------------------------------------------------------------
# _path: POSIX escaped path / glob / IdToDirnode
# ---------------------------------------------------------------------------


def test_posix_path_glob_and_id2dirnode():
    assert escape("a/b\\c") == r"a\/b\\c"
    assert unescape(r"a\/b\\c") == "a/b\\c"
    assert escape(".") == r"\." and unescape(r"\.") == "."
    assert escape("..") == r"\.." and unescape(r"\..") == ".."

    assert path_is_dir_form("/") is True
    assert path_is_dir_form("/a/b/") is True
    assert path_is_dir_form(r"/a/b\/") is False
    assert path_is_dir_form(r"/a/b\\/") is True
    assert path_is_dir_form("/a/b/..") is True

    assert joinpath("/a/b", "c", "d.txt") == "/a/b/c/d.txt"
    assert joinpath("/a/b", "/root/x") == "/root/x"
    assert normpath("/a/b/../c/./d/") == "/a/c/d"
    assert normpath("a/../../b") == "../b"
    assert splits("/a/b\\/c/d") == (["", "a", "b/c", "d"], 0)
    assert joins(["", "a", "b/c"]) == r"/a/b\/c"
    assert splitext("/dir/file.tar.gz") == ("/dir/file.tar", ".gz")
    assert splitext("/dir/.env") == ("/dir/.env", "")
    assert splitext("/dir/sub/") == ("/dir/sub/", "")

    # glob translate_iter: 连续 ** 合并、*、通配符、字面量
    parts = list(translate_iter("a/**/**/*.py"))
    assert [t for _, t, _ in parts] == ["orig", "dstar", "pat"]
    assert parts[0][2] == "a"

    # IdToDirnode 完整树索引
    nodes = IdToDirnode({1: ("docs", 0), 2: ("2026", 1), 3: ("notes", 2)})
    assert nodes.get_name(3) == "notes"
    assert nodes.get_parent_id(3) == 2
    assert nodes.get_child_id(1, "2026") == 2
    assert nodes.get_id(["", "docs", "2026", "notes"]) == 3
    assert nodes.get_patht(3) == ["", "docs", "2026", "notes"]
    assert [a["name"] for a in nodes.get_ancestors(3)] == ["", "docs", "2026", "notes"]
    assert [d["id"] for d in nodes.iter_descendants(1)] == [2, 3]
    nodes.clear(2)
    assert 2 not in nodes and 3 not in nodes and 1 in nodes


# ---------------------------------------------------------------------------
# _hash: Ed2kHash / file_digest / file_mdigest (sync & async)
# ---------------------------------------------------------------------------


def test_hash_ed2k_and_file_mdigest_sync_and_async():
    payload = b"fundrive-pan115-verification-payload" * 100
    expected_md5 = hashlib.md5(payload).hexdigest()
    expected_sha1 = hashlib.sha1(payload).hexdigest()

    # 流式 Ed2kHash 与一次性 ed2k_hash / ed2k_hash_async 结果严格一致
    h = Ed2kHash()
    for i in range(0, len(payload), 137):
        h.update(payload[i : i + 137])
    size_s, ed2k_s = ed2k_hash(io.BytesIO(payload))
    assert size_s == len(payload)
    assert ed2k_s == h.hexdigest()

    # 空文件边界
    empty_size, empty_ed2k = ed2k_hash(b"")
    assert empty_size == 0 and empty_ed2k == Ed2kHash(b"").hexdigest()

    # file_mdigest 同时计算 md5 + sha1 + crc32 + ed2k + callback
    progressed: list[int] = []
    total, (d_md5, d_sha1, d_crc, d_ed2k) = file_mdigest(
        io.BytesIO(payload),
        "md5",
        "sha1",
        "crc32",
        "ed2k",
        chunksize=256,
        callback=progressed.append,
    )
    assert total == len(payload)
    assert sum(progressed) == len(payload)
    assert d_md5.hexdigest() == expected_md5
    assert d_sha1.hexdigest() == expected_sha1
    assert isinstance(d_crc, int) and d_crc != 0
    assert d_ed2k.hexdigest() == ed2k_s

    # start / stop 切片（含负索引）
    sub_total, sub_sha1 = file_digest(
        io.BytesIO(b"0123456789"), "sha1", start=2, stop=-2
    )
    assert sub_total == 6
    assert sub_sha1.hexdigest() == hashlib.sha1(b"234567").hexdigest()

    # 异步路径验证
    async def _verify_async():
        async def _chunks():
            for i in range(0, len(payload), 300):
                yield payload[i : i + 300]

        size_a, ed2k_a = await ed2k_hash_async(io.BytesIO(payload))
        assert size_a == len(payload) and ed2k_a == ed2k_s

        t_a, (a_md5, a_sha1, a_ed2k) = await file_mdigest_async(
            _chunks(), "md5", "sha1", "ed2k"
        )
        assert t_a == len(payload)
        assert a_md5.hexdigest() == expected_md5
        assert a_sha1.hexdigest() == expected_sha1
        assert a_ed2k.hexdigest() == ed2k_s

        t_single, single_sha1 = await file_digest_async(
            io.BytesIO(b"0123456789"), "sha1", start=2, stop=8
        )
        assert t_single == 6
        assert single_sha1.hexdigest() == hashlib.sha1(b"234567").hexdigest()

    asyncio.run(_verify_async())


# ---------------------------------------------------------------------------
# _sqlite: connect / executescript / query / find / upsert_items / rollback
# ---------------------------------------------------------------------------


def test_sqlite_full_crud_fetch_types_and_upsert():
    assert enclose("normal_col") == "normal_col"
    assert enclose("bad col") == '"bad col"'
    assert enclose(("db", "my table")) == 'db."my table"'

    con = connect(":memory:")
    try:
        executescript(
            con,
            """
            CREATE TABLE data (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                tag TEXT DEFAULT ''
            );
            """,
        )
        upsert_items(
            con,
            [{"id": 1, "name": "alpha"}, {"id": 2, "name": "beta"}],
            extras={"tag": "v1"},
            commit=True,
        )
        # 冲突更新
        upsert_items(
            con,
            {"id": 1, "name": "alpha-v2", "tag": "v2"},
            on_conflict_update_fields=("name", "tag"),
            commit=True,
        )
        # IGNORE 模式不覆盖已有记录
        upsert_items(
            con,
            {"id": 1, "name": "should-not-overwrite", "tag": "v9"},
            on_conflict="IGNORE",
            commit=True,
        )

        # FetchType: dict / auto / one / any
        rows_dict = list(
            query(con, "SELECT id, name, tag FROM data ORDER BY id", row_factory="dict")
        )
        assert rows_dict == [
            {"id": 1, "name": "alpha-v2", "tag": "v2"},
            {"id": 2, "name": "beta", "tag": "v1"},
        ]
        assert (
            find(
                con, "SELECT name FROM data WHERE id = ?", 1, row_factory=FetchType.auto
            )
            == "alpha-v2"
        )
        assert (
            find(con, "SELECT id, name FROM data WHERE id = ?", 1, row_factory="one")
            == 1
        )
        assert find(
            con, "SELECT id, name FROM data WHERE id = ?", 1, row_factory="any"
        ) == (1, "alpha-v2")
        assert (
            find(con, "SELECT name FROM data WHERE id = ?", 999, default="missing")
            == "missing"
        )

        # default 为异常对象时抛出
        with pytest.raises(LookupError):
            find(
                con,
                "SELECT name FROM data WHERE id = ?",
                999,
                default=LookupError("nope"),
            )

        # 事务失败回滚
        with pytest.raises(sqlite3.IntegrityError):
            execute(
                con,
                "INSERT INTO data (id, name) VALUES (?, ?)",
                (1, "dup"),
                commit=True,
            )
        assert find(con, "SELECT count(*) FROM data") == 2
    finally:
        con.close()


# ---------------------------------------------------------------------------
# _iterdir: DFS/BFS × sync/async × predicate(6 modes) × depth × onerror
# ---------------------------------------------------------------------------


def test_iterdir_and_walk_all_modes_sync_and_async():
    tree = {
        "root": ["d1", "d2", "f0"],
        "d1": ["d1_sub", "f1"],
        "d1_sub": ["f1_deep"],
        "d2": ["f2"],
    }

    def ls(node):
        return tree.get(node, [])

    def isdir(node):
        return node in tree

    # DFS topdown=True / topdown=False / BFS topdown=None
    dfs_top = list(iterdir_generic("root", ls, topdown=True, max_depth=-1, isdir=isdir))
    assert dfs_top == ["d1", "d1_sub", "f1_deep", "f1", "d2", "f2", "f0"]

    dfs_bot = list(
        iterdir_generic("root", ls, topdown=False, max_depth=-1, isdir=isdir)
    )
    assert dfs_bot == ["f1_deep", "d1_sub", "f1", "d1", "f2", "d2", "f0"]

    bfs = list(iterdir_generic("root", ls, topdown=None, max_depth=-1, isdir=isdir))
    assert bfs == ["d1", "d2", "f0", "d1_sub", "f1", "f2", "f1_deep"]

    # min_depth / max_depth
    depth2 = list(
        iterdir_generic("root", ls, topdown=None, min_depth=2, max_depth=2, isdir=isdir)
    )
    assert depth2 == ["d1_sub", "f1", "f2"]

    # predicate=True (仅文件) / predicate=False (仅目录)
    only_files = list(
        iterdir_generic("root", ls, max_depth=-1, isdir=isdir, predicate=True)
    )
    assert only_files == ["f1_deep", "f1", "f2", "f0"]
    only_dirs = list(
        iterdir_generic("root", ls, max_depth=-1, isdir=isdir, predicate=False)
    )
    assert only_dirs == ["d1", "d1_sub", "d2"]

    # predicate 返回 int 1（输出但剪枝子树）与 int 0（跳过且剪枝子树）
    def custom_pred(node):
        if node == "d1":
            return 1  # 输出 d1，但不再进入 d1 子树
        if node == "d2":
            return 0  # 跳过 d2 且不进入 d2 子树
        return True

    pruned = list(
        iterdir_generic("root", ls, max_depth=-1, isdir=isdir, predicate=custom_pred)
    )
    assert pruned == ["d1", "f0"]

    # onerror 回调捕获 OSError
    errors: list[OSError] = []

    def flaky_ls(node):
        if node == "d2":
            raise PermissionError("blocked")
        return ls(node)

    res = list(
        iterdir_generic(
            "root", flaky_ls, max_depth=-1, isdir=isdir, onerror=errors.append
        )
    )
    assert "d2" in res and "f2" not in res and len(errors) == 1

    # walk_generic BFS & DFS
    walked_bfs = list(walk_generic("root", ls, topdown=None, max_depth=-1, isdir=isdir))
    assert walked_bfs[0] == ("root", ["d1", "d2"], ["f0"])
    assert walked_bfs[1] == ("d1", ["d1_sub"], ["f1"])

    # 异步双路径验证
    async def als(node):
        for item in ls(node):
            yield item

    async def _verify_async():
        a_dfs = [
            x
            async for x in iterdir_generic(
                "root", als, topdown=True, max_depth=-1, isdir=isdir, async_=True
            )
        ]
        assert a_dfs == dfs_top
        a_bfs = [
            x
            async for x in iterdir_generic(
                "root", als, topdown=None, max_depth=-1, isdir=isdir, async_=True
            )
        ]
        assert a_bfs == bfs
        a_pruned = [
            x
            async for x in iterdir_generic(
                "root",
                als,
                max_depth=-1,
                isdir=isdir,
                predicate=custom_pred,
                async_=True,
            )
        ]
        assert a_pruned == ["d1", "f0"]
        a_walk = [
            x
            async for x in walk_generic(
                "root", als, topdown=None, max_depth=-1, isdir=isdir, async_=True
            )
        ]
        assert a_walk == walked_bfs

    asyncio.run(_verify_async())
