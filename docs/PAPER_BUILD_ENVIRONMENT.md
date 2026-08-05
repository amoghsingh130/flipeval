# Paper build environment

Recorded 2026-08-05, when this manuscript was compiled for the first time.

## Toolchain

| component | version |
|---|---|
| distribution | TeX Live 2026, `scheme-small`, tlmgr revision 79639 (2026-07-10) |
| engine | pdfTeX 3.141592653-2.6-1.40.29 |
| kpathsea | 6.4.2 |
| BibTeX | 0.99e |
| latexmk | present at `$TL/bin/x86_64-linux/latexmk`, **not used** |
| pgf/TikZ | 3.1.12 |

Installed at `~/scratch/texlive` from `mirror.ctan.org`. **This is not part of the
pinned computational environment** and must never be confused with it: the
Apptainer image at `~/scratch/flipeval/flipeval.sif` remains the only thing that
runs analysis code. TeX Live is a document build tool only.

Scratch is subject to the 60-day purge, so this install is disposable and may
need recreating. The profile used is reproducible: `scheme-small`, `option_doc 0`,
`option_src 0`, `instopt_adjustpath 0`.

## Build command

`latexmk` is deliberately not used, so that the pass sequence is explicit and
identical to what `paper/main.tex` documents.

```bash
export PATH=$HOME/scratch/texlive/bin/x86_64-linux:$PATH
cd paper
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Three pdflatex passes are required: one to write `.aux`, bibtex, then two more to
resolve citations and settle float placement and page references.

## Required packages

`article.cls`, `inputenc`, `fontenc`, `amsmath`, `amssymb`, `booktabs`,
**`array`**, `graphicx`, `xcolor`, `hyperref`, `natbib`, `amsthm`, `tikz` with
the `arrows.meta` library.

Two notes on the last two:

- **`array` is a 2026-08-05 addition.** It supplies the
  `>{\centering\arraybackslash}p{}` and `>{\raggedright\arraybackslash}p{}`
  column specifications that the overfull-table fixes depend on. Removing it
  breaks every wide table.
- **`arrows.meta` resolves through a fallback.** `scheme-small` ships no
  `tikzlibraryarrows.meta.code.tex`; `\usetikzlibrary` finds
  `pgflibraryarrows.meta.code.tex` instead. This works and needs no action, but
  a stricter TeX installation might not have the fallback, so if the figure ever
  fails to build on another machine, that is the first thing to check.

## Line-breaking settings, and why they are not typography changes

`main.tex` sets `\emergencystretch` to 3em globally, and to 6em locally around
`\input{sections/appendix_registrations}`. Both were added 2026-08-05 to stop
prose lines containing unbreakable identifiers, such as the 40-character model
revision hash in the frozen registration appendix, from running into the margin.

`\emergencystretch` changes **no** font size, **no** margin and **no** measure.
It permits a final line-breaking pass with looser interword spacing rather than
an overflowing line. It is not a page-count device. The local 6em setting exists
specifically because `appendix_registrations.tex` is frozen verbatim and cannot
be edited to add break points; the setting is applied from outside that file and
changes not one character of it, which
`paper/tools/verify_registrations.py` continues to confirm at 7,103 words.

## Float placement

All 19 `table` floats and the Figure 1 `figure` float use `[!t]`. The `!` is
load-bearing: it tells LaTeX to ignore the `\topfraction` size restrictions.

Without it, tall floats are deferred indefinitely and flushed at the end of the
document. That is not hypothetical. Figure 1 originally landed on **page 87**
having been declared on page 2, and after the table-width fixes made three body
tables taller, `tab:certification`, `tab:atlas-strata` and `tab:audit-taxonomy`
deferred to pages 85 and 86 until `[!t]` was applied. **Any new float in this
paper should be `[!t]` from the start, and float pages must be checked after any
change that alters a float's height.**
