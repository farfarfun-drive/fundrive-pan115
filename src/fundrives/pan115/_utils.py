"""fundrive-pan115 内部通用工具集（仅基于 Python 标准库）。

集中替代早期从上游内联的 12 个小微包：
cachedict / dictattr / dicttools / ensure / integer_tool / iter_collect /
property / socket_keepalive / startfile / temporary / texttools / undefined。
"""

from __future__ import annotations

import os
import subprocess
from asyncio import create_subprocess_exec, create_subprocess_shell, to_thread
from collections import UserString
from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Buffer,
    Callable,
    Coroutine,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
)
from enum import IntEnum
from functools import partial, wraps
from functools import update_wrapper as _update_wrapper
from inspect import Parameter, getfullargspec, signature
from platform import system
from shutil import which
from threading import Lock
from types import GenericAlias, MethodType, MethodWrapperType
from typing import (
    Any,
    Final,
    Literal,
    Never,
    Protocol,
    Self,
    SupportsInt,
    TypeIs,
    cast,
    final,
)

__all__ = [
    "AttrDict",
    "KeyLowerDict",
    "LRUDict",
    "SupportsLT",
    "Undefined",
    "argcount",
    "decorated",
    "dict_key_to_lower_merge",
    "dict_key_to_lower_update",
    "dict_map",
    "dict_merge",
    "dict_update",
    "ensure_buffer",
    "ensure_bytes",
    "ensure_str",
    "errno",
    "errno2error",
    "format_time",
    "funcproperty",
    "get",
    "get_first",
    "grouped_mapping",
    "has_keyword_arg",
    "int_to_bytes",
    "is_undefined",
    "iter_items",
    "iter_keyed_dups",
    "locked_cacheproperty",
    "optional",
    "startfile",
    "startfile_async",
    "try_parse_int",
    "undefined",
]


# ---------------------------------------------------------------------------
# Undefined 哨兵对象（替代 _vendor/undefined.py）
# ---------------------------------------------------------------------------


@final
class Undefined:
    """类似 None 的缺失值哨兵单例。"""

    __slots__: tuple[str, ...] = ()
    __instance__: Self

    def __new__(cls, /) -> Self:
        inst = cls.__dict__.get("__instance__")
        if inst is None:
            inst = super().__new__(cls)
            cls.__instance__ = inst
        return inst

    def __bool__(self, /) -> bool:
        return False

    def __eq__(self, other: object, /) -> bool:
        return True if self is other else NotImplemented

    def __hash__(self, /) -> int:
        return 0

    def __repr__(self, /) -> str:
        return "undefined"


undefined: Final[Undefined] = Undefined()


def is_undefined(o: object, /) -> TypeIs[Undefined]:
    return isinstance(o, Undefined)


# ---------------------------------------------------------------------------
# 属性描述符（替代 _vendor/property.py）
# ---------------------------------------------------------------------------


class funcproperty:
    """将可调用对象包装为只读非数据描述符。"""

    def __init__(self, func: Callable[..., Any], /):
        self.__func__ = func
        self.__name__ = getattr(func, "__name__", "")
        self.__doc__ = getattr(func, "__doc__", None)
        self.__is_method__ = isinstance(func, (staticmethod, classmethod, MethodType))

    def __repr__(self, /) -> str:
        return f"{type(self).__qualname__}({self.__func__!r})"

    def __set_name__(self, cls: type, name: str, /) -> None:
        self.__name__ = name

    def __get__(self, instance: Any, cls: type | None = None, /) -> Any:
        if instance is None:
            return self
        if self.__is_method__:
            return self.__func__()
        return self.__func__(instance)

    __class_getitem__: classmethod[Any, Any, Any] = classmethod(GenericAlias)


