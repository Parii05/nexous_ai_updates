import pytest

from rag import retrieve_chunks


DOMAINS = [
    "Engineering",
    "Product",
    "People / HR",
    "Finance",
    "Legal & Compliance",
]


class FakeEmbedder:
    def encode(self, texts):
        return [[0.0] * 384 for _ in texts]


class FakeIndex:
    def __init__(self, requested_domain):
        self.requested_domain = requested_domain
        self.kwargs = None

    def query(self, **kwargs):
        self.kwargs = kwargs
        # Simulate a defensive scenario where Pinecone returns a
        # mismatched-domain candidate alongside the requested domain.
        return {
            "matches": [
                {
                    "score": 0.1,
                    "metadata": {
                        "text": f"{self.requested_domain} policy",
                        "source": f"{self.requested_domain}.pdf",
                        "domain": self.requested_domain,
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


@pytest.mark.parametrize("domain", DOMAINS)
def test_retrieve_chunks_enforces_domain_filter(monkeypatch, domain):
    import rag

    fake_index = FakeIndex(domain)
    monkeypatch.setattr(rag, "embedder", FakeEmbedder())
    monkeypatch.setattr(rag, "index", fake_index)

    chunks = retrieve_chunks("policy", domain=domain)

    assert fake_index.kwargs["filter"] == {
        "$and": [
            {"type": {"$eq": "document_chunk"}},
            {"domain": {"$eq": domain}},
        ]
    }
    assert chunks
    assert all(chunk["domain"] == domain for chunk in chunks)

    # No chunk from another domain may enter the RAG context.
    assert all(chunk["domain"] == domain for chunk in chunks)
