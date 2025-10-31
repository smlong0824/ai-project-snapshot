from src.core.engine import NovaEngine


class FakeModel:
    def __init__(self, resp, loaded=True):
        self.is_loaded = loaded
        self._resp = resp

    def generate(self, prompt, **kwargs):
        return self._resp


class DummyConfig:
    def get_model_config(self, name):
        return {"name": name, "device": "cpu", "quantization": None}

    rag_config = {"embedding_model": "sentence-transformers/all-MiniLM-L6-v2", "collection_name": "test"}
    rag_index_dir = "/tmp"


def test_should_use_heavy_by_marker():
    eng = NovaEngine(DummyConfig())
    eng.llama31 = FakeModel("ok")
    eng.llama31.is_loaded = True
    assert eng.should_use_heavy_thinking("please explain in detail why X") is True


def test_process_query_auto_fast_only():
    eng = NovaEngine(DummyConfig())
    eng.smollm3 = FakeModel("quick answer")
    eng.llama31 = FakeModel("deep answer")
    eng.smollm3.is_loaded = True
    eng.llama31.is_loaded = True
    res = eng.process_query("short query", mode="auto")
    assert res.get("response") == "quick answer"
    assert "SmolLM3" in res.get("model_used", "")


def test_process_query_auto_triggers_heavy():
    eng = NovaEngine(DummyConfig())
    eng.smollm3 = FakeModel("i'm not sure")
    eng.llama31 = FakeModel("detailed")
    eng.smollm3.is_loaded = True
    eng.llama31.is_loaded = True
    long_query = "long query with enough words " * 30
    res = eng.process_query(long_query, mode="auto")
    assert res.get("used_heavy_thinking") is True
    assert "Llama" in res.get("model_used", "") or "→" in res.get("model_used", "")
