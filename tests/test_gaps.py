from aoip.intelligence.gaps import detect_content_gaps
from aoip.models import Conversation


def test_detect_content_gaps_from_conversations():
    gaps = detect_content_gaps(
        [
            Conversation(title="How does climate finance work?", industry="climate", country="Kenya"),
            Conversation(title="Why are climate projects difficult?", industry="climate", country="Kenya"),
        ]
    )

    assert gaps
    assert gaps[0].demand_score > 30
