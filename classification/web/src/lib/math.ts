export interface TextSegment {
  type: 'text' | 'math'
  value: string
  source?: string
  display?: boolean
}

interface Token {
  value: string
  start: number
  end: number
}

interface Range {
  start: number
  end: number
}

const tokenPattern = /[A-Za-z]+[A-Za-z0-9_']*|\d+(?:\.\d+)?(?:…|\.\.\.)?|<=|>=|!=|\+\/-|->|[α-ωΑ-Ωℝℤ∞Π₀₁₂₃₄₅₆₇₈₉]+|[^\s]/gu
const anchorPattern = /^(?:=|<|>|<=|>=|!=|≤|≥|≠|≈|∈|→|⇒|∥|\^|√|×|·|\/|±|\+\/-|->|[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻ⁿ]+)$/u
const punctuationBoundary = new Set([',', ';', ':', '.'])
const opening = new Set(['(', '[', '{'])
const closing = new Set([')', ']', '}'])

const mathWords = new Set([
  'alpha', 'beta', 'gamma', 'delta', 'theta', 'lambda', 'mu', 'sigma', 'phi', 'pi',
  'sin', 'cos', 'tan', 'cosec', 'csc', 'sec', 'cot', 'arcsin', 'arccos', 'arctan',
  'ln', 'log', 'exp', 'sqrt', 'lim', 'arg', 'cis', 'mod', 'det', 'min', 'max',
  'dx', 'dy', 'dt', 'dr', 'du', 'dv', 'dw', 'dz', 'dtheta', 'dlambda',
  'IQR', 'Re', 'Im', 'rad', 'kg', 'cm', 'mm', 'ms',
]);

const namedFunctions = new Set([
  'sin', 'cos', 'tan', 'cosec', 'csc', 'sec', 'cot', 'arcsin', 'arccos', 'arctan',
  'ln', 'log', 'exp', 'sqrt', 'lim', 'arg', 'cis', 'P', 'E', 'f', 'g', 'h', 'p', 'v',
]);

const proseStopWords = new Set([
  'and', 'as', 'at', 'by', 'do', 'for', 'from', 'if', 'in', 'is', 'of', 'on', 'or', 'so', 'the', 'to', 'via', 'with',
]);

const greekNames: Record<string, string> = {
  alpha: String.raw`\alpha `,
  beta: String.raw`\beta `,
  gamma: String.raw`\gamma `,
  delta: String.raw`\delta `,
  theta: String.raw`\theta `,
  lambda: String.raw`\lambda `,
  mu: String.raw`\mu `,
  sigma: String.raw`\sigma `,
  phi: String.raw`\phi `,
  pi: String.raw`\pi `,
};

const unicodeGreek: Record<string, string> = {
  α: String.raw`\alpha `, β: String.raw`\beta `, γ: String.raw`\gamma `, δ: String.raw`\delta `,
  θ: String.raw`\theta `, λ: String.raw`\lambda `, μ: String.raw`\mu `, σ: String.raw`\sigma `,
  φ: String.raw`\phi `, π: String.raw`\pi `, Π: String.raw`\Pi `,
};

const superscripts: Record<string, string> = {
  '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5',
  '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁺': '+', '⁻': '-', 'ⁿ': 'n', 'ⁱ': 'i',
};

const subscripts: Record<string, string> = {
  '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
  '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
};

export function tokenizeMathText(text: string): TextSegment[] {
  const explicit = /\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$/gu
  const segments: TextSegment[] = [];
  let cursor = 0;
  let match: RegExpExecArray | null;

  while ((match = explicit.exec(text)) !== null) {
    if (match.index > cursor) segments.push(...tokenizeImplicitMath(text.slice(cursor, match.index)));
    const value = (match[1] ?? match[2] ?? '').trim();
    if (value) segments.push({ type: 'math', value, source: value, display: Boolean(match[1]) });
    cursor = match.index + match[0].length;
  }
  if (cursor < text.length) segments.push(...tokenizeImplicitMath(text.slice(cursor)));
  return segments.length ? segments : [{ type: 'text', value: text }];
}

function tokenizeImplicitMath(text: string): TextSegment[] {
  const tokens = [...text.matchAll(tokenPattern)].map((match) => ({
    value: match[0],
    start: match.index,
    end: match.index + match[0].length,
  }));
  const ranges: Range[] = [];

  tokens.forEach((token, index) => {
    if (anchorPattern.test(token.value)) ranges.push(expandFromAnchor(tokens, index));
    if (isFunctionStart(tokens, index)) {
      const endIndex = findClosingToken(tokens, index + 1);
      if (endIndex !== -1) ranges.push({ start: token.start, end: tokens[endIndex]!.end });
    }
  });

  for (const match of text.matchAll(/\((?:\s*[−+\-]?(?:\d+(?:\.\d+)?|[A-Za-zα-ωΑ-Ω])\s*,){1,}\s*[−+\-]?(?:\d+(?:\.\d+)?|[A-Za-zα-ωΑ-Ω])\s*\)/gu)) {
    ranges.push({ start: match.index, end: match.index + match[0].length });
  }

  const merged = mergeRanges(ranges.filter((range) => isUsefulFormula(text.slice(range.start, range.end))));
  if (merged.length === 0) return [{ type: 'text', value: text }];

  const segments: TextSegment[] = [];
  let cursor = 0;
  for (const range of merged) {
    if (range.start > cursor) segments.push({ type: 'text', value: text.slice(cursor, range.start) });
    const source = text.slice(range.start, range.end);
    segments.push({ type: 'math', value: toKatex(source), source });
    cursor = range.end;
  }
  if (cursor < text.length) segments.push({ type: 'text', value: text.slice(cursor) });
  return segments;
}

export function toKatex(source: string): string {
  let value = convertGroups(source.trim());

  value = value
    .replace(/Σᵢ₌([₀₁₂₃₄₅₆₇₈₉])([⁰¹²³⁴⁵⁶⁷⁸⁹ⁿ])/gu, (_, lower: string, upper: string) => String.raw`\sum_{i=${subscripts[lower]}}^{${superscripts[upper]}}`)
    .replace(/[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻ⁿⁱ]+/gu, (run) => `^{${[...run].map((character) => superscripts[character]).join('')}}`)
    .replace(/[₀₁₂₃₄₅₆₇₈₉]+/gu, (run) => `_{${[...run].map((character) => subscripts[character]).join('')}}`)
    .replace(/\bd\^([A-Za-z0-9]+)([A-Za-z]?)\s*\/\s*d([A-Za-z]+)\^\1\b/g, (_, order: string, dependent: string, independent: string) => String.raw`\frac{d^{${order}}${dependent}}{d${independent}^{${order}}}`)
    .replace(/\b(d(?:[A-Za-z]|theta|lambda))\s*\/\s*d([A-Za-z]|theta|lambda)\b/gi, (_, numerator: string, denominator: string) => String.raw`\frac{${replaceGreek(numerator)}}{d${replaceGreek(denominator)}}`)
    .replace(/\bd\s*\/\s*d([A-Za-z]|theta|lambda)\b/gi, (_, denominator: string) => String.raw`\frac{d}{d${replaceGreek(denominator)}}`)
    .replace(/(?<![A-Za-z\^_])(\([^()]+\))\s*\/\s*(\([^()]+\))(?![\^⁰¹²³⁴⁵⁶⁷⁸⁹])/gu, String.raw`\frac{$1}{$2}`)
    .replace(/(?<![\^_])([A-Za-zα-ωΑ-Ω0-9]+)\s*\/\s*([A-Za-zα-ωΑ-Ω0-9]+)(?![\^⁰¹²³⁴⁵⁶⁷⁸⁹])/gu, String.raw`\frac{$1}{$2}`)
    .replace(/(?<![A-Za-z\\])(arcsin|arccos|arctan|sin|cos|tan|cosec|csc|sec|cot|ln|log|exp)(\d*[a-z]|\d+)\b/g, (_, name: string, argument: string) => `\\${name === 'cosec' ? 'csc' : name} ${argument}`)
    .replace(/(?<!\\)\b(arcsin|arccos|arctan|sin|cos|tan|cosec|csc|sec|cot|ln|log|exp|lim|arg)\b/g, (name) => `\\${name === 'cosec' ? 'csc' : name}`)
    .replace(/\bcis\b/g, String.raw`\operatorname{cis}`)
    .replace(/\bIQR\b/g, String.raw`\operatorname{IQR}`)
    .replace(/\b(Re|Im)\b/g, String.raw`\operatorname{$1}`)
    .replace(/\b(ms|rad|kg|cm|mm)\b/g, String.raw`\mathrm{$1}`)
    .replace(/\b([A-Za-z])_(\w+)\b/g, '$1_{$2}')
    .replace(/\b([A-Za-z])(\d+)\b/g, '$1_{$2}')
    .replace(/\^([A-Za-z]|\d+)\b/g, '^{$1}')
    .replace(/√\s*([A-Za-z0-9]+)/gu, String.raw`\sqrt{$1}`)
    .replace(/∛\s*([A-Za-z0-9]+)/gu, String.raw`\sqrt[3]{$1}`)
    .replace(/½/gu, String.raw`\frac{1}{2}`)
    .replace(/⅓/gu, String.raw`\frac{1}{3}`)
    .replace(/⅛/gu, String.raw`\frac{1}{8}`)
    .replace(/⅜/gu, String.raw`\frac{3}{8}`)
    .replace(/\+\/-/g, String.raw`\pm `)
    .replace(/->/g, String.raw`\to `)
    .replace(/<=/g, String.raw`\le `)
    .replace(/>=/g, String.raw`\ge `)
    .replace(/!=/g, String.raw`\ne `)
    .replace(/−/gu, '-')
    .replace(/([A-Za-z}\]])\*(?=\s|=|$)/gu, '$1^{*}')
    .replace(/×|\*/gu, String.raw`\times `)
    .replace(/·/gu, String.raw`\cdot `)
    .replace(/≤/gu, String.raw`\le `)
    .replace(/≥/gu, String.raw`\ge `)
    .replace(/≠/gu, String.raw`\ne `)
    .replace(/≈/gu, String.raw`\approx `)
    .replace(/∈/gu, String.raw`\in `)
    .replace(/→/gu, String.raw`\to `)
    .replace(/⇒/gu, String.raw`\Rightarrow `)
    .replace(/∥/gu, String.raw`\parallel `)
    .replace(/∞/gu, String.raw`\infty `)
    .replace(/ℝ/gu, String.raw`\mathbb{R}`)
    .replace(/ℤ/gu, String.raw`\mathbb{Z}`)
    .replace(/±/gu, String.raw`\pm `)
    .replace(/°/gu, String.raw`^{\circ}`)
    .replace(/[′’]/gu, "'")
    .replace(/″/gu, "''")
    .replace(/µ/gu, String.raw`\mu `)
    .replace(/Σ/gu, String.raw`\sum `)
    .replace(/∫/gu, String.raw`\int `)
    .replace(/\$/gu, String.raw`\$`)
    .replace(/\u0302([A-Za-z])/gu, String.raw`\hat{$1}`)
    .replace(/[_^]\s*$/u, '');

  for (const [character, tex] of Object.entries(unicodeGreek)) value = value.replaceAll(character, tex);
  for (const [name, tex] of Object.entries(greekNames)) value = value.replace(new RegExp(`(?<!\\\\)\\b${name}\\b`, 'g'), tex);
  return value.replace(/\s+/g, ' ').trim();
}

