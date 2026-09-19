from rag import list_document_records


class FakeIndex:
    def list(self, namespace, prefix=None):
        assert namespace == "documents"
        assert prefix == "document-"
        return [{"ids": ["document-1", "document-2"]}]

    def fetch(self, ids, namespace):
        assert namespace == "documents"
        return {
            "vectors": {
                "document-1": {
                    "metadata": {
                        "document_id": "1",
                        "filename": "engineering.pdf",
                        "domain": "Engineering",
                        "file_type": "pdf",
                        "status": "indexed",
                        "ocr": False,
                        "indexed": True,
                        "chunk_count": 3,
                        "created_at": "2026-09-19T10:00:00",
                    }
                },
                "document-2": {
                    "metadata": {
                        "document_id": "2",
                        "filename": "finance.png",
                        "domain": "Finance",
                        "file_type": "png",
                        "status": "indexed",
                        "ocr": True,
                        "indexed": True,
                        "chunk_count": 2,
                        "created_at": "2026-09-19T11:00:00",
                    }
                },
            }
        }


def test_document_library_filters_by_domain(monkeypatch):
    import rag

    monkeypatch.setattr(rag, "index", FakeIndex())

    records = list_document_records(domain="Finance")

    assert len(records) == 1
    assert records[0]["filename"] == "finance.png"
    assert records[0]["domain"] == "Finance"
    assert records[0]["ocr"] is True
    assert records[0]["indexed"] is True
