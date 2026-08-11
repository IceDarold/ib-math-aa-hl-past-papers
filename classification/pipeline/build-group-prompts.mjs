#!/usr/bin/env node

import { access, mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repositoryRoot = resolve(here, '../..')
const workRoot = resolve(repositoryRoot, 'classification/work/2024-may-tz1')
const outputRoot = resolve(workRoot, 'groups')
const config = JSON.parse(await readFile(resolve(here, 'question-groups.json'), 'utf8'))

await mkdir(outputRoot, { recursive: true })
for (const [id, question] of Object.entries(config)) {
  const override = resolve(repositoryRoot, `classification/overrides/2024-may-tz1/${id}.md`)
  let source
  try {
    await access(override)
    source = await readFile(override, 'utf8')
  } catch {
    source = await readFile(resolve(workRoot, `questions/${id}.txt`), 'utf8')
    const firstPageMarker = source.indexOf('===== QUESTION PAPER')
    if (firstPageMarker === -1) throw new Error(`${id}: missing question-paper page marker`)
    source = source.slice(firstPageMarker)
  }
  for (const group of question.groups) {
    const prompt = `Classify only ${id}, ${group.scope}. Return no other parts.\n` +
      `For this group expected_question_marks=${group.marks}; its block marks must sum exactly to ${group.marks}.\n` +
      `Keep original question and part identifiers. Keep strings concise.\n\n${source}`
    const filename = `${id}-${group.id}.txt`
    await writeFile(resolve(outputRoot, filename), prompt.replaceAll('\f', ''))
    console.log(`${filename}: ${prompt.length.toLocaleString()} characters, ${group.marks} marks`)
  }
}