function expandFromAnchor(tokens: Token[], anchorIndex: number): Range {
  let startIndex = anchorIndex;
  let depth = 0;
  let lastBalancedStart = anchorIndex;

  for (let index = anchorIndex - 1; index >= 0; index -= 1) {
    const token = tokens[index]!;
    if (isOrdinaryWord(token.value)) {
      startIndex = depth > 0 ? lastBalancedStart : startIndex;
      break;
    }
    if (closing.has(token.value)) depth += 1;
    if (opening.has(token.value)) {
      if (depth > 0) depth -= 1;
    } else if (depth === 0 && punctuationBoundary.has(token.value)) {
      break;
    }
    startIndex = index;
    if (depth === 0) lastBalancedStart = index;
  }

  let endIndex = anchorIndex;
  depth = 0;
  let lastBalancedEnd = anchorIndex;
  for (let index = anchorIndex + 1; index < tokens.length; index += 1) {
    const token = tokens[index]!;
    if (isOrdinaryWord(token.value)) {
      endIndex = depth > 0 ? lastBalancedEnd : endIndex;
      break;
    }
    if (opening.has(token.value)) depth += 1;
    if (closing.has(token.value)) {
      if (depth > 0) depth -= 1;
    } else if (depth === 0 && punctuationBoundary.has(token.value)) {
      break;
    }
    endIndex = index;
    if (depth === 0) lastBalancedEnd = index;
  }

  return { start: tokens[startIndex]!.start, end: tokens[endIndex]!.end };
}

