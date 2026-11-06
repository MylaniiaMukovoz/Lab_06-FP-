from closures import make_logger, make_counter

def test_make_logger():
    logs: list[str] = []
    logger = make_logger("TEST", logs.append)
    
    logger("INFO", "System ready")
    assert len(logs) == 1
    assert logs[0] == "[TEST] [INFO] System ready"

def test_make_counter():
    counter = make_counter(5)
    assert counter() == 6
    assert counter() == 7