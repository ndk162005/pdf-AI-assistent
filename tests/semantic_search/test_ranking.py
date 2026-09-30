from app.semantic_search.search.ranking import ResultRanker

def test_result_ranker():
    raw_matches = [
        {"filename": "docB.pdf", "page_number": 2, "chunk_text": "Lower similarity passage", "distance": 0.3},
        {"filename": "docA.pdf", "page_number": 1, "chunk_text": "Higher similarity passage", "distance": 0.1}
    ]

    ranked = ResultRanker.rank_results(raw_matches)

    assert len(ranked) == 2
    # docA has distance 0.1 -> score 0.9, so it must be rank 1
    assert ranked[0]["rank"] == 1
    assert ranked[0]["document"] == "docA.pdf"
    assert ranked[0]["score"] == 0.9

    assert ranked[1]["rank"] == 2
    assert ranked[1]["document"] == "docB.pdf"
    assert ranked[1]["score"] == 0.7

def test_result_ranker_empty():
    assert ResultRanker.rank_results([]) == []
