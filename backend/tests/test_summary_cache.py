from app import summary_cache
def test_opt_in_cache(monkeypatch,tmp_path):
    monkeypatch.delenv("CLEARFINANCE_CACHE_DIR",raising=False)
    summary_cache.save("private","model","1",{"ok":True})
    assert summary_cache.load("private","model","1") is None
    monkeypatch.setenv("CLEARFINANCE_CACHE_DIR",str(tmp_path))
    summary_cache.save("public","model","1",{"ok":True})
    assert summary_cache.load("public","model","1")=={"ok":True}
    assert summary_cache.load("public","model","2") is None