class locked_cacheproperty(funcproperty):
    """线程安全的实例级缓存属性。"""

    def __init__(self, func: Callable[..., Any], /):
        super().__init__(func)
        self._locks: dict[Any, Lock] = {}
        self._meta_lock = Lock()

    def __get__(self, instance: Any, cls: type | None = None, /) -> Any:
        if instance is None:
            return self
        name = self.__name__
        if name in instance.__dict__:
            return instance.__dict__[name]
        with self._meta_lock:
            lock = self._locks.setdefault(instance, Lock())
        with lock:
            if name in instance.__dict__:
                return instance.__dict__[name]
            val = self.__func__() if self.__is_method__ else self.__func__(instance)
            instance.__dict__[name] = val
            return val


# ---------------------------------------------------------------------------
# 字典与缓存容器（替代 _vendor/dictattr.py, dicttools.py, cachedict.py）
# ---------------------------------------------------------------------------


class AttrDict[K, V](dict[K, V]):
    """支持通过属性读写键值的 dict 子类。"""

    def __init__(self, /, *args: Any, **kwds: Any):
        super().__init__(*args, **kwds)
        self.__dict__ = self  # type: ignore[assignment]

    def __hash__(self, /) -> int:  # type: ignore[override]
        return id(self)

    def __eq__(self, value: object, /) -> bool:
        return self is value or super().__eq__(value)


class LRUDict[K: Hashable, V](dict[K, V]):
    """支持 maxsize 淘汰与 default_factory 的 LRU 字典。"""

    __slots__ = ("default_factory", "maxsize")

    def __init__(
        self,
        maxsize: int = 0,
        /,
        *,
        default_factory: Callable[[], V] | None = None,
    ):
        super().__init__()
        self.maxsize = maxsize
        self.default_factory = default_factory

    def _evict_if_needed(self) -> None:
        maxsize = self.maxsize
        if maxsize > 0:
            while len(self) > maxsize:
                super().__delitem__(next(iter(self)))

    def __missing__(self, key: K, /) -> V:
        if self.default_factory is None:
            raise KeyError(key)
        val = self.default_factory()
        self[key] = val
        return val

    def __getitem__(self, key: K, /) -> V:
        if super().__contains__(key):
            val = super().__getitem__(key)
            super().__delitem__(key)
            super().__setitem__(key, val)
            return val
        return self.__missing__(key)

    def __setitem__(self, key: K, value: V, /) -> None:
        if super().__contains__(key):
            super().__delitem__(key)
        super().__setitem__(key, value)
        self._evict_if_needed()

    def discard(self, key: Any, /) -> None:
        super().pop(key, None)

    def popitem(self, /) -> tuple[K, V]:
        if not self:
            raise KeyError(f"{self!r} is empty")
        key = next(iter(self))
        return key, self.pop(key)

    def update(self, *args: Any, **kwds: Any) -> None:  # type: ignore[override]
        for arg in args:
            if arg:
                for k, v in iter_items(arg):
                    self[k] = v
        for k, v in kwds.items():
            self[k] = v  # type: ignore[index]

    def copy(self, /) -> Self:
        inst = type(self)(self.maxsize, default_factory=self.default_factory)
        dict.update(inst, self)
        return inst


def _lower_key(k: Any) -> Any:
    return k.lower() if hasattr(k, "lower") else k


def iter_items[K, V](
    m: Mapping[K, V] | Iterable[tuple[K, V]], /
) -> Iterator[tuple[K, V]]:
    if isinstance(m, Mapping):
        return iter(m.items())
    return iter(m)