function isFunctionStart(tokens: Token[], index: number): boolean {
  const token = tokens[index];
  const next = tokens[index + 1];
  if (!token || !next || next.value !== '(' || token.end !== next.start) return false;
  const endIndex = findClosingToken(tokens, index + 1);
  if (endIndex !== -1 && tokens.slice(index + 2, endIndex).some((item) => isOrdinaryWord(item.value))) return false;
  return namedFunctions.has(token.value) || /^[A-Za-z]'*$/.test(token.value);
}

function findClosingToken(tokens: Token[], openingIndex: number): number {
  let depth = 0;
  for (let index = openingIndex; index < tokens.length; index += 1) {
    if (tokens[index]!.value === '(') depth += 1;
    if (tokens[index]!.value === ')') {
      depth -= 1;
      if (depth === 0) return index;
    }
  }
  return -1;
}

function isOrdinaryWord(value: string): boolean {
  // Кириллица в формуле не встречается никогда, а разбор её не видел:
  // токенайзер режет русские слова на буквы, каждая буква проходила как
  // символ формулы, и «и совпадают они только когда» между двумя P(...)
  // уезжало внутрь KaTeX, где пробелы между словами пропадают.
  if (/[\u0400-\u04FF]/u.test(value)) return true;
  if (!/^[A-Za-z][A-Za-z0-9_']*$/.test(value)) return false;
  if (/^[A-Za-z]'*$/.test(value) || /^[A-Za-z]\d+$/.test(value)) return false;
  if (/^(?:arcsin|arccos|arctan|sin|cos|tan|cosec|csc|sec|cot|ln|log|exp)(?:\d*[a-z]|\d+)$/.test(value)) return false;
  if (/^[a-z]{2,3}$/.test(value) && !proseStopWords.has(value)) return false;
  return !mathWords.has(value) && !mathWords.has(value.toLowerCase());
}

function mergeRanges(ranges: Range[]): Range[] {
  const sorted = [...ranges].sort((a, b) => a.start - b.start || a.end - b.end);
  const merged: Range[] = [];
  for (const range of sorted) {
    const previous = merged.at(-1);
    if (previous && range.start <= previous.end) previous.end = Math.max(previous.end, range.end);
    else merged.push({ ...range });
  }
  return merged;
}

function isUsefulFormula(value: string): boolean {
  const trimmed = value.trim();
  if (trimmed.length < 2) return false;
  return /[=<>≤≥≠≈∈→⇒∥^√×·/±⁰¹²³⁴⁵⁶⁷⁸⁹]|\b(?:sin|cos|tan|ln|log|lim|arg|cis|sqrt)\b|^[A-Za-z]'*\s*\(/u.test(trimmed);
}

function convertGroups(source: string): string {
  let output = '';
  for (let index = 0; index < source.length;) {
    const rest = source.slice(index);
    const sqrtMatch = /^(?:sqrt\s*|√)\(/i.exec(rest);
    const cubeRootMatch = /^∛\(/u.exec(rest);
    const marker = sqrtMatch?.[0] ?? cubeRootMatch?.[0] ?? (rest.startsWith('^(') || rest.startsWith('_(') ? rest.slice(0, 2) : null);
    if (!marker) {
      output += source[index];
      index += 1;
      continue;
    }

    const openIndex = index + marker.lastIndexOf('(');
    const closeIndex = findMatchingParen(source, openIndex);
    if (closeIndex === -1) {
      output += source[index];
      index += 1;
      continue;
    }

    const inner = convertGroups(source.slice(openIndex + 1, closeIndex));
    output += sqrtMatch ? `\\sqrt{${inner}}` : cubeRootMatch ? `\\sqrt[3]{${inner}}` : `${marker[0]}{${inner}}`;
    index = closeIndex + 1;
  }
  return output;
}

function findMatchingParen(value: string, openIndex: number): number {
  let depth = 0;
  for (let index = openIndex; index < value.length; index += 1) {
    if (value[index] === '(') depth += 1;
    if (value[index] === ')') {
      depth -= 1;
      if (depth === 0) return index;
    }
  }
  return -1;
}

function replaceGreek(value: string): string {
  return Object.entries(greekNames).reduce(
    (result, [name, tex]) => result.replace(new RegExp(name, 'gi'), tex),
    value,
  );
}
