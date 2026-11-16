/**
 * Example: one conversation cut into two recordings, modelled with life-datatypes v2.
 *
 * - The pendant's file ended mid-conversation (endReason: file_boundary).
 * - A Link records the decision that the second recording continues the first.
 * - The words are in Transcript, one per reading of a recording, not in Recording.
 * - A Fact keeps what was decided, with an EvidenceRef as proof.
 * - Diarization swapped the labels between files; Participant.speakerRefs maps both.
 * - Screen activity during the conversation is attached as context.
 *
 * The Python example covers more cases (duplicates, TV audio, gaps, threads).
 */

import type {
  CaptureBundle,
  Conversation,
  Fact,
  Link,
  Recording,
  ScreenObservation,
  Transcript,
} from '../../generated/typescript'

const recordings: Recording[] = [
  {
    id: 'rec-a',
    sourceId: 'omi-pendant',
    modality: 'audio_input',
    range: { start: '2026-11-14T10:54:20Z', end: '2026-11-14T11:05:31Z' },
    origin: 'recovered',
    startReason: 'silence',
    endReason: 'file_boundary',
    currentTranscriptRevision: 'rev-1',
  },
  {
    id: 'rec-b',
    sourceId: 'omi-pendant',
    modality: 'audio_input',
    range: { start: '2026-11-14T11:05:41Z', end: '2026-11-14T11:22:29Z' },
    origin: 'recovered',
    startReason: 'file_boundary',
    endReason: 'silence',
    currentTranscriptRevision: 'rev-1',
  },
]

// One reading of each recording. A better model later adds a new revision; this one is kept.
const transcripts: Transcript[] = [
  {
    recordingId: 'rec-a',
    revision: 'rev-1',
    createdAt: '2026-11-14T11:30:00Z',
    speakers: [
      { label: 'Speaker 0', role: 'owner', personId: 'person-sam' },
      { label: 'Speaker 1', role: 'participant', personId: 'person-alex' },
    ],
    segments: [
      {
        id: 'a-1',
        text: 'Shall we look at the launch budget?',
        speakerLabel: 'Speaker 0',
        start: '2026-11-14T10:54:25Z',
        end: '2026-11-14T10:54:28Z',
      },
    ],
  },
  {
    recordingId: 'rec-b',
    revision: 'rev-1',
    createdAt: '2026-11-14T11:30:00Z',
    speakers: [
      { label: 'Speaker 0', role: 'participant', personId: 'person-alex' },
      { label: 'Speaker 1', role: 'owner', personId: 'person-sam' },
    ],
    segments: [
      {
        id: 'b-1',
        text: 'Back to the budget: can we cut paid ads?',
        speakerLabel: 'Speaker 0',
        start: '2026-11-14T11:05:43Z',
        end: '2026-11-14T11:05:47Z',
      },
      {
        id: 'b-2',
        text: 'Yes, move half of it to events.',
        speakerLabel: 'Speaker 1',
        start: '2026-11-14T11:05:48Z',
        end: '2026-11-14T11:05:51Z',
      },
    ],
  },
]

const cut: Link = {
  id: 'link-cut',
  kind: 'continues',
  fromId: 'rec-a',
  toId: 'rec-b',
  // key names the question. A later run finds this Link by key and does not decide again.
  key: 'continues:rec-a:rec-b:p1',
  decidedBy: 'rule',
  policyVersion: 'p1',
  confidence: 0.95,
  gapSeconds: 10,
  reason: 'file boundary, 10 s gap, same people',
  recordedAt: '2026-11-14T11:31:00Z',
}

const screen: ScreenObservation = {
  id: 'obs-sheet',
  sourceId: 'laptop',
  range: { start: '2026-11-14T10:53:40Z', end: '2026-11-14T11:20:05Z' },
  state: 'active',
  appName: 'Google Chrome',
  windowTitle: 'Launch budget - Google Sheets',
}

const conversation: Conversation = {
  id: 'conv-budget',
  revision: 1,
  closedAt: '2026-11-14T11:38:00Z',
  title: 'Launch budget with Alex',
  range: { start: '2026-11-14T10:54:25Z', end: '2026-11-14T11:05:51Z' },
  parts: [
    { recordingId: 'rec-a', range: { start: '2026-11-14T10:54:25Z', end: '2026-11-14T10:54:28Z' } },
    { recordingId: 'rec-b', range: { start: '2026-11-14T11:05:43Z', end: '2026-11-14T11:05:51Z' } },
  ],
  participants: [
    {
      id: 'p-sam',
      personId: 'person-sam',
      role: 'owner',
      speakerRefs: [
        { recordingId: 'rec-a', speakerLabel: 'Speaker 0' },
        { recordingId: 'rec-b', speakerLabel: 'Speaker 1' },
      ],
    },
    {
      id: 'p-alex',
      personId: 'person-alex',
      role: 'participant',
      speakerRefs: [
        { recordingId: 'rec-a', speakerLabel: 'Speaker 1' },
        { recordingId: 'rec-b', speakerLabel: 'Speaker 0' },
      ],
    },
  ],
  screenObservationIds: [screen.id],
  entityRefs: [{ entityId: 'project-launch', kind: 'project', name: 'Launch' }],
}

// What was decided, with proof. The proof points at a time range of the recording, so it stays
// valid when the recording is transcribed again.
const decision: Fact = {
  id: 'f000000000001',
  subject: { kind: 'project', id: 'project-launch' },
  key: 'decision_made',
  occurredAt: '2026-11-14T11:05:48Z',
  recordedAt: '2026-11-14T11:38:10Z',
  source: 'agent',
  value: {
    text: 'Half of the paid ads budget moves to events.',
    about: ['project-launch', 'person-alex'],
    evidence: [
      {
        recordingId: 'rec-b',
        range: { start: '2026-11-14T11:05:48Z', end: '2026-11-14T11:05:51Z' },
        transcriptRevision: 'rev-1',
        quote: 'Yes, move half of it to events.',
      },
    ],
  },
}

const bundle: CaptureBundle = {
  schemaVersion: '2.0.0',
  range: { start: '2026-11-14T00:00:00Z', end: '2026-11-15T00:00:00Z' },
  timezone: 'Europe/London',
  sources: [
    { id: 'omi-pendant', kind: 'wearable', modalities: ['audio_input'] },
    { id: 'laptop', kind: 'desktop', modalities: ['screen'] },
  ],
  recordings,
  transcripts,
  screenObservations: [screen],
  links: [cut],
  conversations: [conversation],
  entities: [{ id: 'project-launch', kind: 'project', name: 'Launch' }],
  facts: [decision],
}

console.log(`✓ ${bundle.conversations?.[0].title}: ${conversation.parts.length} parts, ${bundle.facts?.length} fact`)
