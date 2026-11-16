"""
Example: one morning of capture, modelled with life-datatypes v2.

It covers the cases the schema exists for:
- one conversation cut into two recordings by a file boundary, joined by a Link
- one recording that holds the end of one conversation and the start of the next (Link kind=split_at)
- a recording transcribed twice, and a human fix that both transcripts keep (Transcript, TranscriptCorrection)
- the same speaker labelled differently in each recording (Participant.speakerRefs)
- the same audio stored twice (Link kind=duplicate_of)
- TV dialogue picked up by the microphone (Speaker role=media)
- a recording that changes subject without a pause (two Fragments)
- a subject that returns after an interruption, across recordings (Thread)
- screen activity during the conversation, and a time with no capture (CaptureGap)
- a live transcript that is replaced by a final one (Transcript.status), where the audio is
  stored (Recording.audio), and an erased range inside one recording (CaptureGap with recordingId)
- facts taken from what was said, each with proof (Fact, EvidenceRef), and the entities they are about

Run from the repository root:
    PYTHONPATH=generated/python python examples/python/example_conversation.py
"""

from datetime import datetime, timezone

from life_datatypes import (
    AudioRef,
    CaptureBundle,
    CaptureGap,
    CaptureSource,
    Conversation,
    ConversationPart,
    Entity,
    EntityRef,
    EvidenceRef,
    Fact,
    FactSubject,
    FactValue,
    FrameRef,
    Fragment,
    Link,
    Participant,
    Recording,
    ScreenObservation,
    ScreenSample,
    Segment,
    Speaker,
    SpeakerRef,
    Thread,
    TimeRange,
    Transcript,
    TranscriptCorrection,
)


def at(hms: str) -> datetime:
    """A UTC time on 14 Nov 2026."""
    hour, minute, second = (int(part) for part in hms.split(":"))
    return datetime(2026, 11, 14, hour, minute, second, tzinfo=timezone.utc)


def span(start: str, end: str) -> TimeRange:
    return TimeRange(start=at(start), end=at(end))


pendant = CaptureSource(id="omi-pendant", kind="wearable", modalities=["audio_input"], device="Omi")
laptop = CaptureSource(id="laptop", kind="desktop", modalities=["screen"], device="MacBook Pro")

# Morning TV, heard by the pendant. Nobody here is talking to the owner.
tv = Recording(
    id="rec-tv",
    sourceId=pendant.id,
    modality="audio_input",
    range=span("07:14:46", "07:25:26"),
    origin="recovered",
    contentHash="sha256:7f1c",
    currentTranscriptRevision="rev-1",
)
tv_transcript = Transcript(
    recordingId="rec-tv",
    revision="rev-1",
    createdAt=at("07:30:00"),
    model="deepgram-nova-3",
    speakers=[Speaker(label="Speaker 0", role="media", confidence=0.9)],
    segments=[
        Segment(id="tv-1", text="Detective Carter from NYPD homicide.", speakerLabel="Speaker 0",
                start=at("07:15:02"), end=at("07:15:05")),
    ],
)
# The phone uploaded the same file twice.
tv_copy = tv.model_copy(update={"id": "rec-tv-copy"})