class KeyLowerDict[K, V](dict[K, V]):
    """键自动转小写的 dict 子类（常用于 HTTP Header）。"""

    def __init__(self, /, *args: Any, **kwds: Any):
        super().__init__()
        self.update(*args, **kwds)

    def __contains__(self, key: object, /) -> bool:
        try:
            return super().__contains__(_lower_key(key))
        except TypeError:
            return False

    def __delitem__(self, key: K, /) -> None:
        super().__delitem__(_lower_key(key))

    def __getitem__(self, key: K, /) -> V:
        return super().__getitem__(_lower_key(key))

    def __setitem__(self, key: K, value: V, /) -> None:
        super().__setitem__(_lower_key(key), value)

    def get(self, key: K, /, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key: K, /, default: Any = undefined) -> Any:
        k = _lower_key(key)
        if default is undefined:
            return super().pop(k)
        return super().pop(k, default)

    def setdefault(self, key: K, /, default: Any = None) -> Any:
        return super().setdefault(_lower_key(key), default)

    def update(self, /, *args: Any, **kwds: Any) -> None:
        for arg in args:
            if arg:
                for k, v in iter_items(arg):
                    self[k] = v
        for k, v in kwds.items():
            self[k] = v  # type: ignore[index]


def get[K, V, V2](
    m: Mapping[K, V] | Iterable[tuple[K, V]],
    k: Any,
    /,
    default: Undefined | V2 = undefined,
) -> V | V2:
    if isinstance(m, Mapping):
        try:
            return m[k]
        except (LookupError, TypeError):
            pass
    else:
        for key, val in m:
            if key is k or key == k:
                return val
    if default is undefined:
        raise KeyError(k)
    return cast(V2, default)


def get_first[K, V, V2](
    m: Mapping[K, V],
    /,
    *keys: Any,
    default: Undefined | V2 = undefined,
) -> V | V2:
    for k in keys:
        try:
            return m[k]
        except (LookupError, TypeError):
            pass
    if default is undefined:
        raise KeyError(*keys)
    return cast(V2, default)


def dict_map[K, V, K2, V2](
    m: Mapping[K, V] | Iterable[tuple[K, V]],
    /,
    key: None | Callable[[K], K2] | Mapping[K, K2] = None,
    value: None | Callable[[V], V2] | Mapping[V, V2] = None,
) -> dict[Any, Any]:
    key_fn: Callable[[Any], Any] | None = (
        (lambda k: key.get(k, k)) if isinstance(key, Mapping) else key
    )
    val_fn: Callable[[Any], Any] | None = (
        (lambda v: value.get(v, v)) if isinstance(value, Mapping) else value
    )
    if key_fn is None:
        if val_fn is None:
            return dict(m)
        return {k: val_fn(v) for k, v in iter_items(m)}
    if val_fn is None:
        return {key_fn(k): v for k, v in iter_items(m)}
    return {key_fn(k): val_fn(v) for k, v in iter_items(m)}


def dict_merge[K, V](
    m: Mapping[K, V] | Iterable[tuple[K, V]],
    /,
    *ms: Mapping[K, V] | Iterable[tuple[K, V]],
    **kwds: Any,
) -> dict[K, V]:
    d: dict[Any, Any] = m if isinstance(m, dict) else dict(m)
    for other in ms:
        for k, v in iter_items(other):
            d.setdefault(k, v)
    for k, v in kwds.items():
        d.setdefault(k, v)
    return d


def dict_update[K, V](
    m: Mapping[K, V] | Iterable[tuple[K, V]],
    /,
    *ms: Mapping[K, V] | Iterable[tuple[K, V]],
    **kwds: Any,
) -> dict[K, V]:
    d: dict[Any, Any] = m if isinstance(m, dict) else dict(m)
    for other in ms:
        d.update(other)
    if kwds:
        d.update(kwds)
    return d


def dict_key_to_lower_merge[K, V](
    m: Mapping[K, V] | Iterable[tuple[K, V]],
    /,
    *ms: Mapping[K, V] | Iterable[tuple[K, V]],
    **kwds: Any,
) -> dict[K, V]:
    d: dict[Any, Any] = {}
    for src in (m, *ms):
        for k, v in iter_items(src):
            d.setdefault(_lower_key(k), v)
    for k, v in kwds.items():
        d.setdefault(_lower_key(k), v)
    return d


