"""POSIX 转义路径、Glob 翻译与目录节点映射（替代 posixpatht / glob_pattern / id2dirnode）。"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import (
    Callable,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    MutableMapping,
    Sequence,
    ValuesView,
)
from fnmatch import translate as _wildcard_translate
from functools import partial
from re import compile as re_compile
from re import escape as re_escape
from reprlib import recursive_repr
from typing import Final, TypedDict
from weakref import WeakKeyDictionary

__all__ = [
    "AncestorDict",
    "IdToDirnode",
    "escape",
    "joinpath",
    "joins",
    "normpath",
    "path_is_dir_form",
    "splitext",
    "splits",
    "translate_iter",
    "unescape",
]

_CRE_DIR_END_search: Final = re_compile(r"(?P<bss>\\*)/\.{0,2}$").search
_CRE_PART_finditer: Final = re_compile(r"[^\\/]*(?:\\(?s:.)[^\\/]*)*").finditer
_REFIND_BRACKET: Final = re_compile(r"\[[^]]+\]").finditer
_RESUB_DOT: Final = re_compile(r"((?:^|(?<=[^\\]))(?s:\\.)*)\.").sub
_RESUB_REMOVE_WRAP_BRACKET: Final = partial(
    re_compile(r"(?s:\[(.[^]]*)(?<![?*])\])").sub, r"\1"
)


# ---------------------------------------------------------------------------
# POSIX 转义路径工具（替代 _vendor/posixpatht.py）
# ---------------------------------------------------------------------------


def path_is_dir_form(path: str, /, slash_escaped: bool = True) -> bool:
    if path in ("/", "", ".", ".."):
        return True
    if slash_escaped:
        match = _CRE_DIR_END_search(path)
        return match is not None and len(match["bss"]) % 2 == 0
    return path.endswith(("/", "/.", "/.."))


def escape(name: str, /, parse_dots: bool = True) -> str:
    if parse_dots and name in (".", ".."):
        return "\\" + name
    return name.replace("\\", r"\\").replace("/", r"\/")


def unescape(name: str, /, parse_dots: bool = True) -> str:
    if parse_dots and name in (r"\.", r"\.."):
        name = name[1:]
    return name.replace(r"\/", "/").replace(r"\\", "\\")


def joinpath(dirname: str, /, *paths: str, slash_escaped: bool = True) -> str:
    if not paths:
        return dirname
    path = ""
    for part in reversed((dirname, *paths)):
        if not part:
            continue
        if not path:
            path = part
        elif part == "/":
            return part + path
        else:
            if not (part.endswith("/") and path_is_dir_form(part, slash_escaped)):
                part += "/"
            path = part + path
        if path.startswith("/"):
            break
    return path


def joins(
    patht: Sequence[str],
    /,
    parents: int = 0,
    escape: Callable[[str], str] | None = escape,
) -> str:
    parents = max(0, parents)
    if not patht:
        return "/".join(("..",) * parents) if parents else ""
    if escape is None:
        path = "/".join(p for p in patht if p)
    else:
        path = "/".join(escape(p) for p in patht if p)
    if not patht[0]:
        return "/" + path
    if parents:
        return "".join(("../",) * parents) + path
    return path


def splits(
    path: str,
    /,
    unescape: Callable[[str], str] | None = unescape,
    parse_dots: bool = True,
    slash_escaped: bool = True,
) -> tuple[list[str], int]:
    if unescape is globals()["unescape"]:
        unescape = partial(unescape, parse_dots=parse_dots)
    parts: list[str] = []
    is_absolute = path.startswith("/")
    if is_absolute:
        parts.append("")
    if slash_escaped:
        part_it = (m[0].replace(r"\/", "/") for m in _CRE_PART_finditer(path) if m[0])
    else:
        part_it = (p for p in path.split("/") if p)
    parents = 0
    for p in part_it:
        if p == "." and parse_dots:
            continue
        if p == ".." and parse_dots:
            if is_absolute:
                if len(parts) > 1:
                    parts.pop()
            elif parts:
                parts.pop()
            else:
                parents += 1
        elif unescape is None:
            parts.append(p)
        else:
            parts.append(unescape(p))
    return parts, parents


def normpath(
    path: str,
    /,
    parse_dots: bool = True,
    slash_escaped: bool = True,
) -> str:
    parts, parents = splits(
        path, unescape=None, parse_dots=parse_dots, slash_escaped=slash_escaped
    )
    return joins(parts, parents, escape=None)


def splitext(path: str, /, slash_escaped: bool = True) -> tuple[str, str]:
    if path_is_dir_form(path, slash_escaped):
        return path, ""
    if slash_escaped:
        start = 0
        for m in _CRE_PART_finditer(path):
            if m[0]:
                start = m.start()
    else:
        start = path.rfind("/") + 1
    if start == len(path):
        return path, ""
    index = path.rfind(".", start)
    if index == -1 or not path[start:index].strip("."):
        return path, ""
    return path[:index], path[index:]


# ---------------------------------------------------------------------------
# Glob 表达式分段翻译（替代 _vendor/glob_pattern.py）
# ---------------------------------------------------------------------------


def _glob_is_pat(part: str, /) -> bool:
    it = enumerate(part)
    try:
        for _, c in it:
            if c in ("?", "*"):
                return True
            if c == "[":
                _, c2 = next(it)
                if c2 == "]":
                    continue
                i, c3 = next(it)
                if c3 == "]":
                    if c2 in ("?", "*"):
                        return True
                    continue
                if part.find("]", i + 1) > -1:
                    return True
        return False
    except StopIteration:
        return False


def _glob_replace_dots(pat: str, /) -> str:
    if "." not in pat:
        return pat
    chunks: list[str] = []
    last = 0
    for m in _REFIND_BRACKET(pat):
        start, stop = m.span()
        chunks.append(pat[last:start].replace(".", "[^/]"))
        chunks.append(m[0])
        last = stop
    chunks.append(_RESUB_DOT(r"\g<1>[^/]", pat[last:]))
    return "".join(chunks)


def translate_iter(
    pattern: str,
    /,
    allow_escaped_slash: bool = False,
) -> Iterator[tuple[str, str, str]]:
    last_type = ""
    if allow_escaped_slash:
        ls, _ = splits(pattern, parse_dots=False, unescape=None)
    else:
        ls = pattern.split("/")
    for part in ls:
        if not part:
            continue
        orig_part = ""
        if part == "*":
            out = "[^/]*"
            last_type = "star"
        elif len(part) >= 2 and not part.strip("*"):
            if last_type == "dstar":
                continue
            out = "[^/]*(?:/[^/]*)*"
            last_type = "dstar"
        elif _glob_is_pat(part):
            out = _glob_replace_dots(_wildcard_translate(part)[4:-3])
            last_type = "pat"
        else:
            orig_part = _RESUB_REMOVE_WRAP_BRACKET(part)
            out = re_escape(orig_part)
            last_type = "orig"
        yield out, last_type, orig_part


# ---------------------------------------------------------------------------
# 目录 ID -> (名称, 父 ID) 索引（替代 _vendor/id2dirnode.py）
# ---------------------------------------------------------------------------


class AncestorDict(TypedDict):
    id: int
    parent_id: int
    name: str


class _WeakStr(str):
    """支持弱引用的字符串子类。"""


class IdToDirnode(MutableMapping[int, tuple[str, int]]):
    def __init__(
        self,
        data: Mapping[int, tuple[str, int]]
        | Iterable[tuple[int, tuple[str, int]]]
        | None = None,
        /,
    ):
        self.data: dict[int, tuple[str, int]] = {}
        self._pid_to_children: defaultdict[int, WeakKeyDictionary[str, int]] = (
            defaultdict(WeakKeyDictionary)
        )
        if data:
            self.update(data)

    def __contains__(self, key: object, /) -> bool:
        try:
            return key in self.data
        except TypeError:
            return False

    @recursive_repr()
    def __repr__(self, /) -> str:
        cls = type(self)
        return f"{cls.__module__}.{cls.__qualname__}({self.data})"

    def __delitem__(self, cid: int, /) -> None:
        del self.data[cid]

    def __getitem__(self, cid: int, /) -> tuple[str, int]:
        return self.data[cid]

    def __setitem__(self, cid: int, pair: tuple[str, int], /) -> None:
        name, pid = pair
        wname = _WeakStr(name)
        self.data[cid] = (wname, pid)
        self._pid_to_children[pid][wname] = cid

    def __iter__(self, /) -> Iterator[int]:
        return iter(self.data)

    def __len__(self, /) -> int:
        return len(self.data)

    def keys(self, /) -> KeysView[int]:
        return self.data.keys()

    def values(self, /) -> ValuesView[tuple[str, int]]:
        return self.data.values()

    def items(self, /) -> ItemsView[int, tuple[str, int]]:
        return self.data.items()

    def get_name(self, id: int, /) -> str:
        return str(self[id][0])

    def get_parent_id(self, id: int, /) -> int:
        return self[id][1]

    def get_child_id(self, pid: int, name: str, /) -> int:
        return self._pid_to_children[pid][_WeakStr(name)]

    def get_id(self, patht: Sequence[str], /, parent_id: int = 0) -> int:
        if not patht:
            return parent_id
        if not patht[0]:
            parent_id = 0
        pid_to_children = self._pid_to_children
        for name in patht:
            if name:
                parent_id = pid_to_children[parent_id][_WeakStr(name)]
        return parent_id

    def clear(self, top_id: int = 0, /) -> None:
        if top_id:
            self.data.pop(top_id, None)
            if children := self._pid_to_children.pop(top_id, None):
                for cid in children.values():
                    self.clear(cid)
        else:
            self.data.clear()
            self._pid_to_children.clear()

    def get_ancestor(self, id: int = 0, /) -> AncestorDict:
        if not id:
            return {"id": 0, "parent_id": 0, "name": ""}
        name, pid = self[id]
        return {"id": id, "parent_id": pid, "name": str(name)}

    def get_ancestors(self, id: int = 0, /) -> list[AncestorDict]:
        if not id:
            return [self.get_ancestor()]
        ancestors: list[AncestorDict] = []
        while id:
            name, pid = self[id]
            ancestors.append({"id": id, "parent_id": pid, "name": str(name)})
            id = pid
        ancestors.append(self.get_ancestor())
        ancestors.reverse()
        return ancestors

    def get_patht(self, id: int = 0, /) -> list[str]:
        if not id:
            return [""]
        patht: list[str] = []
        while id:
            name, id = self[id]
            patht.append(str(name))
        patht.append("")
        patht.reverse()
        return patht

    def iter_children(self, pid: int = 0, /) -> Iterator[AncestorDict]:
        return (
            {"id": cid, "parent_id": pid, "name": str(name)}
            for name, cid in self._pid_to_children[pid].items()
        )

    def iter_descendants(self, top_id: int = 0, /) -> Iterator[AncestorDict]:
        for attr in self.iter_children(top_id):
            yield attr
            yield from self.iter_descendants(attr["id"])