# One conversation, cut in two by the end of a downloaded file (10 seconds apart).
part_one = Recording(
    id="rec-a",
    sourceId=pendant.id,
    modality="audio_input",
    range=span("10:54:20", "11:05:31"),
    origin="recovered",
    startReason="silence",
    endReason="file_boundary",
    contentHash="sha256:a913",
    audio=AudioRef(uri="s3://example-bucket/audio/rec-a.opus", format="opus"),
    currentTranscriptRevision="rev-2",
)
part_one_speakers = [
        Speaker(label="Speaker 0", role="owner", personId="person-sam", displayName="Sam"),
        Speaker(label="Speaker 1", role="participant", personId="person-alex", displayName="Alex"),
]
# The first reading heard "menu". Segment ids belong to one revision only.
part_one_rev1 = Transcript(
    recordingId="rec-a",
    revision="rev-1",
    createdAt=at("11:30:00"),
    model="deepgram-nova-2",
    speakers=part_one_speakers,
    segments=[
        Segment(id="a-1", text="Shall we look at the launch budget?", speakerLabel="Speaker 0",
                start=at("10:54:25"), end=at("10:54:28")),
        Segment(id="a-2", text="Yes, marketing is over by about ten percent.", speakerLabel="Speaker 1",
                start=at("10:54:29"), end=at("10:54:33")),
        Segment(id="a-3", text="Different thing: did you book the menu?", speakerLabel="Speaker 1",
                start=at("11:02:10"), end=at("11:02:13")),
        Segment(id="a-4", text="Not yet, I'll do it today.", speakerLabel="Speaker 0",
                start=at("11:02:14"), end=at("11:02:16")),
    ],
)
# A better model read the recording again. rev-1 is kept. The segment ids are new; the times are not.
part_one_rev2 = Transcript(
    recordingId="rec-a",
    revision="rev-2",
    createdAt=at("18:00:00"),
    model="deepgram-nova-3",
    speakers=part_one_speakers,
    segments=[
        Segment(id="a2-1", text="Shall we look at the launch budget?", speakerLabel="Speaker 0",
                start=at("10:54:25"), end=at("10:54:28")),
        Segment(id="a2-2", text="Yes, marketing is over by about ten percent.", speakerLabel="Speaker 1",
                start=at("10:54:29"), end=at("10:54:33")),
        Segment(id="a2-3", text="Different thing: did you book the menu?", speakerLabel="Speaker 1",
                start=at("11:02:10"), end=at("11:02:13")),
        Segment(id="a2-4", text="Not yet, I'll do it today.", speakerLabel="Speaker 0",
                start=at("11:02:14"), end=at("11:02:16")),
    ],
)
# Both models heard "menu". The owner fixed it once. The fix is on a time range, so it applies to
# rev-1, to rev-2 and to any later revision.
venue_fix = TranscriptCorrection(
    id="fix-venue",
    recordingId="rec-a",
    range=span("11:02:10", "11:02:13"),
    text="Different thing: did you book the venue?",
    author="person-sam",
    recordedAt=at("12:15:00"),
)
part_two = Recording(
    id="rec-b",
    sourceId=pendant.id,
    modality="audio_input",
    range=span("11:05:41", "11:22:29"),
    origin="recovered",
    startReason="file_boundary",
    endReason="silence",
    contentHash="sha256:c04e",
    currentTranscriptRevision="rev-1",
)
# Live transcript, written while the recording was still going. It is provisional: it grows and may
# be replaced in place, until the final revision below exists. After that it is frozen.
part_two_live = Transcript(
    recordingId="rec-b",
    revision="live-1",
    status="provisional",
    createdAt=at("11:05:55"),
    model="deepgram-nova-3-streaming",
    speakers=[Speaker(label="Speaker 0", role="participant"), Speaker(label="Speaker 1", role="owner")],
    segments=[
        Segment(id="live-1", text="Back to the budget, can we cut paid ads?", speakerLabel="Speaker 0",
                start=at("11:05:43"), end=at("11:05:47")),
    ],
)
part_two_transcript = Transcript(
    recordingId="rec-b",
    revision="rev-1",
    status="final",
    createdAt=at("11:30:00"),
    model="deepgram-nova-3",
    # Diarization numbered the voices the other way round in this file.
    speakers=[
        Speaker(label="Speaker 0", role="participant", personId="person-alex", displayName="Alex"),
        Speaker(label="Speaker 1", role="owner", personId="person-sam", displayName="Sam"),
        Speaker(label="Speaker 2", role="participant", displayName="Plumber"),
    ],
    segments=[
        Segment(id="b-1", text="Back to the budget: can we cut paid ads?", speakerLabel="Speaker 0",
                start=at("11:05:43"), end=at("11:05:47")),
        Segment(id="b-2", text="Yes, move half of it to events.", speakerLabel="Speaker 1",
                start=at("11:05:48"), end=at("11:05:51")),
        # Alex leaves. Two minutes later the plumber calls. The pendant never stopped recording.
        Segment(id="b-3", text="Hi, it's the plumber. I can come about the leak on Friday.", speakerLabel="Speaker 2",
                start=at("11:08:02"), end=at("11:08:07")),
        Segment(id="b-4", text="Friday morning works.", speakerLabel="Speaker 1",
                start=at("11:08:08"), end=at("11:08:10")),
    ],
)

fragments = [
    # range is the anchor. segmentIds is optional and only valid for one transcript revision.
    Fragment(id="frag-budget-1", recordingId="rec-a", range=span("10:54:25", "10:54:33"),
             topic="launch budget", transcriptRevision="rev-2", segmentIds=["a2-1", "a2-2"]),
    Fragment(id="frag-venue", recordingId="rec-a", range=span("11:02:10", "11:02:16"), topic="venue booking"),
    Fragment(id="frag-budget-2", recordingId="rec-b", range=span("11:05:43", "11:05:51"), topic="launch budget"),
    Fragment(id="frag-leak", recordingId="rec-b", range=span("11:08:02", "11:08:10"), topic="leak repair"),
]

