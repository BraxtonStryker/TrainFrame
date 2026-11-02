# TrainFrame: plan (draft 2, 2026-11-02)

A study app in the same family as QuizQrusher, InfoBase, CwikCard and RunDown. You (or an AI) write a plain-text **frame file** for a homework set, a lecture or an exam review; you drop it into TrainFrame; it becomes an interactive walkthrough like the ECEN 305 and ELEN 304 HW3 pages: step-by-step reveals, formula tags that pop up the formula in place, and plots with sliders. The framework is written once. Every new file is only content.

---

## 1. What I took from your existing work

| Source | What TrainFrame keeps |
|---|---|
| **ECEN 305 HW3** | Already data-driven (`BANK` and `PROBLEMS` objects turned into the page by `build()`). Formula bank with topic chips and auto "Used in P1, P3" links; step lists per part with Next step / Show all / Hide; ref tags that open the formula *inline under the step* ("peek") with "Open in formula bank"; sticky left rail with per-problem progress bars; "Done on paper" checkboxes; progress saved; Explain-prompt rubrics; the Q-function calculator; "Before you submit" checklist. |
| **ELEN 304 HW3** | Hand-written HTML, but the interactive parts are the model for visuals: scope-style plots with sliders, view buttons (Part 1 / Part 2), stem plots, a unit circle with live phase vectors, live tables and readouts, a bottom sheet for formulas on phones, filter-by-problem chips. |
| **InfoBase** | The hub idea: class tabs, files dropped into the page and kept in IndexedDB, works offline, "Download for offline" makes one HTML with the files inside. |
| **All four apps** | The look and conventions: Homepage color tokens and dark mode, the 51 px title bar with the app switcher and settings cog, Atkinson Hyperlegible, `calc(Npx * var(--fs))` font sizes, single-file `index.html` in vanilla JS, nothing loaded from other sites, KaTeX bundled from RunDown, service worker + `tools/sw_version.py`, every storage name prefixed with the app's name (one shared origin). |

One change from both walkthroughs: they load MathJax and Google Fonts from CDNs. TrainFrame uses the bundled KaTeX and the inlined font like your other apps, so it works offline.

---

## 2. Why a language and not a CSV

You landed on the right call. A CSV fights this content at every turn: LaTeX is full of commas and quotes, steps are multi-line, and the content nests (problem → part → step → visual), which a flat row can't show without escape rules nobody can read. A line-based language reads top to bottom like the page it makes, diffs cleanly in git, and is forgiving to write by hand.

---

## 3. The frame language

The spec is [docs/LANGUAGE.md](docs/LANGUAGE.md), now v0.2. The worked examples are `examples-private/ecen305-hw3.frame` and `examples-private/elen304-hw3.frame`. In short:

- A file is a list of blocks. Each starts with an `@type` line, then come `key: value` properties, then the body.
- Bodies are text with `$math$`, light Markdown, `{{F2}}` refs (outside math only) and `{= expr}` live values.
- Visual lines are written `keyword main part; option; option`. Semicolons separate the parts, and commas separate list items (v0.2, your call).
- `let` and `check:` give plots and answers one shared, safe math language. A `check:` that fails shows up in the load report.
- The language grows by adding words (new block types, visual types and options), never by changing old ones (§9 of the spec).

---

## 4. Visual types (the plug-in catalog)

Each visual type is written once in the framework as a plug-in: a name, the lines and options it accepts, and a draw function. Block types work the same way, so a new class type (circuits, code, logic) gets new words without touching the old ones. Files only *use* them. Adding, say, Bode plots later means one new plug-in, and every file can use `@bode` from then on.

| Type | Draws | Covers |
|---|---|---|
| `@plot` | Curves, shading between bounds, vertical markers, labeled points, several traces with a legend, sliders, view buttons, live captions | 305's density plots, 304's scope plots |
| `@stem` | Discrete sequences and line spectra (filled or hollow, labels) | 304's \|a_n\| spectra, x[n] |
| `@phasor` | Unit circle / complex plane with vectors from a formula over n | 304 P1's unit circle |
| `@calc` | Number inputs → computed outputs, plus an optional plot | 305's Q-function calculator |
| `@table` | Rows over a range (n = 0 to 7) with computed, live columns | 304's b_n/a_n table, 305's Q mini-table |

Plots are SVG (sharp at any zoom, themed by CSS, easy to label), redrawn on slider input.

---

## 5. The app

### Layout

