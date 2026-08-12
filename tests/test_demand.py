from aoip.intelligence.demand import assess_demand, google_news_rss_for_query, google_trends_explore_url


class Item:
    def __init__(self, title: str):
        self.title = title


def test_google_demand_urls_are_generated():
    assert "news.google.com/rss/search" in google_news_rss_for_query("Africa startup funding")
    assert "trends.google.com/trends/explore" in google_trends_explore_url("Africa startup funding")


def test_assess_demand_scores_questions():
    result = assess_demand(
        "Startup funding",
        "Africa startup funding",
        "investment",
        [Item("How to raise startup funding in Africa"), Item("Best grants for African entrepreneurs")],
    )

    assert result.demand_score > 40
    assert result.authority_gap_score > 40
    assert result.suggested_title
