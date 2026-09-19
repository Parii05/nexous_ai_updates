from rag import build_citation_entries


def test_build_citation_entries_preserve_source_and_page_number():
    chunks = [
        {"text": "First supporting paragraph", "source": "doc1.pdf", "page_number": 2},
        {"text": "Second supporting paragraph", "source": "doc2.pdf", "page_number": 5},
    ]

    citations = build_citation_entries(chunks)

    assert citations[0]["id"] == 1
    assert citations[0]["source"] == "doc1.pdf"
    assert citations[0]["page_number"] == 2
    assert citations[1]["id"] == 2
    assert citations[1]["source"] == "doc2.pdf"
    assert citations[1]["page_number"] == 5
