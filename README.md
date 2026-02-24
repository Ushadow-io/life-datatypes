# life-datatypes

[![npm version](https://img.shields.io/npm/v/life-datatypes.svg)](https://www.npmjs.com/package/life-datatypes)
[![PyPI version](https://img.shields.io/pypi/v/life-datatypes.svg)](https://pypi.org/project/life-datatypes/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Shared conversation data types for ASR, NLP, and conversation analysis across the Ushadow ecosystem.

## Overview

`life-datatypes` defines a unified conversation schema that bridges **Chronicle** (conversation storage), **Mycelia** (conversation analysis), and other services that work with transcribed conversations.

The schema models conversations at three hierarchical levels:

```
Conversation (time-bounded dialog with start/end)
├── Segments (atomic timeline units, delimited by speaker/pause)
│   └── Like lines in a screenplay
├── Fragments (consecutive segments grouped by topic)
│   └── Discussion of a specific subject within the timeline
└── Threads (fragments grouped by broader theme)
    └── Can be non-consecutive across the conversation
```

## Installation

### Python (PyPI)

```bash
pip install life-datatypes
```

```python
from life_datatypes import Conversation, Segment, Fragment, Thread

# Use the types...
```

### TypeScript / JavaScript (npm)

```bash
npm install life-datatypes
```

```typescript
import { Conversation, Segment, Fragment, Thread } from 'life-datatypes'

// Use the types...
```

## Quick Example

### Python

```python
from life_datatypes import Segment, Fragment, Thread, Conversation
from datetime import datetime
from uuid import uuid4

# Create a segment from ASR output
segment = Segment(
    id=str(uuid4()),
    text="Hello, how are you?",
    speaker="alice",
    start=0.0,
    end=2.5,
    confidence=0.98,
    language="en"
)

# Create a fragment (semantic unit)
fragment = Fragment(
    id=str(uuid4()),
    text="Hello, how are you?",
    segmentId=segment.id,
    type="utterance",
    metadata={"intent": "greeting"}
)

# Assemble into a conversation
conversation = Conversation(
    id=str(uuid4()),
    title="Meeting with Alice",
    participants=["alice", "bob"],
    startTime=datetime.now(),
    segments=[segment],
    fragments=[fragment]
)

# Validate and serialize
json_data = conversation.model_dump_json()
```

### TypeScript

```typescript
import { Conversation, Segment, Fragment } from 'life-datatypes'
import { randomUUID } from 'crypto'

const segment: Segment = {
  id: randomUUID(),
  text: 'Hello, how are you?',
  speaker: 'alice',
  start: 0.0,
  end: 2.5,
  confidence: 0.98,
  language: 'en'
}

const conversation: Conversation = {
  id: randomUUID(),
  title: 'Meeting with Alice',
  participants: ['alice', 'bob'],
  startTime: new Date().toISOString(),
  segments: [segment]
}

// Serialize to JSON
const json = JSON.stringify(conversation)
```

## Data Model

### Segment
A contiguous transcribed text from a speaker with timing metadata.

```python
Segment(
    id: str                    # Unique identifier
    text: str                  # Transcribed text
    speaker: str               # Speaker ID or name
    start: float               # Start time (seconds)
    end: float                 # End time (seconds)
    confidence: float          # ASR confidence (0-1)
    language: str              # Language code (e.g., 'en')
    metadata: dict             # Provider-specific data
)
```

### Fragment
A topic-linked group of **consecutive** segments (e.g., discussion of a specific subject).

Fragments must reference adjacent segments in the chronological timeline.

```python
Fragment(
    id: str                    # Unique identifier
    text: str                  # Fragment text (combined from consecutive segments)
    segmentIds: list[str]      # References to consecutive segment IDs (must be adjacent)
    type: str                  # 'sentence' | 'clause' | 'turn' | 'utterance' | 'other'
    start: float               # Start time (from first segment)
    end: float                 # End time (from last segment)
    metadata: dict             # Fragment-specific metadata
)
```

### Thread
A broader topic grouping of fragments across the conversation.

Unlike fragments (which are consecutive), threads can span **non-consecutive fragments**. For example, a "budget" thread might include fragments scattered throughout the conversation.

```python
Thread(
    id: str                    # Unique identifier
    title: str                 # Thread title/topic
    description: str           # Detailed description
    fragmentIds: list[str]     # Fragment IDs (can be non-consecutive)
    participants: list[str]    # Speakers involved
    startTime: float           # Earliest fragment start (seconds)
    endTime: float             # Latest fragment end (seconds)
    metadata: dict             # Tags, sentiment, importance, etc.
)
```

### Conversation
The complete conversation with all three levels: segments (atomic timeline), fragments (consecutive topic groupings), and threads (broader themes).

```python
Conversation(
    id: str                    # Unique identifier
    title: str                 # Conversation title
    description: str           # Summary
    participants: list[str]    # All speakers
    startTime: str             # ISO 8601 timestamp
    endTime: str               # ISO 8601 timestamp
    duration: float            # Total duration (seconds)
    segments: list[Segment]    # All segments (chronological order)
    fragments: list[Fragment]  # Topic-grouped consecutive segments
    threads: list[Thread]      # Broader topic groupings
    metadata: dict             # Conversation-level metadata
)
```

## Schema Design

The schema is language-agnostic, hierarchical, and version-stable:

- **Single source of truth**: `schema/conversation.json` (JSON Schema Draft 7)
- **Type generation**: Automatically generated from schema for Python (Pydantic) and TypeScript
- **Three-level hierarchy**: Segments (atomic) → Fragments (consecutive topic grouping) → Threads (broader themes)
- **Extensibility**: `metadata` fields on every type allow provider-specific extensions
- **Validation**: Built-in validation in generated Pydantic models

### Design Decisions

**Three Levels:**
- **Segments**: Delimited by speaker change or pause — atomic timeline units (like screenplay lines)
- **Fragments**: Consecutive segments linked by topic — local coherence within timeline
- **Threads**: Fragments linked by broader theme — can be scattered across conversation (non-consecutive)

This mirrors real conversation dynamics: you discuss budget with interruptions for other topics, then return to budget later. Threads capture this pattern; fragments capture the contiguous bits.

## Contributing

### Modifying the Schema

1. Edit `schema/conversation.json`
2. Regenerate types:
   ```bash
   npm run codegen:typescript
   python scripts/codegen-python.py
   ```
3. Test generators with examples:
   ```bash
   python examples/python/example_conversation.py
   node examples/typescript/example_conversation.ts
   ```
4. Create a pull request with schema changes and regenerated types

### Publishing a Release

Tag a version and push to GitHub:

```bash
git tag v1.0.1
git push origin v1.0.1
```

The GitHub Actions workflow automatically:
1. Regenerates types
2. Publishes to npm and PyPI
3. Creates a GitHub Release

## License

MIT — see [LICENSE](LICENSE)

## Maintainers

- Ushadow Contributors

## Related Projects

- [Chronicle](https://github.com/ushadow-io/chronicle) — Conversation storage and retrieval
- [Mycelia](https://github.com/ushadow-io/mycelia) — Conversation analysis and insights