def dict_key_to_lower_update[K, V](
    m: Mapping[K, V] | Iterable[tuple[K, V]],
    /,
    *ms: Mapping[K, V] | Iterable[tuple[K, V]],
    **kwds: Any,
) -> dict[K, V]:
    d: dict[Any, Any] = {}
    for src in (m, *ms):
        for k, v in iter_items(src):
            d[_lower_key(k)] = v
    for k, v in kwds.items():
        d[_lower_key(k)] = v
    return d


# ---------------------------------------------------------------------------
# 类型转换与解析（替代 _vendor/integer_tool.py, ensure.py）
# ---------------------------------------------------------------------------


def int_to_bytes(
    n: int,
    /,
    byteorder: Literal["little", "big"] = "big",
    signed: bool = False,
) -> bytes:
    return n.to_bytes((n.bit_length() + 7) >> 3, byteorder=byteorder, signed=signed)


def try_parse_int(o: Any, /, check_types: None | type | tuple[type, ...] = str) -> Any:
    if isinstance(o, int):
        return o
    if check_types is None or isinstance(o, check_types):
        if isinstance(o, SupportsInt):
            return int(o)
        if isinstance(o, str) and o:
            if o == "true":
                return True
            if o == "false":
                return False
            if o == "0":
                return 0
            if o[0] != "0" and o.isascii() and o.isdigit():
                return int(o)
        elif isinstance(o, Buffer):
            return int.from_bytes(o, "big")
    return o


def ensure_str(o: Any, /, encoding: str = "utf-8", errors: str = "strict") -> str:
    if isinstance(o, str):
        return o
    if isinstance(o, Buffer):
        return str(o, encoding, errors)
    return str(o)


def ensure_bytes(o: Any, /, encoding: str = "utf-8", errors: str = "strict") -> bytes:
    if isinstance(o, bytes):
        return o
    if isinstance(o, memoryview):
        return o.tobytes()
    if isinstance(o, Buffer):
        return bytes(o)
    if isinstance(o, int):
        return int_to_bytes(o)
    if isinstance(o, (str, UserString)):
        return o.encode(encoding, errors)
    try:
        return bytes(o)
    except Exception:
        return str(o).encode(encoding, errors)


def ensure_buffer(o: Any, /, encoding: str = "utf-8", errors: str = "strict") -> Buffer:
    if isinstance(o, Buffer):
        return o
    if isinstance(o, int):
        return int_to_bytes(o)
    if isinstance(o, (str, UserString)):
        return o.encode(encoding, errors)
    try:
        return bytes(o)
    except Exception:
        return str(o).encode(encoding, errors)


# ---------------------------------------------------------------------------
# 迭代归组与去重（替代 _vendor/iter_collect.py）
# ---------------------------------------------------------------------------


class SupportsLT(Protocol):
    def __lt__(self, o: Any, /) -> bool: ...


async def _grouped_mapping_async[K, V](
    it: AsyncIterable[Any],
    /,
    key: Callable[[V], K] | None = None,
    *,
    mapping: MutableMapping[K, list[V]] | None = None,
) -> MutableMapping[K, list[V]]:
    out: MutableMapping[Any, list[Any]] = {} if mapping is None else mapping
    if key is not None:
        async for v in it:
            out.setdefault(key(v), []).append(v)
    else:
        async for k, v in it:
            out.setdefault(k, []).append(v)
    return out


def grouped_mapping[K, V](
    it: Iterable[Any] | AsyncIterable[Any],
    /,
    key: Callable[[V], K] | None = None,
    *,
    mapping: MutableMapping[K, list[V]] | None = None,
) -> MutableMapping[K, list[V]] | Coroutine[Any, Any, MutableMapping[K, list[V]]]:
    if not isinstance(it, Iterable):
        return _grouped_mapping_async(it, key=key, mapping=mapping)
    out: MutableMapping[Any, list[Any]] = {} if mapping is None else mapping
    if key is not None:
        for v in it:
            out.setdefault(key(v), []).append(v)
    else:
        for k, v in it:
            out.setdefault(k, []).append(v)
    return out


