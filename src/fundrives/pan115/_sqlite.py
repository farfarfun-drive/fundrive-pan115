"""轻量级 SQLite 辅助模块（替代 _vendor/sqlitetools.py，仅依赖标准库 sqlite3）。"""

from __future__ import annotations

from collections import ChainMap, UserDict
from collections.abc import Buffer, Callable, Iterable, Iterator, Mapping, Sequence
from contextlib import closing, contextmanager, suppress
from enum import IntEnum
from os import PathLike
from re import compile as re_compile
from sqlite3 import connect as sqlite_connect
from typing import Any, Final, Literal, Self

__all__ = [
    "FetchType",
    "connect",
    "enclose",
    "execute",
    "executescript",
    "find",
    "query",
    "upsert_items",
]

_CRE_COLNAME_sub: Final = re_compile(r" \[[^]]+\]$").sub


class _MappingAsDict(UserDict[Any, Any], dict[Any, Any]):
    def __init__(self, data: Mapping[Any, Any], /):
        self.data = data  # type: ignore[assignment]


class FetchType(IntEnum):
    auto = 0
    any = 1
    one = 2
    dict = 3

    @classmethod
    def ensure(cls, val: Any, /) -> Self:
        if isinstance(val, cls):
            return val
        if isinstance(val, str):
            with suppress(KeyError):
                return cls[val]
        return cls(val)


def enclose(
    name: str | Iterable[str],
    encloser: str | tuple[str, str] = '"',
) -> str:
    if not isinstance(name, str):
        return ".".join(enclose(part, encloser) for part in name)
    if name.isidentifier():
        return name
    if isinstance(encloser, tuple):
        left, right = encloser
        return f"{left}{name}{right}"
    return f"{encloser}{name.replace(encloser, encloser * 2)}{encloser}"


def connect(
    db: Any = ":memory:",
    /,
    check_same_thread: bool = False,
    **connect_kwargs: Any,
) -> Any:
    if isinstance(db, (bytes, str, PathLike)):
        connect_kwargs["check_same_thread"] = check_same_thread
        if isinstance(db, str) and db.startswith("file:"):
            connect_kwargs.setdefault("uri", True)
        return sqlite_connect(db, **connect_kwargs)
    if hasattr(db, "connection"):
        return db.connection
    return db


@contextmanager
def _context_cursor(con: Any, /, isolation_level: str | None = "") -> Iterator[Any]:
    if hasattr(con, "cursor"):
        cursor = con.cursor()
    elif isinstance(con, (bytes, str, PathLike)):
        cursor = connect(con).cursor()
    else:
        cursor = con
    if isolation_level is None:
        yield cursor
        return
    with suppress(Exception):
        cursor.execute(f"BEGIN {isolation_level}")
    try:
        yield cursor
    except BaseException:
        with suppress(Exception):
            cursor.execute("ROLLBACK")
        raise
    else:
        with suppress(Exception):
            cursor.execute("COMMIT")


def _normalize_params(params: Any, /) -> Any:
    if params is None:
        return None
    if isinstance(params, Mapping):
        return params if isinstance(params, dict) else _MappingAsDict(params)
    if isinstance(params, (str, Buffer)) or not isinstance(params, Sequence):
        return (params,)
    return params


def _bind_row_factory(
    cursor: Any,
    /,
    row_factory: None | int | str | FetchType | Callable[..., Any] = None,
) -> Any:
    factory: Callable[..., Any] | None = None
    if row_factory is not None:
        if callable(row_factory):
            factory = row_factory
        else:
            ft = FetchType.ensure(row_factory)
            if ft is FetchType.auto:

                def factory(_cur: Any, record: Any) -> Any:
                    if (
                        isinstance(record, Sequence)
                        and not isinstance(record, (str, Buffer))
                        and len(record) == 1
                    ):
                        return record[0]
                    return record

            elif ft is FetchType.one:

                def factory(_cur: Any, record: Any) -> Any:
                    if not isinstance(record, (str, Buffer)):
                        if isinstance(record, Sequence):
                            return record[0]
                        if isinstance(record, Mapping):
                            return record[next(iter(record))]
                        if isinstance(record, Iterable):
                            return next(iter(record))
                    return record

            elif ft is FetchType.dict:
                try:
                    fields: Sequence[Any] = tuple(
                        _CRE_COLNAME_sub("", f[0]) for f in cursor.description
                    )
                except Exception:
                    fields = range(1 << 15)

                def factory(_cur: Any, record: Any) -> Any:
                    if not isinstance(record, Mapping):
                        return dict(zip(fields, record, strict=False))
                    return record

    if factory is not None:
        if hasattr(cursor, "row_factory"):
            cursor.row_factory = factory
        else:

            def _iter() -> Iterator[Any]:
                try:
                    for record in cursor:
                        yield factory(cursor, record)
                finally:
                    cursor.close()

            return _iter()
    return cursor


def execute(
    con: Any,
    /,
    sql: str,
    params: Any = None,
    executemany: bool = False,
    commit: bool = False,
) -> Any:
    with _context_cursor(con, "" if commit else None) as cursor:
        if executemany and params:
            cursor.executemany(sql, map(_normalize_params, params))
        else:
            norm = _normalize_params(params)
            if norm is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, norm)
        return cursor


def executescript(con: Any, /, sql: str) -> Any:
    with _context_cursor(con, None) as cursor:
        stripped = sql.strip()
        if stripped:
            if hasattr(cursor, "executescript"):
                cursor.executescript(stripped)
            else:
                for stmt in (s.strip() for s in stripped.split(";") if s.strip()):
                    cursor.execute(stmt)
        return cursor


def query(
    con: Any,
    /,
    sql: str,
    params: Any = None,
    row_factory: None | int | str | FetchType | Callable[..., Any] = None,
) -> Any:
    return _bind_row_factory(execute(con, sql, params), row_factory)


def find(
    con: Any,
    /,
    sql: str,
    params: Any = None,
    default: Any = None,
    row_factory: int | str | FetchType | Callable[..., Any] = "auto",
) -> Any:
    with closing(query(con, sql, params)) as cursor:
        record = next(_bind_row_factory(cursor, row_factory), default)
        if isinstance(record, BaseException):
            raise record
        return record


def upsert_items(
    con: Any,
    items: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    /,
    extras: Mapping[str, Any] | None = None,
    table: str = "data",
    fields: Sequence[str] = (),
    on_conflict: Literal["", "ABORT", "FAIL", "IGNORE", "REPLACE", "ROLLBACK"] = "",
    on_conflict_update_fields: Sequence[str] = (),
    where: str = "",
    commit: bool = False,
) -> Any:
    seq: Sequence[Mapping[str, Any]] = (items,) if isinstance(items, Mapping) else items
    if extras:
        seq = [ChainMap(dict(item), extras) for item in seq]
        if fields:
            fields = tuple(dict.fromkeys((*fields, *extras)))
    if not fields:
        fields = tuple(seq[0])
    insert_conflict = f" OR {on_conflict}" if on_conflict else ""
    cols = ",".join(map(enclose, fields))
    placeholders = ",".join(f":{f}" for f in fields)
    sql = f"INSERT{insert_conflict} INTO {enclose(table)}({cols})\nVALUES ({placeholders})"
    if not on_conflict:
        upd_fields = on_conflict_update_fields or fields
        updates = ",".join(f"{enclose(f)}=excluded.{enclose(f)}" for f in upd_fields)
        sql += f"\nON CONFLICT DO UPDATE SET {updates}"
    if where:
        sql += "\nWHERE " + where
    return execute(con, sql, seq, executemany=True, commit=commit)
