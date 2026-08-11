import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(here, '../pilots/2024-november/questions.tsv');
const generatedRoot = resolve(here, '../generated/2024-may-tz1/deepseek-v4-pro');
const reviewPath = resolve(here, '../reviews/2024-may-tz1/calibration-v1.json');
const output = resolve(here, 'src/data/questions.json');
const raw = await readFile(source, 'utf8');
const [headerLine, ...lines] = raw.trim().split(/\r?\n/);
const headers = headerLine.split('\t');
const manualRows = lines.map((line) => Object.fromEntries(
  line.split('\t').map((value, index) => [headers[index], value])
)).map((row) => ({
  ...row,
  session: 'November 2024',
  zone: 'Common',
  review_status: 'manual_verified',
  method_family: '',
  markscheme_pages: row.source_pages,
  evidence: '[]',
  confidence: JSON.stringify({ segmentation: 'high', topic: 'high', method: 'high' }),
  review_flags: '',
}));

const generatedPapers = await Promise.all([1, 2, 3].map(async (paper) => (
  JSON.parse(await readFile(resolve(generatedRoot, `paper-${paper}.json`), 'utf8'))
)));
const review = JSON.parse(await readFile(reviewPath, 'utf8'));
const reviewedIds = new Set(review.reviews.map((item) => item.id));
const generatedRows = generatedPapers.flatMap((paper) => paper.blocks.map((block) => ({
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
  review_status: reviewedIds.has(block.id) ? 'manual_verified' : 'ai_draft',
  evidence: JSON.stringify(block.evidence),
  confidence: JSON.stringify(block.confidence),
  review_flags: block.review_flags.join('|'),
})));

const rows = [...manualRows, ...generatedRows];
const generatedReviewed = generatedRows.filter((row) => row.review_status === 'manual_verified').length;
const generatedDraft = generatedRows.length - generatedReviewed;

await writeFile(output, `${JSON.stringify(rows, null, 2)}\n`);
console.log(`Wrote ${rows.length} rows (${manualRows.length + generatedReviewed} manually verified, ${generatedDraft} AI draft) to ${output}`);