async def _iter_keyed_dups_async[K, V](
    it: AsyncIterable[Any],
    /,
    key: Callable[[V], K] | None = None,
    keep_first: None | bool | Callable[[V], SupportsLT] = None,
) -> AsyncIterator[tuple[K, V]]:
    pairs: AsyncIterable[tuple[Any, Any]] = (
        ((key(v), v) async for v in it) if key is not None else it
    )
    if keep_first is None:
        seen_once: dict[Any, Any] = {}
        emitted: set[Any] = set()
        async for k, v in pairs:
            if k in emitted:
                yield k, v
            elif k in seen_once:
                yield k, seen_once.pop(k)
                yield k, v
                emitted.add(k)
            else:
                seen_once[k] = v
    elif callable(keep_first):
        best: dict[Any, tuple[SupportsLT, Any]] = {}
        async for k, v in pairs:
            score = keep_first(v)
            if k in best:
                prev_score, prev_v = best[k]
                if score < prev_score:
                    yield k, prev_v
                else:
                    yield k, v
                    continue
            best[k] = (score, v)
    elif keep_first:
        seen: set[Any] = set()
        async for k, v in pairs:
            if k in seen:
                yield k, v
            else:
                seen.add(k)
    else:
        last: dict[Any, Any] = {}
        async for k, v in pairs:
            if k in last:
                yield k, last[k]
            last[k] = v


def _iter_keyed_dups_sync[K, V](
    it: Iterable[Any],
    /,
    key: Callable[[V], K] | None = None,
    keep_first: None | bool | Callable[[V], SupportsLT] = None,
) -> Iterator[tuple[K, V]]:
    pairs: Iterable[tuple[Any, Any]] = (
        ((key(v), v) for v in it) if key is not None else it
    )
    if keep_first is None:
        seen_once: dict[Any, Any] = {}
        emitted: set[Any] = set()
        for k, v in pairs:
            if k in emitted:
                yield k, v
            elif k in seen_once:
                yield k, seen_once.pop(k)
                yield k, v
                emitted.add(k)
            else:
                seen_once[k] = v
    elif callable(keep_first):
        best: dict[Any, tuple[SupportsLT, Any]] = {}
        for k, v in pairs:
            score = keep_first(v)
            if k in best:
                prev_score, prev_v = best[k]
                if score < prev_score:
                    yield k, prev_v
                else:
                    yield k, v
                    continue
            best[k] = (score, v)
    elif keep_first:
        seen: set[Any] = set()
        for k, v in pairs:
            if k in seen:
                yield k, v
            else:
                seen.add(k)
    else:
        last: dict[Any, Any] = {}
        for k, v in pairs:
            if k in last:
                yield k, last[k]
            last[k] = v


def iter_keyed_dups[K, V](
    it: Iterable[Any] | AsyncIterable[Any],
    /,
    key: Callable[[V], K] | None = None,
    keep_first: None | bool | Callable[[V], SupportsLT] = None,
) -> Iterator[tuple[K, V]] | AsyncIterator[tuple[K, V]]:
    if not isinstance(it, Iterable):
        return _iter_keyed_dups_async(it, key=key, keep_first=keep_first)
    return _iter_keyed_dups_sync(it, key=key, keep_first=keep_first)


# ---------------------------------------------------------------------------
# 文本与格式化（替代 _vendor/texttools/）
# ---------------------------------------------------------------------------


def format_time(t: int | float, /) -> str:
    m, s = divmod(t, 60)
    ss = f"{s:09.06f}" if isinstance(s, float) else f"{s:02d}"
    m = int(m)
    if m < 60:
        return f"{m:02d}:{ss}"
    h, m = divmod(m, 60)
    if h < 24:
        return f"{h:02d}:{m:02d}:{ss}"
    d, h = divmod(h, 24)
    return f"{d}d{h:02d}:{m:02d}:{ss}"


