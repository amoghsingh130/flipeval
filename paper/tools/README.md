# Paper tooling

Run from the repository root. Python 3.9 on the login node is enough: these use
only the standard library, deliberately, so they run where the pinned image is
not available.

These live under `paper/` rather than `scripts/` on purpose. `scripts/` is a
fingerprinted tree (`scripts/freeze_prepace.py`), so a change there triggers the
in-image pytest gate and a freeze refresh; these touch no cluster-side code and
are not part of the analysis pipeline. Earlier table generators were left in
session scratchpads and lost, which is why these are committed.

| tool | what it does |
|---|---|
| `gen_registrations.py` | Regenerates `sections/appendix_registrations.tex` from the four FROZEN registration documents. Read-only against them. |
| `verify_registrations.py` | Proves that appendix reproduces the frozen text word-for-word, by diffing word streams. Exits non-zero on any mismatch. |
| `check_paper.py` | Stand-in for a LaTeX build: recursive `\input` expansion, then labels, refs, cite keys, environment balance, and the anonymous-build leak check. |
| `gen_reading_copy.py` | Regenerates `READING_COPY.md`. Run it *after* committing content, so the recorded commit is the state it reflects. |

Order after editing paper content:

```bash
python3 paper/tools/gen_registrations.py     # only if a frozen doc gained an amendment
python3 paper/tools/verify_registrations.py
python3 paper/tools/check_paper.py
git commit ...
python3 paper/tools/gen_reading_copy.py
git commit paper/READING_COPY.md ...
```

## The anonymous build

`paper/main.tex` carries `\newif\ifanon`. `\anonfalse` is the arXiv preprint;
`\anontrue` is the TMLR submission. Every de-anonymising item is routed through
a macro defined next to the switch. `check_paper.py` fails if an identifier
appears in rendered text anywhere outside `main.tex`, which is the only thing
that stops a raw URL pasted into a section from silently breaking the blind
build.

## Validation these tools were given

- `verify_registrations.py` was negative-controlled: it detects a changed
  number, a changed word ending, and a deleted `\item`.
- `check_paper.py`'s leak check was negative-controlled with a planted name.
- `gen_reading_copy.py` was validated by regenerating `READING_COPY.md` at
  `b4b2d99` in a detached worktree and diffing against the committed file:
  **zero content lines differ**. The only differences are whitespace, and they
  are intentional — the previous generator separated index-table rows with
  blank lines, which terminates the markdown table after its header.
