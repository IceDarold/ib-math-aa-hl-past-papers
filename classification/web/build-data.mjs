import { access, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const classificationRoot = resolve(here, '..');
const manualSource = resolve(classificationRoot, 'pilots/2024-november/questions.tsv');
const generatedRoot = resolve(classificationRoot, 'generated');
const sessionsPath = resolve(classificationRoot, 'pipeline/sessions.json');
const reviewPath = resolve(classificationRoot, 'reviews/2024-may-tz1/calibration-v1.json');
const output = resolve(here, 'src/data/questions.json');

const [raw, sessions, review] = await Promise.all([
  readFile(manualSource, 'utf8'),
  readFile(sessionsPath, 'utf8').then(JSON.parse),
  readFile(reviewPath, 'utf8').then(JSON.parse),
]);

const sessionBySlug = new Map(sessions.map((session) => [session.slug, session]));
const reviewedIds = new Set(review.reviews.map((item) => item.id));

function sourceFor(session, paper) {
  return session.sources?.[String(paper)] ?? session.source;
}

const [headerLine, ...lines] = raw.trim().split(/\r?\n/);
const headers = headerLine.split('\t');
const manualRows = lines.map((line) => Object.fromEntries(
  line.split('\t').map((value, index) => [headers[index], value])
)).map((row) => ({
  ...row,
  session: 'November 2024',
  zone: 'Common',
  source_root: 'AA_HL/2024/November/Common',
  review_status: 'manual_verified',
  method_family: '',
  markscheme_pages: row.source_pages,
  evidence: '[]',
  confidence: JSON.stringify({ segmentation: 'high', topic: 'high', method: 'high' }),
  review_flags: '',
}));

const generatedRows = [];
for (const entry of await readdir(generatedRoot, { withFileTypes: true })) {
  if (!entry.isDirectory()) continue;
  const session = sessionBySlug.get(entry.name);
  if (!session) continue;

  const resultRoot = resolve(generatedRoot, entry.name, 'deepseek-v4-pro');
  try {
    await access(resolve(resultRoot, 'manifest.json'));
  } catch {
    continue;
  }

  const papers = await Promise.all([1, 2, 3].map((paper) => (
    readFile(resolve(resultRoot, `paper-${paper}.json`), 'utf8').then(JSON.parse)
  )));

  generatedRows.push(...papers.flatMap((paper) => paper.blocks.map((block) => ({
    id: block.id,
    paper: String(paper.paper),
    question: block.question,
    part: block.part || '-',
    marks: String(block.marks),
    calculator: paper.calculator,
    source_pages: block.source_pages,
    markscheme_pages: block.markscheme_pages,
    task_summary: block.task_summary,
    primary_topic: block.primary_topic,
    secondary_topics: block.secondary_topics.join('|') || '-',
    method_family: block.method_family,
    method_tags: block.method_tags.join('|'),
    method_path: block.method_path.join('; '),
    accepted_alternatives: block.accepted_alternatives.join('|') || '-',
    session: paper.session,
    zone: paper.zone,
    source_root: sourceFor(session, paper.paper),
    review_status: reviewedIds.has(block.id) ? 'manual_verified' : 'ai_draft',
    evidence: JSON.stringify(block.evidence),
    confidence: JSON.stringify(block.confidence),
    review_flags: block.review_flags.join('|'),
  }))));
}

function sessionOrder(session) {
  const match = /^(May|November) (\d{4})$/.exec(session);
  if (!match) return Number.MAX_SAFE_INTEGER;
  return Number(match[2]) * 100 + (match[1] === 'May' ? 5 : 11);
}

const rows = [...manualRows, ...generatedRows].sort((a, b) => (
  sessionOrder(a.session) - sessionOrder(b.session)
  || a.zone.localeCompare(b.zone)
  || Number(a.paper) - Number(b.paper)
  || Number(a.question) - Number(b.question)
  || a.part.localeCompare(b.part)
));
const verified = rows.filter((row) => row.review_status === 'manual_verified').length;
const drafts = rows.length - verified;
const includedSessions = new Set(rows.map((row) => `${row.session}|${row.zone}`)).size;

await writeFile(output, `${JSON.stringify(rows, null, 2)}\n`);
console.log(`Wrote ${rows.length} rows from ${includedSessions} sessions (${verified} manually verified, ${drafts} AI draft) to ${output}`);
