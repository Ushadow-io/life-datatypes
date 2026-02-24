#!/usr/bin/env node

const fs = require('fs')
const path = require('path')
const { compile } = require('json-schema-to-typescript')

async function generateTypeScript() {
  const schemaPath = path.join(__dirname, '../schema/conversation.json')
  const outputPath = path.join(__dirname, '../generated/typescript/index.ts')

  const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf-8'))

  try {
    const tsCode = await compile(schema, 'Conversation', {
      bannerComment: `/**
   * Auto-generated from schema/conversation.json
   * DO NOT EDIT DIRECTLY
   * Run: npm run codegen:typescript
   */`,
      declareExternallyReferenced: true,
    })

    fs.mkdirSync(path.dirname(outputPath), { recursive: true })
    fs.writeFileSync(outputPath, tsCode)
    console.log(`✓ Generated ${outputPath}`)
  } catch (error) {
    console.error('❌ TypeScript codegen failed:', error.message)
    process.exit(1)
  }
}

generateTypeScript()
