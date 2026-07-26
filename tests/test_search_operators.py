from aoip.search.operators import generate_search_operators


def test_generate_search_operators_limits_and_shapes_queries():
    queries = generate_search_operators(["Nigeria"], ["AI"], sites=["linkedin.com"], intents=["funding"], limit=10)

    assert len(queries) == 1
    assert queries[0].query == "site:linkedin.com Nigeria AI funding"
    assert queries[0].country == "Nigeria"
    assert queries[0].industry == "AI"
