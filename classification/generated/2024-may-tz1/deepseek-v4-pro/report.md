# May 2024 TZ1 classification report

Status: **partially reviewed** — 25 of 95 blocks have been manually compared with the question papers and markschemes.

## Result

| Paper | Questions | Blocks | Marks |
| --- | ---: | ---: | ---: |
| Paper 1 | 12 | 37 | 110 |
| Paper 2 | 12 | 33 | 110 |
| Paper 3 | 2 | 25 | 55 |
| **Total** | **26** | **95** | **275** |

All three final JSON documents pass `classification/pipeline/validate-generated.mjs`: IDs are unique, mark totals match the papers, and every primary topic, method family, confidence value, and review flag belongs to the controlled taxonomy. The validator also checks that the calibration ledger has unique, existing block IDs and a correction for every `corrected` verdict.

## Calibration review

The complete flagged set (15 blocks) and a deterministic cross-paper sample of 10 unflagged blocks were visually reviewed against both source PDFs. The sample seed is `calibration-v1`; its IDs and decisions are recorded in `classification/reviews/2024-may-tz1/calibration-v1.json`.

| Cohort | Reviewed | Accepted | Corrected |
| --- | ---: | ---: | ---: |
| Flagged | 15 | 10 | 5 |
| Unflagged sample | 10 | 9 | 1 |
| **Total** | **25** | **19** | **6** |

The corrections cover two function-analysis method labels, one differential-equation sign and topic, two 3D-vector topic/method labels, and one lost square root in a task summary. The raw DeepSeek fragments remain unchanged; the deterministic merger applies the audited correction layer to the final papers.

The reviewed 25 blocks now have `manual_verified` status in the web interface. The remaining 70 blocks retain `ai_draft` status.

## Extraction and generation

Question papers and markschemes were extracted page by page. DeepSeek classified short questions directly and long questions in mark-balanced groups, which were merged only after their marks matched the expected group and paper totals.

Five formula- or diagram-heavy locations used visual, manually verified transcriptions before DeepSeek classification:

- Paper 1 Q6, Q8, Q9 and Q10(f);
- Paper 3 Q2(h).

59 blocks use generic page-level evidence created by the deterministic merger; 36 retain more specific evidence generated from the markscheme. Generic evidence is sufficient for provenance, but those blocks are good candidates for the second-pass evidence audit.

## Bulk-run decision

The structure is good enough for a bulk run, but not for unattended publication. The flagged set had a 5/15 correction rate, and the unflagged control sample still found 1/10 needing correction. DeepSeek also assigned high segmentation confidence to every block, so model confidence cannot be used as the only review gate.

For the remaining sessions, keep the same question/group pipeline and require:

1. deterministic mark-total and schema validation for every paper;
2. manual review of every flagged block;
3. a seeded 10% sample of unflagged blocks, with a minimum of two per paper;
4. expansion to full-paper review whenever the sample contains a factual transcription error;
5. publication as AI draft until that session's review gate passes.
