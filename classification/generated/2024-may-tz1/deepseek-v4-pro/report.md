# May 2024 TZ1 classification report

Status: **AI draft**, not manually verified.

## Result

| Paper | Questions | Blocks | Marks |
| --- | ---: | ---: | ---: |
| Paper 1 | 12 | 37 | 110 |
| Paper 2 | 12 | 33 | 110 |
| Paper 3 | 2 | 25 | 55 |
| **Total** | **26** | **95** | **275** |

All three final JSON documents pass `classification/pipeline/validate-generated.mjs`: IDs are unique, mark totals match the papers, and every primary topic, method family, confidence value, and review flag belongs to the controlled taxonomy.

## Review queue

15 blocks carry review flags:

- 5 `shared_marks` blocks;
- 4 `diagram_dependent` blocks;
- 3 blocks involving uncertain formula extraction;
- 4 blocks with an explicit alternative route (two overlap formula-extraction flags);
- 1 `topic_uncertain` block.

The remaining 80 blocks have no explicit review flag, but still retain `ai_draft` status until a human accepts them.

## Extraction and generation

Question papers and markschemes were extracted page by page. DeepSeek classified short questions directly and long questions in mark-balanced groups, which were merged only after their marks matched the expected group and paper totals.

Five formula- or diagram-heavy locations used visual, manually verified transcriptions before DeepSeek classification:

- Paper 1 Q6, Q8, Q9 and Q10(f);
- Paper 3 Q2(h).

59 blocks use generic page-level evidence created by the deterministic merger; 36 retain more specific evidence generated from the markscheme. Generic evidence is sufficient for provenance, but those blocks are good candidates for the second-pass evidence audit.

## Recommended calibration before the bulk run

1. Manually review all 15 flagged blocks.
2. Randomly sample 10 unflagged blocks across the three papers.
3. Confirm whether combined shared-mark blocks should remain combined or be split when individual A/M marks are explicit in the markscheme.
4. Tune confidence: DeepSeek marked segmentation high for all 95 blocks, which is too optimistic for an unattended production run.
5. After calibration, run the remaining paired papers with the same question/group pipeline and send only flagged or sampled items to human review.
