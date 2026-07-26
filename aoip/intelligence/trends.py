from __future__ import annotations

from collections import Counter

from aoip.models import Conversation


def trend_snapshot(conversations: list[Conversation]) -> list[dict[str, object]]:
    counter: Counter[str] = Counter()
    for conversation in conversations:
        if conversation.industry:
            counter[conversation.industry] += 1

    rows: list[dict[str, object]] = []
    for topic, count in counter.most_common(12):
        rows.append(
            {
                "topic": topic,
                "signals": count,
                "direction": "accelerating" if count >= 3 else "emerging" if count == 2 else "early",
                "strength": min(100, count * 18),
            }
        )
    return rows