```
top bar:       [v] TrainFrame Beta  Library | ECEN 304 x | ECEN 305 x | +      Help  Calc  Settings
class header:  HW3 Walkthrough x | Midterm review x            <- this class's open files
               Assignments | Formula sheet | Search | Add files              Edit class
------------------------------------------------------------------------------------
Assignments:   ECEN 305 > Homework     (breadcrumb, then folders, then file cards)

An open file:
+--------------+---------------------------------------+---+
| Formulas     | ECEN 305 > Homework                   | N |  <- NOTES tab on the right edge;
| P1  8  ===   | title, facts, intro, formula bank     | O |     the box slides out
| P2  8  =     | P1 -> parts -> steps, visuals         | T |     (as in QuizQrusher)
| ...          | ...                                   | E |
+--------------+---------------------------------------+---+
 problem rail                        calculator: a pop-out window, draggable, on every screen
```

The top bar and the class header stay on screen, so switching tabs never scrolls the page and every tab can keep its spot. On a phone the rail becomes a sideways strip under them (as in the ECEN 305 page), the notes tab stays on the right edge, and the calculator opens full width.

### Pieces

- **Library** (home): every class as a card, archived classes in a fold below, then Add files. Classes come from the files' `class:` lines, plus **New class**. Files with no class go in **Unsorted**.
- **Tabs** (like RunDown's document tabs): a class opens as a closable tab next to Library, and each class's open files get closable tabs above its sections. A class tab remembers its section and folder; a file tab remembers its scroll spot. Closing a class tab keeps its state for next time.
- **Edit class:** rename (files whose `class:` line has the old name keep landing in the renamed class), archive or unarchive, and delete (with its files and notes).
- **Section tabs** inside a class:
  - **Assignments**: a folder directory. A file lands in the folder its `folder:` line names (`Homework`, `Exams/Midterm 1`). You can make folders and move, rename or delete files in the app. Moves are saved in the app and never change the file.
  - **Formula sheet**: every formula and definition from the class's files, grouped, with links to the problems that use each one. A formula that appears in several files is shown once.
  - **Search**: text, formulas and problems across the class.
  - **Add files**: drop, pick or paste `.frame` files. Shows the load report with **Copy report for AI**. Dropping a file with the same `@frame` id asks before replacing it.
- **Problem rail** (from the ECEN 305 page): Formulas, then each problem with its points and a progress bar. It's sticky, and it highlights where you are.
- **Notes box** (from QuizQrusher): one per assignment, saved automatically. **Insert heading** adds the problem and part you're on. **Export** saves the notes as a text or Markdown file.
- **Calculator** (TI-36X Pro style), a pop-out window you can drag and that every page has:
  - **Basics:** trig and inverse trig, hyperbolic functions, logs, powers, roots, nCr, nPr, !, memory variables, `ans`, scrollable history, deg/rad/grad, and sci/eng/fixed display.
  - **Fractions and complex:** n/d and mixed numbers, an exact ⇄ decimal toggle, a+bi and polar (r∠θ), conj, arg.
  - **Solvers:** polynomials (degree 2 and 3, complex roots included), 2×2 and 3×3 linear systems, and numeric solve for f(x) = 0.
  - **Stats and calculus:** 1- and 2-variable stats; linear, quadratic, exponential, ln and power regressions; d/dx and ∫ at a point or over an interval; a function table.
  - **Matrices, vectors and base-n:** matrix add, multiply, determinant, inverse, transpose and RREF; vector dot, cross and norm; hex, bin, oct and dec conversion with AND, OR, XOR and NOT.
  - It runs on the same expression engine as the frame files, so the complex and integral code is shared. Typing from the keyboard works too.
  - Later: unit conversions and physical constants, which the TI-36X Pro also has.
- **Walkthrough view:** the rendered file, with progress saved per file.
- **Edit view** (later phase): the source on the left and a live preview on the right, with errors marked, for writing by hand.
- **Export:** download the `.frame` file, or a standalone HTML (the app plus the file) that opens from disk. **Download for offline** saves a whole class, as in InfoBase.
- **Help:** the language reference and a **Copy AI prompt** button.
- **Files are always drop-in.** Nothing is hosted with the site except the invented demo.

---

## 6. Repo layout

```
TrainFrame/
  index.html              the whole app: parser, checker, renderer, visuals, hub, notes, calculator
  sw.js  manifest.webmanifest  icons/
  vendor/katex.min.js     the same KaTeX build RunDown and InfoBase use
  docs/LANGUAGE.md        full language reference (also shown in Help)
  prompts/generator.md    the prompt you hand an AI along with your assignment
  examples/demo.frame     a public demo with invented problems, shipped in the app
  examples-private/       gitignored: your real HW walkthroughs converted (the two original HTML pages are gitignored too)
  tools/harness.py        headless-Chrome tests (parser, rendering, steppers, sliders)
  tools/sw_version.py     copied from RunDown
  README.md  CLAUDE.md  .gitignore
```

Published as `BraxtonStryker/TrainFrame` at `https://braxtonstryker.github.io/TrainFrame/`, with storage names starting `trainFrame`. Teal is TrainFrame's color: the default accent (`#0F766E` / `#2DD4BF`, the Teal preset), the app switcher entry and the icon.

---

## 7. Steps I'll take

Each step ends with something you can open and react to. ★ marks the places your review matters most.

1. ✓ **Language spec.** v0.1 written and four real problems converted; v0.2 adds semicolons and `folder:`.
2. **Working shell.** `git init`; the shell copied from RunDown (tokens, title bar, app switcher, settings, theme, font, KaTeX, service worker); the layout: class tabs, section tabs, folder directory, Add files, the problem rail, the notes box and the calculator window. Until steps 3 and 4 land, an opened file shows its source.
3. **Parser and checker.** Text becomes a tree of blocks with line numbers. Unknown refs, missing answers, bad expressions and failed `check:` lines are reported. The safe expression parser lands here, with complex numbers and the adaptive integral.
4. **Renderer.** The title block, the rail with progress, the formula bank (group and problem chips, "Used in"), problems → parts → steppers, ref peeks (inline on desktop, a bottom sheet on phones), answers, explain rubrics, notes and callouts, and the checklist. Progress is saved per file.
5. **Visuals.** `@plot` first, since it covers most of both walkthroughs. Then `@stem`, `@table` and `@calc`, then `@phasor`.
6. **Hub.** The Formula sheet and Search tabs, the load report with Copy for AI, export as `.frame` and as standalone HTML, and Download for offline.
7. **Calculator.** The TI-36X Pro modes in §5, in this order: basics, fractions and complex, solvers, stats and calculus, then matrices, vectors and base-n.
8. **★ AI pipeline.** `prompts/generator.md` and the in-app Copy prompt. Then the real test: hand an AI the original ECEN 305 assignment, load what it writes, and tighten the spec and prompt wherever it trips.
9. **Full conversions as regression tests.** Both HW3 walkthroughs, converted completely and run through the harness.
10. **Edit view** with live preview.
11. **★ Ship.** Create the GitHub repo and turn on Pages; add a TrainFrame card and footer link to the Homepage; add TrainFrame to the app switcher in QuizQrusher, InfoBase, CwikCard and RunDown. That touches five other repos, so I'll ask before each push.
12. **Later:** cross-file refs, more visual types, unit conversions and constants in the calculator.

---

## 8. How you can help

- **Try the shell** (step 2) on your laptop and phone, and tell me what the layout gets wrong before the renderer fills it in.
- **Send the original assignment PDFs** for ECEN 305 HW3 and ELEN 304 HW3. Step 8 needs them to compare what an AI writes from scratch against the walkthroughs you already trust.
- **Tell me which visuals your classes need.** Bode plots? Pole-zero plots? Convolution? Circuits? RC transients? Probability densities? That sets the plug-in order after the first five.
- **Name the other kinds of files you'd want** (lecture notes, exam review, lab prep, formula sheet) so the notes blocks get designed alongside the homework ones.
- **Write one small file by hand** after step 6 and tell me where it fought you.
- **Check it on your phone** before it ships, as with QuizQrusher's Phase 10.

---

## 9. Decisions

Settled on 2026-11-02:

1. **Name and extension:** TrainFrame, `.frame` files only.
2. **Color:** teal.
3. **Real walkthroughs stay private.** They live in the gitignored `examples-private/`, and an invented demo ships instead. (My default, since you didn't say otherwise. Tell me if you want them public.)
4. **Files are always drop-in.** No hosted library.
5. **Syntax:** semicolons between the parts of a visual line, commas within lists, and IDs in braces on header lines (`@formula {F1} Title`).
6. **Class sections:** Assignments (folders), Formula sheet, Search, Add files. Open classes are tabs next to Library, with the class's open files as tabs above the sections; every tab remembers its place. Classes can be renamed, archived and deleted.
7. **Folders** come from the file's `folder:` line, and you can move files in the app.
8. **Notes:** one box per assignment.
9. **Calculator:** all four TI-36X Pro mode groups.
