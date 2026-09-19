from rag import chunk_text


def test_chunk_text_preserves_paragraph_boundaries():
    text = "Heading\n\nFirst paragraph about cats.\n\nSecond paragraph about dogs."

    chunks = chunk_text(text)

    assert len(chunks) >= 2
    assert any("First paragraph" in chunk for chunk in chunks)
    assert any("Second paragraph" in chunk for chunk in chunks)