# Each Link is one saved decision. key names the question, so a later run finds the answer and does
# not decide again. A Link is never changed: to override one, add a Link that retracts it.
links = [
    Link(id="link-dup", kind="duplicate_of", fromId="rec-tv", toId="rec-tv-copy",
         key="duplicate_of:rec-tv:rec-tv-copy:p1", decidedBy="rule", policyVersion="p1",
         confidence=1.0, gapSeconds=-640, reason="same contentHash and range", recordedAt=at("07:31:00")),
    Link(id="link-cut", kind="continues", fromId="rec-a", toId="rec-b",
         key="continues:rec-a:rec-b:p1", decidedBy="rule", policyVersion="p1",
         confidence=0.95, gapSeconds=10, reason="file boundary, 10 s gap, same people",
         recordedAt=at("11:31:00")),
    # A model put the cut between the two conversations in rec-b ten seconds too early.
    Link(id="link-split-model", kind="split_at", fromId="rec-b", at=at("11:07:50"),
         key="split_at:rec-b:p1", decidedBy="model", model="small-gap-model", policyVersion="p1",
         confidence=0.7, reason="topic and people change", recordedAt=at("11:31:05")),
    # The owner moved it. The model's Link stays in the record; this one wins.
    Link(id="link-split-human", kind="split_at", fromId="rec-b", at=at("11:08:00"),
         key="split_at:rec-b:p1", decidedBy="human", reason="the plumber's call starts here",
         recordedAt=at("12:20:00"), retracts="link-split-model"),
]

screen = ScreenObservation(
    id="obs-sheet",
    sourceId=laptop.id,
    range=span("10:53:40", "11:20:05"),
    state="active",
    appName="Google Chrome",
    windowTitle="Launch budget - Google Sheets",
    url="https://docs.google.com/spreadsheets/d/example",
    samples=[
        ScreenSample(id="s-1", capturedAt=at("10:53:50"), trigger="open", textSource="accessibility",
                     text="Launch budget | Marketing 11,000 | Events 4,000",
                     frame=FrameRef(frameId="f-1029", capturedAt=at("10:53:50"), availability="local")),
    ],
)

alex = Entity(id="person-alex", kind="person", name="Alex", confirmed=True)
launch = Entity(id="project-launch", kind="project", name="Launch", aliases=["the launch"], confirmed=True)
venue_task = Entity(id="task-book-venue", kind="task", name="Book the venue", confirmed=True)

conversation = Conversation(
    id="conv-budget",
    revision=3,  # 1: first built. 2: the venue fix. 3: the owner moved the split.
    closedAt=at("11:38:00"),
    title="Launch budget with Alex",
    summary="Marketing is 10% over budget; half of paid ads moves to events. Venue still to book.",
    citations=[
        EvidenceRef(recordingId="rec-a", range=span("10:54:29", "10:54:33"), transcriptRevision="rev-2",
                    quote="Yes, marketing is over by about ten percent."),
        EvidenceRef(recordingId="rec-b", range=span("11:05:48", "11:05:51"), transcriptRevision="rev-1",
                    quote="Yes, move half of it to events."),
    ],
    range=span("10:54:25", "11:05:51"),
    parts=[
        ConversationPart(recordingId="rec-a", range=span("10:54:25", "11:02:16")),
        ConversationPart(recordingId="rec-b", range=span("11:05:43", "11:05:51")),
    ],
    participants=[
        Participant(id="p-sam", personId="person-sam", displayName="Sam", role="owner",
                    speakerRefs=[SpeakerRef(recordingId="rec-a", speakerLabel="Speaker 0"),
                                 SpeakerRef(recordingId="rec-b", speakerLabel="Speaker 1")]),
        Participant(id="p-alex", personId="person-alex", displayName="Alex", role="participant",
                    speakerRefs=[SpeakerRef(recordingId="rec-a", speakerLabel="Speaker 1"),
                                 SpeakerRef(recordingId="rec-b", speakerLabel="Speaker 0")]),
    ],
    fragmentIds=["frag-budget-1", "frag-venue", "frag-budget-2"],
    threads=[
        Thread(id="thread-budget", title="Launch budget",
               fragmentIds=["frag-budget-1", "frag-budget-2"], participantIds=["p-sam", "p-alex"]),
    ],
    screenObservationIds=["obs-sheet"],
    entityRefs=[
        EntityRef(entityId=alex.id, kind="person", name="Alex"),
        EntityRef(entityId=launch.id, kind="project", name="Launch"),
    ],
)
# The second conversation in rec-b starts at the human split.
plumber_call = Conversation(
    id="conv-plumber",
    revision=2,
    closedAt=at("11:40:00"),
    title="Plumber about the leak",
    range=span("11:08:02", "11:08:10"),
    parts=[ConversationPart(recordingId="rec-b", range=span("11:08:02", "11:08:10"))],
    fragmentIds=["frag-leak"],
)

