import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(here, '../pilots/2024-november/questions.tsv');
const output = resolve(here, 'src/data/questions.json');
const raw = await readFile(source, 'utf8');
const [headerLine, ...lines] = raw.trim().split(/\r?\n/);
const headers = headerLine.split('\t');
const rows = lines.map((line) => Object.fromEntries(
  line.split('\t').map((value, index) => [headers[index], value])
));

await writeFile(output, `${JSON.stringify(rows, null, 2)}\n`);
console.log(`Wrote ${rows.length} rows to ${output}`);
