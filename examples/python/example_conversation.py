"""
Example: Build a conversation from segments, fragments, and threads using life-datatypes

Hierarchy:
- Segments: Atomic timeline units (speaker lines, delimited by speaker change/pause)
- Fragments: Consecutive segments grouped by topic (discussion of one subject)
- Threads: Non-consecutive fragments grouped by broader topic (meta-themes)
"""

from datetime import datetime
from uuid import uuid4
from life_datatypes import Segment, Fragment, Thread, Conversation

# Create segments from ASR output (chronological order)
# Each segment is a line of dialog (speaker change or pause boundary)
segments = [
    Segment(
        id=str(uuid4()),
        text="Hello, how are you today?",
        speaker="alice",
        start=0.0,
        end=2.5,
        confidence=0.98,
        language="en",
    ),
    Segment(
        id=str(uuid4()),
        text="I'm doing great, thanks for asking.",
        speaker="bob",
        start=3.0,
        end=5.2,
        confidence=0.96,
        language="en",
    ),
    Segment(
        id=str(uuid4()),
        text="I wanted to discuss the quarterly budget.",
        speaker="alice",
        start=6.0,
        end=8.5,
        confidence=0.94,
        language="en",
    ),
]

# Create fragments: consecutive segments with same topic
fragments = [
    Fragment(
        id=str(uuid4()),
        text="Hello, how are you today? I'm doing great, thanks for asking.",
        segmentIds=[segments[0].id, segments[1].id],  # Consecutive greeting exchange
        type="utterance",
        metadata={"topic": "greeting"},
    ),
    Fragment(
        id=str(uuid4()),
        text="I wanted to discuss the quarterly budget.",
        segmentIds=[segments[2].id],  # Budget discussion starts
        type="utterance",
        metadata={"topic": "budget"},
    ),
]

# Create threads: fragments grouped by broader topic (can be non-consecutive)
threads = [
    Thread(
        id=str(uuid4()),
        title="Opening Ceremony",
        description="Initial greeting and pleasantries",
        fragmentIds=[fragments[0].id],
        participants=["alice", "bob"],
        startTime=0.0,
        endTime=5.2,
    ),
]

# Assemble the full conversation
conversation = Conversation(
    id=str(uuid4()),
    title="Alice and Bob Meeting",
    description="A meeting between Alice and Bob",
    participants=["alice", "bob"],
    startTime=datetime.fromisoformat("2024-02-24T10:00:00+00:00"),
    endTime=datetime.fromisoformat("2024-02-24T10:10:00+00:00"),
    duration=600.0,
    segments=segments,  # Atomic timeline
    fragments=fragments,  # Consecutive topic groupings
    threads=threads,  # Broader topic themes
    metadata={
        "source": "deepgram",
        "quality": "high",
        "recording_device": "conference_microphone",
    },
)

# Validate and print
print("✓ Conversation created successfully")
print(f"  ID: {conversation.id}")
print(f"  Title: {conversation.title}")
print(f"  Participants: {', '.join(conversation.participants)}")
print(f"  Segments: {len(conversation.segments)}")
print(f"  Fragments: {len(conversation.fragments)}")
print(f"  Threads: {len(conversation.threads)}")

# Serialize to JSON for storage/transmission
import json
print("\nSerialized conversation (first 500 chars):")
print(json.dumps(conversation.model_dump(), indent=2)[:500] + "...")

