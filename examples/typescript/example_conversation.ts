/**
 * Example: Build a conversation from segments, fragments, and threads using life-datatypes
 *
 * Hierarchy:
 * - Segments: Atomic timeline units (speaker lines, delimited by speaker change/pause)
 * - Fragments: Consecutive segments grouped by topic (discussion of one subject)
 * - Threads: Non-consecutive fragments grouped by broader topic (meta-themes)
 */

import { Segment, Fragment, Thread, Conversation } from '../generated/typescript'
import { randomUUID } from 'crypto'

// Create segments from ASR output (chronological order)
// Each segment is a line of dialog (speaker change or pause boundary)
const segments: Segment[] = [
  {
    id: randomUUID(),
    text: 'Hello, how are you today?',
    speaker: 'alice',
    start: 0.0,
    end: 2.5,
    confidence: 0.98,
    language: 'en',
  },
  {
    id: randomUUID(),
    text: "I'm doing great, thanks for asking.",
    speaker: 'bob',
    start: 3.0,
    end: 5.2,
    confidence: 0.96,
    language: 'en',
  },
  {
    id: randomUUID(),
    text: 'I wanted to discuss the quarterly budget.',
    speaker: 'alice',
    start: 6.0,
    end: 8.5,
    confidence: 0.94,
    language: 'en',
  },
]

// Create fragments: consecutive segments with same topic
const fragments: Fragment[] = [
  {
    id: randomUUID(),
    text: "Hello, how are you today? I'm doing great, thanks for asking.",
    segmentIds: [segments[0].id, segments[1].id],  // Consecutive greeting exchange
    type: 'utterance',
    metadata: { topic: 'greeting' },
  },
  {
    id: randomUUID(),
    text: 'I wanted to discuss the quarterly budget.',
    segmentIds: [segments[2].id],  // Budget discussion starts
    type: 'utterance',
    metadata: { topic: 'budget' },
  },
]

// Create threads: fragments grouped by broader topic (can be non-consecutive)
const threads: Thread[] = [
  {
    id: randomUUID(),
    title: 'Opening Ceremony',
    description: 'Initial greeting and pleasantries',
    fragmentIds: [fragments[0].id],
    participants: ['alice', 'bob'],
    startTime: 0.0,
    endTime: 5.2,
  },
]

// Assemble the full conversation
const conversation: Conversation = {
  id: randomUUID(),
  title: 'Alice and Bob Meeting',
  description: 'A meeting between Alice and Bob',
  participants: ['alice', 'bob'],
  startTime: new Date('2024-02-24T10:00:00Z').toISOString(),
  endTime: new Date('2024-02-24T10:10:00Z').toISOString(),
  duration: 600.0,
  segments,  // Atomic timeline
  fragments,  // Consecutive topic groupings
  threads,  // Broader topic themes
  metadata: {
    source: 'deepgram',
    quality: 'high',
    recording_device: 'conference_microphone',
  },
}

// Print summary
console.log('✓ Conversation created successfully')
console.log(`  ID: ${conversation.id}`)
console.log(`  Title: ${conversation.title}`)
console.log(`  Participants: ${conversation.participants.join(', ')}`)
console.log(`  Segments: ${conversation.segments.length}`)
console.log(`  Fragments: ${conversation.fragments.length}`)
console.log(`  Threads: ${conversation.threads.length}`)

// Serialize to JSON
console.log('\nSerialized conversation (first 500 chars):')
console.log(JSON.stringify(conversation, null, 2).substring(0, 500) + '...')
