from rag import rank_hybrid_results


def test_rank_hybrid_results_uses_dense_and_sparse_signals():
    candidates = [
        {"text": "Python for data science", "score": 0.1, "source": "doc-a"},
        {"text": "A cat sleeps on the couch", "score": 0.2, "source": "doc-b"},
    ]

    ranked = rank_hybrid_results("python data science", candidates)

    assert ranked[0]["text"] == "Python for data science"
    assert ranked[0]["sparse_score"] > ranked[1]["sparse_score"]
    assert ranked[0]["hybrid_score"] > ranked[1]["hybrid_score"]
