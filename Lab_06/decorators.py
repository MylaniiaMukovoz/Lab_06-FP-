import functools
import time
from typing import Callable, ParamSpec, TypeVar, Literal

P = ParamSpec("P")
R = TypeVar("R")

def timed(
    label: str | None = None,
    *,
    unit: Literal["s", "ms", "us"] = "ms",
    logger: Callable[[str], None] = lambda _: None,
    clock: Callable[[], float] = time.perf_counter,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Декоратор таймінгу для вимірювання часу виконання функції."""
    factor = {"s": 1.0, "ms": 1e3, "us": 1e6}[unit]
    
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        name = label or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            t0 = clock()
            try:
                return func(*args, **kwargs)
            finally:
                dt = (clock() - t0) * factor
                logger(f"[timed] {name} took {dt:.3f} {unit}")
        return wrapper
    return decorator

def logged(
    level: str = "INFO",
    *,
    logger: Callable[[str, str], None]
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Декоратор для логування викликів функцій, їх аргументів та результатів або винятків."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)

            logger(level, f"Calling {func.__name__}({signature})")
            try:
                result = func(*args, **kwargs)
                logger(level, f"{func.__name__} returned {result!r}")
                return result
            except Exception as e:
                logger("ERROR", f"{func.__name__} raised {type(e).__name__}: {e}")
                raise
        return wrapper
    return decorator

import random
import threading
from typing import Any, Callable, Hashable, Tuple


def retries(
    attempts: int = 3,
    exceptions: Tuple[type[BaseException], ...] = (Exception,),
    delay: float = 0.0,
    backoff: float = 1.0,
    jitter: float = 0.0,
    *,
    sleep: Callable[[float], None] = time.sleep,
    logger: Callable[[str], None] = lambda _: None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Декоратор повторів при винятках з експоненційним бекофом."""
    assert attempts >= 1
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            exc: BaseException | None = None
            for i in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    exc = e
                    if i == attempts:
                        logger(f"[retries] fail after {i} attempts: {e!r}")
                        break
                    wait = delay * (backoff ** (i - 1)) + (random.random() * jitter if jitter else 0.0)
                    logger(f"[retries] attempt {i} failed: {e!r}; sleeping {wait:.3f}s")
                    sleep(wait)
            assert exc is not None
            raise exc
        return wrapper
    return decorator

def make_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Hashable:
    """Простий ключ для хешованих аргументів[cite: 1]."""
    return (args, tuple(sorted(kwargs.items())))

def cached(
    *,
    ttl: float | None = None,
    time_fn: Callable[[], float] = time.time,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Декоратор кешування з підтримкою TTL та методами інвалідації[cite: 1]."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        cache: dict[Hashable, tuple[float | None, R]] = {}
        lock = threading.Lock()
        
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = make_key(args, kwargs)
            now = time_fn()
            with lock:
                if key in cache:
                    exp, val = cache[key]
                    if exp is None or now < exp:
                        return val
                    else:
                        del cache[key] 

            val = func(*args, **kwargs)
            with lock:
                expiry = None if ttl is None else now + ttl
                cache[key] = (expiry, val)
            return val

        def cache_clear() -> None:
            with lock: 
                cache.clear()

        def cache_invalidate(predicate: Callable[[tuple[Any, ...], dict[str, Any]], bool]) -> int:
            removed = 0
            with lock:
                for k in list(cache.keys()):
                    args_k, kwargs_k = k[0], dict(k[1])
                    if predicate(args_k, kwargs_k):
                        del cache[k]
                        removed += 1
            return removed

        wrapper.cache_clear = cache_clear           
        wrapper.cache_invalidate = cache_invalidate 
    return decorator