# ---------------------------------------------------------------------------
# 平台辅助：打开文件（替代 _vendor/startfile.py）
# ---------------------------------------------------------------------------


if hasattr(os, "startfile"):
    startfile = os.startfile  # type: ignore[attr-defined]

    @wraps(startfile)
    async def startfile_async(*args: Any, **kwds: Any) -> Any:
        return await to_thread(startfile, *args, **kwds)
else:

    def _resolve_open_cmd() -> str:
        match system():
            case "Linux" | "Android":
                return "xdg-open"
            case "Darwin":
                return "open"
            case "Windows":
                return "start"
            case _:
                if which("xdg-open"):
                    return "xdg-open"
                raise RuntimeError("cannot resolve startfile command")

    def startfile(path: Any, /, *args: Any) -> None:
        subprocess.run([_resolve_open_cmd(), path, *args], check=False)

    async def startfile_async(path: Any, /, *args: Any) -> None:
        cmd: Any = [_resolve_open_cmd(), path, *args]
        if isinstance(cmd, str):
            proc = await create_subprocess_shell(cmd)
        else:
            proc = await create_subprocess_exec(*cmd)
        await proc.communicate()


# ---------------------------------------------------------------------------
# 函数参数检测与装饰器辅助（替代 _vendor/argtools.py, decotools.py）
# ---------------------------------------------------------------------------


def argcount(func: Callable[..., Any], /) -> int:
    """统计可调用对象的位置参数个数。"""
    if isinstance(func, partial):
        return max(0, argcount(func.func) - len(func.args))
    is_method = isinstance(func, (MethodType, MethodWrapperType))
    try:
        return func.__code__.co_argcount - is_method
    except AttributeError:
        return len(getfullargspec(func).args) - is_method


def has_keyword_arg(func: Callable[..., Any], arg_name: str, /) -> bool:
    """判断可调用对象是否接受指定关键字参数（或 **kwargs）。"""
    try:
        sig = signature(func)
    except ValueError:
        try:
            arg_spec = getfullargspec(func)
            return bool(arg_spec.varkw or arg_name in arg_spec.kwonlyargs)
        except TypeError:
            return False
    for name, param in sig.parameters.items():
        if param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY):
            if name == arg_name:
                return True
        elif param.kind is Parameter.VAR_KEYWORD:
            return True
    return False


def _bind[R](func: Callable[..., R], /, *args: Any, **kwds: Any) -> Callable[..., R]:
    def bound(*pargs: Any, **kargs: Any) -> R:
        return func(*args, *pargs, **{**kwds, **kargs})

    return bound


def _safe_update_wrapper(f: Any, g: Any, /) -> Any:
    if f is g or not callable(f):
        return f
    return _update_wrapper(f, g)


def decorated(f: Callable[..., Any], /) -> Callable[..., Any]:
    """将形如 `def deco(func, /, *args, **kwds)` 的单层函数转为装饰器。"""

    def wrapper(*args: Any) -> Any:
        return _safe_update_wrapper(_bind(f, *args), args[-1])

    return _safe_update_wrapper(wrapper, f)


def optional(f: Callable[..., Any], /) -> Callable[..., Any]:
    """使带默认参数的装饰器同时支持 `@deco` 和 `@deco(...)` 两种用法。"""
    nargs = 0
    for param in signature(f).parameters.values():
        if param.kind is param.POSITIONAL_ONLY or (
            param.kind is param.POSITIONAL_OR_KEYWORD and param.default is param.empty
        ):
            nargs += 1
        if nargs >= 2:
            break

    def wrapped(*args: Any, **kwds: Any) -> Any:
        if len(args) >= nargs:
            return _safe_update_wrapper(f(*args, **kwds), args[-1])
        return _bind(f, *args, **kwds)

    return _safe_update_wrapper(wrapped, f)


# ---------------------------------------------------------------------------
# 错误码枚举与异常映射（替代 _vendor/errno2.py）
# ---------------------------------------------------------------------------


