from rag import retrieve_chunks


class FakeEmbedder:
    def encode(self, texts):
        return [[0.0] * 384 for _ in texts]


class FakeIndex:
    def __init__(self):
        self.kwargs = None

    def query(self, **kwargs):
        self.kwargs = kwargs
        return {
            "matches": [
                {
                    "score": 0.1,
                    "metadata": {
                        "text": "Finance budget policy",
                        "source": "finance.pdf",
                        "domain": "Finance",
                        "type": "document_chunk",
                    },
                },
                {
                    "score": 0.2,
                    "metadata": {
                        "text": "Engineering deployment policy",
                        "source": "engineering.pdf",
                        "domain": "Engineering",
                        "type": "document_chunk",
                    },
                },
            ]
        }


def test_retrieve_chunks_enforces_domain_filter(monkeypatch):
    import rag

    fake_index = FakeIndex()
    monkeypatch.setattr(rag, "embedder", FakeEmbedder())
    monkeypatch.setattr(rag, "index", fake_index)

    chunks = retrieve_chunks("budget", domain="Finance")

    assert fake_index.kwargs["filter"] == {
        "$and": [
            {"type": {"$eq": "document_chunk"}},
            {"domain": {"$eq": "Finance"}},
        ]
    }
    assert chunks
    assert all(chunk["domain"] == "Finance" for chunk in chunks)
    assert all("Engineering" not in chunk["text"] for chunk in chunks)
