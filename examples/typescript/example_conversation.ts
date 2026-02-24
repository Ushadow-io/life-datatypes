/**
 * Example: Parse a conversation from transcribed data using life-datatypes
 */

import { Segment, Fragment, Thread, Conversation } from '../generated/typescript'
import { randomUUID } from 'crypto'

// Create segments from ASR output
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
]

// Create fragments (semantic units)
const fragments: Fragment[] = [
  {
    id: randomUUID(),
    text: 'Hello, how are you today?',
    segmentId: segments[0].id,
    type: 'utterance',
    metadata: { intent: 'greeting' },
  },
  {
    id: randomUUID(),
    text: "I'm doing great, thanks for asking.",
    segmentId: segments[1].id,
    type: 'utterance',
    metadata: { sentiment: 'positive' },
  },
]

// Create threads (topical coherence)
const threads: Thread[] = [
  {
    id: randomUUID(),
    title: 'Opening Greeting',
    description: 'Initial pleasantries and greeting exchange',
    fragmentIds: [fragments[0].id, fragments[1].id],
    participants: ['alice', 'bob'],
    startTime: 0.0,
    endTime: 5.2,
  },
]

// Assemble the full conversation
const conversation: Conversation = {
  id: randomUUID(),
  title: 'Alice and Bob Conversation',
  description: 'A simple greeting conversation',
  participants: ['alice', 'bob'],
  startTime: new Date('2024-02-24T10:00:00Z').toISOString(),
  endTime: new Date('2024-02-24T10:05:00Z').toISOString(),
  duration: 300.0,
  segments,
  fragments,
  threads,
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
