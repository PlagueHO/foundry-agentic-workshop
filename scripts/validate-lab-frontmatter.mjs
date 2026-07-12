import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const trackNames = [
  'introduction-foundry-agent-service',
  'agent-framework-dotnet',
]
const requiredKeys = [
  'title',
  'description',
  'lastUpdated',
  'track',
  'module',
  'slug',
  'estimatedTimeMinutes',
  'difficulty',
  'prerequisites',
  'audience',
  'technologies',
  'tags',
  'status',
  'contentType',
]
const allowedDifficulties = new Set(['beginner', 'intermediate', 'advanced'])
const allowedStatuses = new Set(['active', 'draft'])

function parseFrontMatter(markdown) {
  const openingMatch = markdown.match(/^---\r?\n/)
  if (!openingMatch) return null

  const closingMatch = markdown.match(/\r?\n---\r?\n/)
  if (!closingMatch || closingMatch.index === undefined) return null

  const end = closingMatch.index
  const closingLength = closingMatch[0].length

  const values = {}
  for (const line of markdown.slice(openingMatch[0].length, end).split(/\r?\n/)) {
    const match = line.match(/^([A-Za-z][A-Za-z0-9.]*)\s*:\s*(.*)$/)
    if (match) {
      const value = match[2].replace(/^['"]|['"]$/g, '')
      values[match[1]] = value || 'defined'
    }
  }
  return { values, body: markdown.slice(end + closingLength) }
}

async function moduleReadmes() {
  const files = []
  for (const track of trackNames) {
    const trackPath = path.join(repoRoot, 'labs', track)
    const entries = await fs.readdir(trackPath, { withFileTypes: true })
    for (const entry of entries) {
      if (entry.isDirectory() && /^\d{2}-/.test(entry.name)) {
        files.push({ track, slug: entry.name, path: path.join(trackPath, entry.name, 'README.md') })
      }
    }
  }
  return files.sort((a, b) => a.path.localeCompare(b.path))
}

const errors = []
for (const module of await moduleReadmes()) {
  const markdown = await fs.readFile(module.path, 'utf8')
  const parsed = parseFrontMatter(markdown)
  const relativePath = path.relative(repoRoot, module.path).replaceAll(path.sep, '/')

  if (!parsed) {
    errors.push(`${relativePath}: missing front matter at line 1`)
    continue
  }

  for (const key of requiredKeys) {
    if (!(key in parsed.values) || parsed.values[key] === '') {
      errors.push(`${relativePath}: missing ${key}`)
    }
  }

  const moduleNumber = Number.parseInt(module.slug.slice(0, 2), 10)
  if (parsed.values.track !== module.track) errors.push(`${relativePath}: track does not match path`)
  if (Number(parsed.values.module) !== moduleNumber) errors.push(`${relativePath}: module does not match path`)
  if (parsed.values.slug !== module.slug) errors.push(`${relativePath}: slug does not match path`)
  if (!Number.isInteger(Number(parsed.values.estimatedTimeMinutes))) errors.push(`${relativePath}: estimatedTimeMinutes must be an integer`)
  if (!/^\d{4}-\d{2}-\d{2}$/.test(parsed.values.lastUpdated)) errors.push(`${relativePath}: lastUpdated must use YYYY-MM-DD format`)
  if (!allowedDifficulties.has(parsed.values.difficulty)) errors.push(`${relativePath}: invalid difficulty`)
  if (!allowedStatuses.has(parsed.values.status)) errors.push(`${relativePath}: invalid status`)
  if (parsed.values.contentType !== 'lab') errors.push(`${relativePath}: contentType must be lab`)

  const heading = parsed.body.match(/^#\s+(.+)$/m)?.[1]
  if (heading !== parsed.values.title) errors.push(`${relativePath}: title does not match H1`)
}

if (errors.length > 0) {
  console.error(errors.join('\n'))
  process.exitCode = 1
} else {
  console.log(`Validated front matter for ${(await moduleReadmes()).length} lab modules`)
}
