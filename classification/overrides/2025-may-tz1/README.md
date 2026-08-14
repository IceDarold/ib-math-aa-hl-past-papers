# May 2025 TZ1 review overrides

These corrections merge the stronger parts of the local classification draft
into the complete version from `main`. Run them before rebuilding the merged
paper files:

```sh
node classification/overrides/2025-may-tz1/apply.mjs
node classification/pipeline/merge-bulk.mjs 2025-may-tz1
```

The review compared the question papers, markschemes, both generated drafts,
and rendered PDF pages. The applied decisions are intentionally narrow:

- combine P1 Q11(c)(i)-(ii) and P2 Q6(a)(i)-(ii), because each pair has one
  shared printed mark allocation;
- keep the combined P1 Q7(b)(i)-(ii) block already present in `main`;
- correct the P1 Q5 mean to `p((9/4)^a - 1)`, with `p = 8/5`, `a = 10`;
- use printed source-page numbers instead of PDF indices where the draft was
  offset by one page;
- apply only the topic and method changes supported by the task and markscheme.

The local P1 Q11(b) text was deliberately not copied: it gave the wrong sign
for the plane constant. The complete `main` result, `x - y + z = 15`, is kept.
