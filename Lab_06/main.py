from closures import make_logger, make_counter
from decorators import timed, logged

def std_output(msg: str) -> None:
    print(msg)

app_logger = make_logger("MAIN_APP", std_output)
func_counter = make_counter()

@timed(unit="ms", logger=lambda msg: app_logger("DEBUG", msg))
@logged(level="INFO", logger=app_logger)
def process_data(data: list[int], scale: int = 1) -> list[int]:
    """Обробляє список чисел, масштабуючи їх."""
    func_counter()
    if scale < 0:
        raise ValueError("Scale must be positive")
    return [x * scale for x in data]

if __name__ == "__main__":
    app_logger("INFO", "Application started")
    
    process_data([1, 2, 3], scale=10)
    try:
        process_data([5, 5], scale=-2)
    except ValueError:
        pass
    
    app_logger("INFO", f"Total function calls: {func_counter()}")