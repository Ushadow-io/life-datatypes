"""
Example: Parse a conversation from transcribed data using life-datatypes
"""

from datetime import datetime
from uuid import uuid4
from life_datatypes import Segment, Fragment, Thread, Conversation

# Create segments from ASR output
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
]

# Create fragments (semantic units)
fragments = [
    Fragment(
        id=str(uuid4()),
        text="Hello, how are you today?",
        segmentId=segments[0].id,
        type="utterance",
        metadata={"intent": "greeting"},
    ),
    Fragment(
        id=str(uuid4()),
        text="I'm doing great, thanks for asking.",
        segmentId=segments[1].id,
        type="utterance",
        metadata={"sentiment": "positive"},
    ),
]

# Create threads (topical coherence)
threads = [
    Thread(
        id=str(uuid4()),
        title="Opening Greeting",
        description="Initial pleasantries and greeting exchange",
        fragmentIds=[fragments[0].id, fragments[1].id],
        participants=["alice", "bob"],
        startTime=0.0,
        endTime=5.2,
    ),
]

# Assemble the full conversation
conversation = Conversation(
    id=str(uuid4()),
    title="Alice and Bob Conversation",
    description="A simple greeting conversation",
    participants=["alice", "bob"],
    startTime=datetime.fromisoformat("2024-02-24T10:00:00+00:00"),
    endTime=datetime.fromisoformat("2024-02-24T10:05:00+00:00"),
    duration=300.0,
    segments=segments,
    fragments=fragments,
    threads=threads,
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