def _issubcls(a: Any, b: type, /) -> bool:
    try:
        return issubclass(a, b)
    except TypeError:
        return False


class errno(IntEnum):
    """标准 POSIX errno 精简枚举（支持 .description / .error() / .throw()）。"""

    description: str

    def __new__(cls, value: int, description: str = "") -> Self:
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    EPERM = 1, "Operation not permitted"
    ENOENT = 2, "No such file or directory"
    ESRCH = 3, "No such process"
    EINTR = 4, "Interrupted system call"
    EIO = 5, "Input/output error"
    EBADF = 9, "Bad file descriptor"
    ECHILD = 10, "No child processes"
    EAGAIN = 11, "Resource temporarily unavailable"
    EACCES = 13, "Permission denied"
    EFAULT = 14, "Bad address"
    EBUSY = 16, "Device or resource busy"
    EEXIST = 17, "File exists"
    ENOTDIR = 20, "Not a directory"
    EISDIR = 21, "Is a directory"
    EINVAL = 22, "Invalid argument"
    EFBIG = 27, "File too large"
    ENOSPC = 28, "No space left on device"
    ESPIPE = 29, "Illegal seek"
    EPIPE = 32, "Broken pipe"
    ERANGE = 34, "Numerical result out of range"
    ENOSYS = 38, "Function not implemented"
    EWOULDBLOCK = 41, "Operation would block"
    ENODATA = 61, "No data available"
    EOPNOTSUPP = 95, "Operation not supported"
    ECONNABORTED = 103, "Software caused connection abort"
    ECONNRESET = 104, "Connection reset by peer"
    ESHUTDOWN = 108, "Cannot send after transport endpoint shutdown"
    ETIMEDOUT = 110, "Connection timed out"
    ECONNREFUSED = 111, "Connection refused"
    EALREADY = 114, "Operation already in progress"
    EINPROGRESS = 115, "Operation now in progress"
    EDQUOT = 122, "Disk quota exceeded"
    ENOTSUP = 134, "Not supported parameter or option"
    EAUTH = 137, "Authentication error"
    ENOTCAPABLE = 154, "Capabilities insufficient"

    @staticmethod
    def of(key: int | str | errno, /) -> errno:
        if isinstance(key, errno):
            return key
        if isinstance(key, int):
            return errno(key)
        try:
            return errno[key]
        except KeyError as e:
            raise ValueError(key) from e

    def error(self, /, *args: Any, **kwds: Any) -> BaseException:
        if args and _issubcls(args[0], BaseException):
            exctype: type[BaseException] = args[0]
            args = args[1:]
        else:
            exctype = errno2error.get(self, OSError)
        if not (args or kwds):
            args = (self.description,)
        return exctype(self, *args, **kwds)

    def throw(self, /, *args: Any, **kwds: Any) -> Never:
        raise self.error(*args, **kwds)


errno2error: Final[dict[errno, type[OSError]]] = {
    errno.EPERM: PermissionError,
    errno.ENOENT: FileNotFoundError,
    errno.ESRCH: ProcessLookupError,
    errno.EINTR: InterruptedError,
    errno.ECHILD: ChildProcessError,
    errno.EAGAIN: BlockingIOError,
    errno.EACCES: PermissionError,
    errno.EEXIST: FileExistsError,
    errno.ENOTDIR: NotADirectoryError,
    errno.EISDIR: IsADirectoryError,
    errno.EPIPE: BrokenPipeError,
    errno.EWOULDBLOCK: BlockingIOError,
    errno.ECONNABORTED: ConnectionAbortedError,
    errno.ECONNRESET: ConnectionResetError,
    errno.ESHUTDOWN: BrokenPipeError,
    errno.ETIMEDOUT: TimeoutError,
    errno.ECONNREFUSED: ConnectionRefusedError,
    errno.EALREADY: BlockingIOError,
    errno.EINPROGRESS: BlockingIOError,
    errno.ENOTCAPABLE: PermissionError,
}