# Facts: what was said or done, with proof. A fact is never changed and has no status.
# occurredAt is the recording time. recordedAt is when we learned it.
facts = [
    Fact(id="f000000000001", subject=FactSubject(kind="project", id=launch.id), key="decision_made",
         occurredAt=at("11:05:48"), recordedAt=at("11:38:10"), source="agent",
         value=FactValue(text="Half of the paid ads budget moves to events.", about=[launch.id, alex.id],
                         evidence=[EvidenceRef(recordingId="rec-b", range=span("11:05:48", "11:05:51"),
                                               transcriptRevision="rev-1",
                                               quote="Yes, move half of it to events.")])),
    Fact(id="f000000000002", subject=FactSubject(kind="task", id=venue_task.id), key="promise_made",
         occurredAt=at("11:02:14"), recordedAt=at("11:38:10"), source="agent",
         value=FactValue(text="Sam will book the venue today.", about=[venue_task.id, alex.id],
                         direction="owed_by_me", due="2026-11-14",
                         evidence=[EvidenceRef(recordingId="rec-a", range=span("11:02:14", "11:02:16"),
                                               transcriptRevision="rev-2",
                                               quote="Not yet, I'll do it today.")])),
    # Later the owner says it is done. Nothing above is edited: "open or done" is worked out from both facts.
    Fact(id="f000000000003", subject=FactSubject(kind="task", id=venue_task.id), key="done_reported",
         occurredAt=at("16:40:00"), recordedAt=at("16:40:00"), source="person",
         value=FactValue(text="Venue booked.")),
]

bundle = CaptureBundle(
    schemaVersion="2.0.0",
    range=TimeRange(start=datetime(2026, 11, 14, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2026, 11, 15, 0, 0, tzinfo=timezone.utc)),
    timezone="Europe/London",
    ownerPersonId="person-sam",
    sources=[pendant, laptop],
    recordings=[tv, tv_copy, part_one, part_two],
    transcripts=[tv_transcript, part_one_rev1, part_one_rev2, part_two_live, part_two_transcript],
    corrections=[venue_fix],
    fragments=fragments,
    screenObservations=[screen],
    gaps=[CaptureGap(id="gap-1", sourceId=pendant.id, range=span("07:48:10", "10:06:42"),
                     cause="not_recording"),
          # The user erased one minute of the TV recording: the words are gone, the range stays known.
          CaptureGap(id="gap-2", sourceId=pendant.id, recordingId="rec-tv",
                     range=span("07:20:00", "07:21:00"), cause="excluded")],
    links=links,
    conversations=[conversation, plumber_call],
    entities=[alex, launch, venue_task],
    facts=facts,
)

# Round-trip through JSON to prove the bundle is valid against the schema models.
restored = CaptureBundle.model_validate_json(bundle.model_dump_json())
print("✓ CaptureBundle valid")
print(f"  recordings: {len(restored.recordings)}  transcripts: {len(restored.transcripts)}  "
      f"fragments: {len(restored.fragments)}  links: {len(restored.links)}  "
      f"conversations: {len(restored.conversations)}  facts: {len(restored.facts)}")
conv = restored.conversations[0]
pause = (conv.parts[1].range.start - conv.parts[0].range.end).total_seconds()
print(f"  '{conv.title}': {len(conv.parts)} parts, pause of {pause:.0f} s between them")

# A decision is read by key: the newest Link that nothing retracts.
retracted = {link.retracts for link in restored.links if link.retracts}
split = [link for link in restored.links if link.key == "split_at:rec-b:p1" and link.id not in retracted]
print(f"  rec-b is split at {split[0].at:%H:%M:%S}, decided by {split[0].decidedBy.value}")

# A task has no status field. It is done if a done_reported fact follows the promise.
task = [fact for fact in restored.facts if fact.subject.id == "task-book-venue"]
done = any(fact.key == "done_reported" for fact in task)
print(f"  'Book the venue': {'done' if done else 'open'}, from {len(task)} facts")
