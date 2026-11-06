import pytest
from decorators import retries

def test_retries_no_sleep() -> None:
    """Успіх на 3-й спробі без реального sleep, підрахунок викликів[cite: 1]."""
    calls = {"n": 0}
    
    def fake_sleep(_: float) -> None: 
        calls["slept"] = True
        
    @retries(attempts=3, delay=0, sleep=fake_sleep, logger=lambda s: None)
    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3: 
            raise RuntimeError("boom")
        return "ok"
        
    assert flaky() == "ok"
    assert calls["n"] == 3