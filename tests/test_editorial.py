from aoip.ai import AIClient
from aoip.config import AppSettings
from aoip.intelligence.editorial import assess_conversation


def test_assess_conversation_offline_scores_opportunity():
    settings = AppSettings()
    result = assess_conversation(
        "Nigeria AI startup funding is accelerating",
        "Investors are asking how founders can access compute and capital.",
        ["Nigeria"],
        ["AI"],
        AIClient(settings),
    )

    assert result.country == "Nigeria"
    assert result.industry == "AI"
    assert result.opportunity_score > 50
    assert result.recommended_action in {"publish", "investigate", "engage", "monitor"}
