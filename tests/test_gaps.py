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


def test_conversation_attributes_remain_available_after_session_commit():
    from aoip.db import SessionLocal

    conversation = Conversation(
        title="Nigeria fintech policy update",
        summary="Policy changes are affecting fintech strategy.",
        content="Why are payment companies changing their roadmaps?",
        industry="fintech",
        country="Nigeria",
        opportunity_score=70,
    )
    session = SessionLocal()
    session.add(conversation)
    session.commit()
    session.close()

    assert conversation.title == "Nigeria fintech policy update"
    assert conversation.opportunity_score == 70
