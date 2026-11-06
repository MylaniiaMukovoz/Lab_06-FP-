from decorators import timed

def test_timed_uses_clock_and_logger() -> None:
    """Перевірка інʼєкції clock/logger та логування часу."""
    ticks = [0.0, 0.012345]
    def fake_clock() -> float:
        return ticks.pop(0)
    
    logs: list[str] = []
    def fake_log(s: str) -> None: 
        logs.append(s)
        
    @timed("work", unit="ms", logger=fake_log, clock=fake_clock)
    def work(x: int) -> int: 
        return x * x
        
    assert work(5) == 25
    assert any("work took 12.345 ms" in m for m in logs)