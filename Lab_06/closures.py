from typing import Callable

def make_logger(prefix: str, output_fn: Callable[[str], None]) -> Callable[[str, str], None]:
    """
    Створює логер із заданим префіксом.
    Використовує ін'єктовану функцію output_fn замість прямого виклику print.
    """
    def log(level: str, msg: str) -> None:
        output_fn(f"[{prefix}] [{level}] {msg}")
    return log

def make_counter(start: int = 0) -> Callable[[], int]:
    """
    Лічильник викликів, що зберігає стан через nonlocal.
    """
    value = start
    def inc() -> int:
        nonlocal value
        value += 1
        return value
    return inc