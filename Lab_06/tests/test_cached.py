from decorators import cached

def test_cached_ttl_and_invalidate() -> None:
    """Перевірка TTL, часткового й повного очищення кешу[cite: 1]."""
    time_state = {"t": 1000.0}
    def time_fn() -> float: 
        return time_state["t"]
        
    hit = {"n": 0}
    @cached(ttl=1.0, time_fn=time_fn)
    def f(x: int) -> int:
        hit["n"] += 1
        return x * 2
        
    assert f(10) == 20  
    assert f(10) == 20   
    assert hit["n"] == 1
    
    time_state["t"] += 2.0 
    assert f(10) == 20
    assert hit["n"] == 2
    
    removed = f.cache_invalidate(lambda a, kw: a == (10,))
    assert removed >= 1
    assert f(10) == 20
    assert hit["n"] == 3