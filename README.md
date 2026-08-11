# IB Mathematics AA HL Past Papers

Private study archive of IB Mathematics: Analysis and Approaches Higher Level examination papers and markschemes.

## Coverage

- 2021: May and November
- 2022: May and November
- 2023: May and November
- 2024: May and November
- 2025: May and November
- 2026: May, partial

The archive contains 110 PDF files. Session-level README files describe the available timezones, papers, markschemes, and examination dates.

## Structure

Files are organized under `AA_HL` by year, examination session, timezone or zone, and paper number.

## Classification pilot

The first manual topic-and-method classification covers the complete November 2024 Common session:

- [Pilot review](classification/pilots/2024-november/README.md)
- [Question-level dataset](classification/pilots/2024-november/questions.tsv)
- [Topic taxonomy](classification/taxonomy/topics.yaml)
- [Method-family taxonomy](classification/taxonomy/method-families.yaml)

## Question Atlas

The pilot can be explored in a React, TypeScript, Tailwind CSS, and Vite research interface:

```bash
npm --prefix classification/web install
npm --prefix classification/web run dev
```

Open `http://127.0.0.1:5173/`. The interface supports full-text search, topic and method-family filters, Paper and calculator filters, keyboard selection, KaTeX-rendered mathematical notation, ordered solution paths, accepted alternatives, and direct links to source papers and markschemes. The Vite development server also serves the linked archive PDFs without copying them into the web build.

The development and production build commands regenerate browser data from `questions.tsv` automatically. It can also be rebuilt directly:

```bash
npm --prefix classification/web run data:build
```

Create a production build with:

```bash
npm --prefix classification/web run build
```
