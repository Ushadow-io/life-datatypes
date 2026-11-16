#!/usr/bin/env node

const fs = require('fs')
const path = require('path')
const { compile } = require('json-schema-to-typescript')

async function generateTypeScript() {
  const schemaPath = path.join(__dirname, '../schema/conversation.json')
  const outputPath = path.join(__dirname, '../generated/typescript/index.ts')

  const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf-8'))

  // The schema is a set of definitions with no root type. Give the compiler a root
  // that references every definition, so each one is emitted as a named export.
  const root = {
    title: 'LifeDataTypes',
    type: 'object',
    properties: Object.fromEntries(
      Object.keys(schema.definitions).map((name) => [name, { $ref: `#/definitions/${name}` }])
    ),
    additionalProperties: false,
    definitions: schema.definitions,
  }

  try {
    const tsCode = await compile(root, 'LifeDataTypes', {
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
