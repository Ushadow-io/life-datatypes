# life-datatypes

[![npm version](https://img.shields.io/npm/v/life-datatypes.svg)](https://www.npmjs.com/package/life-datatypes)
[![PyPI version](https://img.shields.io/pypi/v/life-datatypes.svg)](https://pypi.org/project/life-datatypes/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Shared data types for captured life evidence (audio recordings, transcripts, screen activity),
the conversations derived from it, and the facts taken from those conversations, across the
Ushadow ecosystem: **Chronicle** (capture and
storage), **Mycelia** (analysis) and any service that reads or writes them.

## Core idea: capture units are not events

A **recording** is how audio was cut: by a silence, a button press, a dropped connection
or the end of a downloaded file. A **conversation** is what happened. They do not line
up:

- one conversation can pause and continue, so it spans several recordings;
- one recording can hold the end of one conversation and the start of the next;
- the same moment can be captured twice (the same file uploaded twice, or a phone and a
  pendant both listening).

The same is true on screen: a **screen observation** is one app/window from switch-in to
switch-out, not an activity.

So the schema keeps capture and meaning apart and connects them by id. Every time is
**absolute UTC**, so evidence from different recordings and devices lines up.

### One real morning

You plan the launch with Alex. You stop for coffee. You continue. The plumber calls. The pendant
goes on charge. Later the TV is on.

```
Time           08:55            09:20  09:26       09:40 09:41     09:52             10:30     10:45
What happened  |=== Launch plan with Alex ===|pause|== continues ==||== Plumber ==|  on charge     |  TV news  |
Recording      |============ A ==============|     |============== B =============|  CaptureGap    |==== C ====|
Fragment       |-- F1 Budget --|-- F2 Venue -|     |-F3 Budget-|-F4 Next-||-- F5 Leak ----|
Thread         "Budget" = F1 + F3   (the subject comes back after the pause)
Conversation   |======== 1, part 1 ==========|     |== 1, part 2 ==||===== 2 ======|                (none: media)
Link           continues: A -> B                                    split_at: B at 09:41
```

- Conversation 1 is in two recordings. A `Link` of kind `continues` joins A and B.
- Recording B holds the end of conversation 1 and all of conversation 2. A `Link` of kind
  `split_at` cuts it at 09:41.
- The coffee pause is the time between two parts of one conversation. It is not a gap.
- The time on charge is a `CaptureGap`. A reader can say "there is no data", not "nothing happened".
- Recording C is TV. Its speakers have the role `media`. It makes no conversation and no facts
  about the owner.

The lines inside F1 read like a screenplay. Each line is a `Segment`:

```
08:55:02  ALEX (participant)  Can we look at the budget first?
08:55:06  YOU  (owner)        Yes. The limit is 2,000.
```

The second line gives one `Fact`, `constraint_added {budget: 2000}`, whose `EvidenceRef` points
at recording A, 08:55:06, with the quote.

### The names, from small to large

```
CaptureBundle (one span, e.g. a local day)
├── CaptureSource        devices: pendant, phone, desktop
├── Recording            one continuous piece of audio, from cut to cut ("the tape")
├── Transcript           one reading of a recording; a recording can have several
│   ├── Speaker          a voice, with a label local to this recording, and a role
│   └── Segment          one line of speech (atomic unit)
├── TranscriptCorrection a human fix for a time range; applies to every transcript
├── Fragment             consecutive speech in ONE recording about one subject (a scene)
├── ScreenObservation    one app/window session
│   ├── ScreenSample     what was on screen at a moment
│   └── FrameRef         pointer to a frame (may be pruned on the device)
├── MeetingMarker        a meeting detected from a machine signal
├── CaptureGap           time when a source captured nothing
├── Link                 a saved decision: continues / split_at / duplicate_of / overlaps / unrelated
├── Conversation         time-bounded exchange, pauses allowed
│   ├── ConversationPart an interval of one recording; gaps between parts are pauses
│   ├── Participant      one person, mapped to every recording-local speaker label
│   └── Thread           fragments on one subject, possibly interrupted (a storyline)
├── Entity               a person, project, task, place or organisation
└── Fact                 something that was said or done, with proof (EvidenceRef)
```

| Name | In the real world | Rule | Made by |
|---|---|---|---|
| `Segment` | One line of speech | One speaker, until the speaker changes or pauses | Transcription |
| `Speaker` | A voice on one tape | The label is local to the recording | Transcription |
| `Recording` | The tape | From cut to cut. A cut is technical, not the end of a talk | Capture |
| `Transcript` | One reading of the tape | Never overwritten. A better reading is a new revision | Transcription |
| `Fragment` | A scene | Consecutive speech, one subject, one recording | Model, checked by code |
| `Thread` | A storyline | Fragments on one subject; they can be apart and in different recordings | Model |
| `ConversationPart` | "This piece of the tape is ours" | One time range of one recording | Code, from Links |
| `Participant` | A person in the talk | Joins the voices from each recording to one person | Speaker match, or a human |
| `Conversation` | The talk | One exchange between people. Pauses are allowed | Code, from Links |
| `Link` | "Same talk" or "new talk" | Decided once. A human Link wins | Rule, model or human |
| `CaptureGap` | The pendant was off | "No data" is not "nothing happened" | Code |
| `Fact` | "We agreed X" | Never changed. No status. Has proof | Model or human |

### Naming rules

- Types are `PascalCase` and singular. Fields are `camelCase`. A time ends in `At`; a reference
  ends in `Id` or `Ids`.
- Enum values are `snake_case` (`duplicate_of`).
- A fact `key` is `snake_case`: a thing plus a past verb (`task_requested`, `promise_made`). It
  says what happened. It never names a status.
- Use `Conversation`, `Recording` and `Fragment`. Do not add "episode", "session" or "chunk".

## Evidence is never overwritten

- **Point at time, not at segment ids.** Segment ids change when a recording is transcribed
  again. `Fragment`, `ConversationPart` and `EvidenceRef` point at a time range of a recording, so
  they stay valid.
- **A new transcript is a new `Transcript` revision.** `Recording.currentTranscriptRevision` says
  which one to use.
- **A human word fix is a `TranscriptCorrection`** on a time range. It applies to every revision.
- **A decision is a `Link`, found by `key`.** To override one, add a Link whose `retracts` is the
  old id.
- **A `Fact` has no status.** Whether it still counts is worked out from retractions and newer
  facts. This is the same shape as a taskfacts (`ushadow_facts`) fact.
- **Erasing is the one exception.** When the user erases a range, the words are removed and a
  `CaptureGap` with `cause: excluded` marks the range.

## Edge cases the schema covers

| Case | How it is modelled |
|---|---|
| A conversation continues after a pause, in a new recording | `Conversation.parts` has one `ConversationPart` per recording. A `Link` (`kind: continues`) stores the decision so it is not made again. |
| A recording ends for a technical reason, not a real ending | `Recording.startReason` / `endReason` (`silence`, `user_action`, `disconnect`, `file_boundary`, `size_limit`, `meeting_boundary`, …). |
| One recording holds two subjects with no pause | Two `Fragment`s over consecutive time ranges of the same recording. |
| One recording holds the end of one conversation and the start of the next | A `Link` with `kind: split_at` and the time in `at`. Each conversation takes one `ConversationPart` of the recording. |
| A subject returns after an interruption | A `Thread` lists the non-consecutive fragments, which may come from different recordings of the conversation. |
| "Speaker 0" is a different person in the next recording | `Speaker.label` is local to its recording. `Participant.speakerRefs` maps every label that is the same person; `personId` is set once someone is identified. |
| TV, radio or a video is picked up by the microphone | `Speaker.role: media` (or `background` for nearby people not addressed). System audio uses `Recording.modality: audio_output`. |
| The same audio stored twice | `Recording.contentHash`, and a `Link` with `kind: duplicate_of`. |
| Two devices captured the same moment | A `Link` with `kind: overlaps`. |
| Audio downloaded later from device storage | `Recording.origin: recovered` (vs `live`, `upload`, `import`). |
| A recording is transcribed again and segment ids change | A new `Transcript` with a new `revision`; the old one is kept. Everything else points at time ranges, so nothing breaks. |
| The transcript has a wrong word or a wrong speaker | A `TranscriptCorrection` on the time range. It applies to every transcript revision. |
| Audio for a past time arrives late | New recordings at their recorded times. A closed `Conversation` can change: its `revision` goes up and its `id` stays. |
| "Nothing was recorded" vs "recorded, nothing happened" | `CaptureGap` with a `cause`. Captured silence is simply a recording with no segments. |
| A meeting app defines where a conversation starts and ends | `MeetingMarker`, referenced by `Conversation.meetingId`. |
| A window reports no app name | `ScreenObservation.appName` is optional. |
| Screen frames are pruned on the device | `FrameRef.availability`: `local`, `uploaded` or `pruned`. |
| A human corrects a decision | A new `Link` with `decidedBy: human` and `retracts` set to the old Link. Tools must not override a human decision with a rule or model one. |
| The same question is asked again on a later run | `Link.key` identifies the question. The run reuses the Link and does not decide again. |
| A claim in a summary needs proof | `Conversation.citations`: `EvidenceRef`s with the recording, the time range and the quote. |
| Something was agreed, promised or asked for | A `Fact` (`decision_made`, `promise_made`, `task_requested`) with `value.evidence`. |
| A task is done, or a fact was wrong | A new `Fact` (`done_reported`), or a `Fact` whose `retracts` is the wrong one. Nothing is edited. |
| Two names are the same person | A `Fact` with key `same_entity`. |
| A bystander is heard | An `Entity` with `confirmed: false`. No profile until the user confirms. |
| The user erases what was said | The words are removed, and a `CaptureGap` with `cause: excluded` covers the range. |

## Rules the JSON Schema cannot check

Validators should enforce these in code:

1. A `TimeRange` has `end >= start`.
2. A `Fragment`'s `range` is inside its recording's `range`. If `segmentIds` is set, the ids are consecutive within `transcriptRevision`.
3. `Conversation.parts` are in time order and do not overlap; `Conversation.range` covers them.
4. Every `SpeakerRef` points to a label that exists in a transcript of that recording.
5. A `Thread`'s fragments belong to the conversation that contains the thread.
6. Text is not copied upward: fragments and threads reference time ranges instead of repeating text. An `EvidenceRef.quote` is the one allowed copy.
7. A `Transcript.revision` is unique within its recording. `Recording.currentTranscriptRevision` names one that exists.
8. A `Link` of kind `split_at` has `at` and no `toId`. Every other kind has `toId`.
9. For one `Link.key`, the Link that counts is the newest one that no other Link retracts. A `human` Link is not retracted by a `rule` or `model` Link.
10. A `Fact` with `source: agent` has at least one `value.evidence` entry.

## Installation

```bash
pip install life-datatypes     # Python (Pydantic v2)
npm install life-datatypes     # TypeScript
```

```python
from life_datatypes import CaptureBundle, Conversation, Fact, Link, Recording, Transcript
```

```typescript
import type { CaptureBundle, Conversation, Fact, Link, Recording, Transcript } from 'life-datatypes'
```

## Examples

- [`examples/python/example_conversation.py`](examples/python/example_conversation.py): a full
  morning with a split conversation, two conversations in one recording, a second transcript and
  a human word fix, a duplicate recording, TV audio, a returning subject, screen context, a
  capture gap, and facts with proof.
- [`examples/typescript/example_conversation.ts`](examples/typescript/example_conversation.ts):
  a split conversation joined by a `Link`, with a transcript and one fact.

```bash
PYTHONPATH=generated/python python examples/python/example_conversation.py
npx -p typescript tsc --noEmit --strict examples/typescript/example_conversation.ts
```

## Schema design

- **Single source of truth:** `schema/conversation.json` (JSON Schema Draft 7).
- **Generated types:** Pydantic v2 models and TypeScript types are generated from it.
- **References, not copies:** a `CaptureBundle` holds each item once; everything else refers to it by id.
- **Named enums:** every enum is its own definition (`SpeakerRole`, `CutReason`, `LinkKind`, …), so generated code has stable names.
- **Extensibility:** `metadata` on most types for provider-specific data. Unknown top-level fields are rejected.

## Contributing

### Modifying the schema

1. Edit `schema/conversation.json`.
2. Regenerate types:
   ```bash
   npm install
   npm run codegen:typescript
   pip install datamodel-code-generator
   python scripts/codegen-python.py
   ```
3. Run both examples (above).
4. Open a pull request with the schema change.

### Publishing a release

Tag a version and push it. The workflow regenerates types and publishes to npm and PyPI.

```bash
git tag v2.0.0
git push origin v2.0.0
```

## License

MIT, see [LICENSE](LICENSE).

## Related projects

- [Chronicle](https://github.com/ushadow-io/chronicle): capture, storage and retrieval
- [Mycelia](https://github.com/ushadow-io/mycelia): conversation analysis and insights
