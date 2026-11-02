# The frame language (v0.2 draft)

A **frame file** is a plain-text `.frame` file that TrainFrame turns into an interactive walkthrough: problems revealed one step at a time, formula tags that open the formula in place, and plots with sliders. You write content only. The layout, the interactivity and the look come from the app.

This page is the whole language. The worked examples are `examples-private/ecen305-hw3.frame` and `examples-private/elen304-hw3.frame`.

---

## Cheat sheet

A frame file is a list of **blocks**. Each block starts with an `@` line. The `key: value` lines right under it are its **properties**, and everything after them is its **body**.

### 1. The file header

```
@frame {my-hw3}
title: Homework 3
class: ECEN 305
folder: Homework

Intro text goes here.
```

- `@frame` always comes first, followed by the file's id in braces (letters, digits, `-` or `_`).
- `class` picks the class tab the file goes in, and `folder` picks the folder inside it.
- The blank line ends the properties. "Intro text goes here." is the body.

### 2. A formula

```
@formula {F1} Valid PDF
group: PDF & CDF
$$ \int f_X(x)\,dx = 1 $$
```

- After `@formula` comes its ID in braces (`{F1}`), then its title. The braces keep the ID apart from the title, and they match the `{{F1}}` that refers to it.
- `$...$` is inline math and `$$...$$` is display math, both written in LaTeX.

### 3. A problem

```
@problem {P1} Find the constant
points: 8
let f(x) = if(0 <= x <= 2, 3/8 * x^2, 0)

@given
$f_X(x) = c\,x^2$ on $[0, 2]$.

@part {a}
Find $c$.

@step Normalize {{F1}}
Set the total area to 1, as in {{F1}}.
$$ \int_0^2 c\,x^2\,dx = 1 $$

@answer
$$ c = \tfrac{3}{8} $$
check: integral(x = 0 to 2, f(x)) = 1
```

- `let` defines a function that the problem's plots and checks can use.
- `{{F1}}` on a `@step` line tags the step "Uses F1". In the text it becomes a tag you click to open the formula.
- `check:` makes the app work out both sides when the file loads and report any mismatch.

### 4. A plot with a slider

```
@plot Density
x: -0.4 to 2.4; ticks 0, 1, 2
y: 0 to 1.5; ticks 0, 0.5, 1; label "$f_X(x)$"
slider b: 0 to 2; step 0.05; start 1; label "Upper limit $b$"
curve f; color 1
shade f from 0 to b
caption: Area $= {= integral(x = 0 to b, f(x)) : 3}$
```

- Every visual line is written **keyword main part; option; option**. Semicolons separate the parts. Commas only separate the items of a list, like the ticks. A `;` at the end of the line is fine but not needed.
- `{= ... }` is a live value that updates as the slider moves. `: 3` means 3 decimals.

### 5. Comments

A line starting with `//` is a comment.

### Blocks at a glance

| Blocks | Use them for |
|---|---|
| `@frame` | The file header: first, and only once |
| `@formula`, `@definition` | Cards in the formula bank |
| `@problem`, then `@given`, `@plan`, `@part`, `@step`, `@answer`, `@explain` | Worked problems |
| `@plot`, `@stem`, `@phasor`, `@table`, `@calc` | Interactive visuals |
| `@section`, `@checklist`, `@note`, `@tip`, `@warning` | Page structure and callouts |

---

## 1. The rules

1. **A block starts with `@type`** at the very start of a line. What follows on that line is the block's ID in braces and/or its title: `@formula {F1} Valid PDF` (see the table in §3). An ID written without braces (`@formula F1 Valid PDF`) also works, as the first word.
2. **Properties** are `key: value` lines directly under the header. Keys are lowercase and only the ones that block knows count. The first line that isn't one of them, or a blank line, starts the body.
3. **The body** runs until the next `@` line. It is text (§2), except in visuals, whose lines are instructions (§6).
4. **`let`** and **`check:`** lines work anywhere in the blocks that allow them.
5. **`//`** at the start of a line makes it a comment. Indentation never matters; indent however reads best to you.
6. **No HTML and no escaping:** write `<`, `>` and `&` as they are. To start a text line with `@` or `//`, put a backslash before it: `\@`. A literal dollar sign is `\$`.
7. **The first block is `@frame`.** There is one per file.
8. **IDs are unique within the file** across formulas, definitions and problems, and they are case-sensitive (`F1` is not `f1`).

## 2. Text

| Write | You get |
|---|---|
| A blank line | A new paragraph. Lines without a blank between them join into one paragraph. |
| `$x^2$` | Inline math (LaTeX, rendered by KaTeX) |
| `$$ ... $$` | Display math. It can span several lines, which is how `aligned` and `cases` work. |
| `**bold**`, `*italic*`, `` `code` ``, `==highlight==` | As in Markdown |
| `- item` or `1. item` | Bulleted or numbered lists |
| `\| a \| b \|` rows | A table (a header row, a `\|---\|---\|` row, then rows), as in GitHub Markdown |
| `{{F2}}` | A formula or definition tag. Click it to open the formula right there. |
| `{{P3}}`, `{{P3.b}}` | A link to a problem, or to one part of it |
| `{= expr}`, `{= expr : 4}` | A live value: the expression's result to 3 decimals, or to as many as you say. Updates when sliders move. Works inside math too. |

**Refs are read only outside math.** LaTeX uses `{{` and `}}` all the time (`\frac{{a}}{b}`), so `{{F2}}` inside `$...$` is left alone as LaTeX.

## 3. Blocks

### File and reference blocks

| Block | Header line | Properties | Body |
|---|---|---|---|
| `@frame` | `@frame {file-id}` | `title`, `class` (the class tab it goes in; files without one go in an "Unsorted" tab), `folder` (the folder inside the class, like `Homework`; use `/` for a subfolder, like `Exams/Midterm 1`; files without one sit at the top of the class), `subtitle` (the small line above the title), `fact` (repeatable: `fact: Due = Oct 6`), `kind` (`homework`, `notes`, `review` or `formulas`; default `homework`), `steps` (`per part`, the default, or `per problem`) | Intro paragraph under the title |
| `@formula` | `@formula {ID} title` | `group` (formula bank filter chip), `style` | Math plus a short note |
| `@definition` | `@definition {ID} term` | `group`, `style` | The definition |
| `@section` | `@section title` | none | Text. Starts a new section in the side rail (mainly for notes files). |
| `@checklist` | `@checklist title` | none | A list. Each item gets a checkbox that is remembered. |

In homework files, formulas and definitions are collected into the **formula bank** at the top, wherever you write them. Each card shows "Used in P1, P3", worked out from the refs. In notes files they also appear where you write them.

`class` and `folder` only say where a new file lands. You can move a file to another folder or class in the app afterward. That move is saved in the app, and the file itself doesn't change.

### Problem blocks

| Block | Header line | Properties | Body |
|---|---|---|---|
| `@problem` | `@problem {ID} title` | `points` (`8` shows as "8 pts"; anything else is shown as written, like `+3 bonus`), `short` (rail label), `label` (badge text instead of the ID, like `Bonus`), `steps` (overrides the file's) | none, but `let` lines go here |
| `@given` | `@given` or `@given heading` | none | The problem statement (heading defaults to "Given") |
| `@plan` | `@plan` or `@plan heading` | none | The approach (heading defaults to "Plan"; e.g. `@plan Strategy`) |
| `@part` | `@part {ID}` or `@part {ID} title` | `points` | The part's question. A one-letter ID shows as "(a)"; others as "Part 1". |
| `@step` | `@step title` | `style` | The step. Refs on the header line become its "Uses" tags. |
| `@answer` | `@answer` | none | The final answer, plus any `check:` lines |
| `@explain` | `@explain prompt` | none | A list of what a full written explanation needs, hidden until asked for |

**Stepping.** With `steps: per part`, each part gets its own Next step / Show all / Hide controls (like ECEN 305). With `steps: per problem`, the whole problem is one sequence, and each `@part` line puts a "Part 1" label on the step after it (like ELEN 304). Steps written before the first `@part` are a lead-in that every part builds on.

### Callouts

`@note`, `@tip` and `@warning`, each with an optional title on the header line and text as the body.

### Where things go (nesting)

- `@formula`, `@definition`, `@section`, `@problem`, `@checklist` are top level. Starting one ends whatever problem was open.
- Inside a problem: `@given`, `@plan`, `@part`, `@step`, `@answer`, `@explain`.
- **A visual or callout belongs to the block right above it:**

| Written right after | It shows up |
|---|---|
| `@problem`, `@given`, `@plan` | At the top of the problem, always visible |
| `@part` | At the top of the part, always visible |
| `@step` | Inside that step, revealed with it |
| `@answer` | Inside the answer, revealed with it |
| anything, with `place: after steps` | Below the problem's steps, always visible (ELEN 304's "Check it" plots) |
| `@section`, `@frame`, or top level | In the page, right there |

## 4. Styling

There's no CSS in a frame file. A short list of words covers the looks, and every one works in light and dark mode:

| Where | Words |
|---|---|
| `@formula`, `@definition` | `style: wide` (spans the full width of the bank), `style: highlight` |
| `@step` | `style: key` (marks an important step), `style: aside` (lighter, for a side remark) |
| Visual lines | `color 1` to `color 4`, `muted`, `dashed`, `dotted`, `width 3` |

New looks get added to the app, so every file can use them.

## 5. Expressions, `let` and `check:`

Plots, live values and checks share one small math language. TrainFrame parses it itself, so a frame file can never run code.

| | |
|---|---|
| Numbers and constants | `3`, `0.5`, `1e-3`, `pi`, `e`, `j` (the imaginary unit), `deg` (π/180), `inf` |
| Arithmetic | `+ - * / ^` and `%` (remainder, always ≥ 0). A plain number may touch what follows it: `2x`, `3pi`, `4(x+1)`. Anything else needs `*`. |
| Comparisons and logic | `< <= > >= == !=`, chained like `0 <= x <= 2`, and `and`, `or`, `not` |
| Choices | `if(cond, a, b)`, or a chain `if(c1, a, c2, b, otherwise)` |
| Functions | `sin cos tan asin acos atan atan2 sinh cosh tanh exp ln log10 log2 sqrt abs sign floor ceil round min max clamp(x, lo, hi) mod(a, b)` |
| Probability | `fact(n)`, `choose(n, k)`, `gauss(x, mu, sigma)`, `Phi(z)`, `Q(z)`, `Qinv(p)`, `erf`, `erfc` |
| Complex | `j`, `re`, `im`, `abs`, `arg`, `conj`, `cis(theta)`; `exp` and arithmetic work on complex numbers |
| Sums and integrals | `sum(n = 1 to N, expr)`, `sum(n = 1 to N step 2, expr)`, `product(k = 1 to n, expr)`, `integral(x = 0 to 2, expr)` (computed numerically and refined around jumps, so square waves and piecewise densities come out right; complex integrands work) |

**`let`** defines a function or a constant: `let f(x) = 3/8 * x^2` or `let w0 = pi/2`. Put lets on the `@frame` for the whole file, on a `@problem` for that problem (its visuals and checks see them), or inside a visual for that visual only. Lets can use each other, but not themselves.

**`check:`** goes in a `@step` or an `@answer`: `check: <expression> = <expected>`. TrainFrame computes both sides when the file loads. A pass puts a ✓ on the step; a failure goes in the load report with its line number. The tolerance is half of the last decimal you wrote, so `= 0.578` passes for 0.578125. An expected value written as an expression, like `= 1/8`, must match to about 6 significant digits. Complex values compare too: `check: exp(-j*pi/2) = -j`.

The best checks compute something independently, such as an `integral(...)` of the density instead of the closed form you just derived. That catches algebra mistakes the steps would hide.

## 6. Visuals

A visual is a figure with one or more **panels**, starting with the type in its header: `@plot`, `@stem`, `@phasor`, `@table` or `@calc`, followed by an optional title. Its lines are instructions, one per line.

**The shape of a line:** a keyword and its main part, then any options, with a semicolon before each one:

```
slider b: 0 to 2; step 0.05; start 1; label "Upper limit $b$"
```

| Part | In this line |
|---|---|
| Keyword | `slider` |
| Main part | `b: 0 to 2` |
| Options | `step 0.05`, `start 1` and `label "Upper limit $b$"` |

- **`;` separates the parts** and **`,` separates the items of a list** inside one part: `ticks 0, 0.5, 1`, `set dc = 1, N = 3`, `for t in -4, -2, 0`.
- A `;` at the end of the line is allowed. Options can come in any order.
- A `;` inside quotes or inside an expression's parentheses doesn't count.
- Text lines (`caption:`, `readout:`, `place:`, `layout:`) are plain text, so a semicolon in them is just a semicolon.

### Lines any visual can use

| Line | What it does |
|---|---|
| `slider b: 0 to 2; step 0.05; start 1; label "Upper limit $b$"` | A slider that sets variable `b` |
| `toggle parts; label "Show the two parts"` | A checkbox that sets `parts` to 1 or 0 |
| `set dc = 1, N = 3` | Sets variables (starting values, or a view's values). This is one list, so it uses commas. |
| `let y(t) = ...` | A function only this visual uses |
| `view Part 1` | Starts lines that apply only while that view's button is picked, up to the next `view` or `panel` line (details below) |
| `caption: ...` | Text under the figure: math, refs and `{= }` live values allowed. Several caption lines join into one paragraph. |
| `readout: ...` | A monospace live readout box, same text rules |
| `place: after steps` | See "Where things go" |
| `layout: side by side` | Puts the panels next to each other on wide screens (stacked is the default) |
| `panel <type>` | Starts the next panel in the same figure. Every panel shares the sliders and views. |

**Views** are the Part 1 / Part 2 / Explore buttons. The first view is picked when the page opens. A view's `set` lines run when it's picked, its other lines (shading, dots, captions, even sliders) show only while it's picked, and its button stays lit as long as its `set` values hold. Lines before the first `view` apply to every view. A slider inside a view appears only in that view and applies its value when the view is picked.

**Legends and labels.** `legend "..."` on any drawing line adds an entry to the figure's legend (once, even if the line repeats in several views). `label "..."` writes text right at the thing: next to a dot, stem or vector, at the top of a mark, at the right end of a curve. Add `below` to put a label underneath.

### `@plot` (and `panel plot`): curves on axes

| Line | |
|---|---|
| `x: -2 to 2; ticks every 0.5; label "x"` | Horizontal axis. Its name is the curve variable: write `t: -6 to 6` and curves use `t`. |
| `y: 0 to 1.5; ticks 0, 0.5, 1; label "$f_X(x)$"` | Vertical axis. Leave it out to fit the curves. |
| `ticks every pi/2` (an axis option) | Steps of π are labeled π/2, π, 3π/2 … |
| `ticks 0, 1/pi as "1/π", 0.5 as "½"` (an axis option) | Custom tick labels |
| `curve f`, `curve sin(x - t0); dashed` | A curve: the name of a `let` function, or an expression in the axis variable. Options: `color N`, `muted`, `dashed`, `dotted`, `width N`, `legend "..."`, `label "..."`. Jumps in `if(...)` curves are drawn sharp. |
| `shade f from 0 to b` | Fills the area under `f` between two bounds (expressions). Options: `color N`. |
| `mark x = 4/3; label "E[X] = 4/3"` | A vertical marker line. `mark y = 0.5` draws a horizontal one. |
| `dot (2, y(2)); label "{= y(2)}"; below` | A point. Add `for t = -4 to 4` or `for t in -4, -2, 0` as an option to draw several. |

### `@stem` (and `panel stem`): discrete sequences and spectra

Same axis lines as a plot, plus:

`stem (n, a(n)); for n = -9 to 9; filled if kept(n); label "{= a(n)}"`

Options: `for ...`, `hollow`, `filled if <condition>` (hollow otherwise), `color N`, `label "..."`.

### `@phasor` (and `panel phasor`): the complex plane

A unit circle with Re and Im axes. `radius 2` changes its scale.

`vector exp(-j*n*pi*t0); for n = 0 to 3; label "n={= n}"; one color each`

Vectors that land on the same spot share one label.

### `@table` (and `panel table`): live tables

```
rows n = -3 to 3
column "n" = n
column "$b_n/a_n$" = exp(-j*n*pi*t0) : 3
```

`rows n in 0, 1, 2, 5` works too. Complex results show as `a + bj`. For a fixed table, use a Markdown table in the text instead.

### `@calc` (and `panel calc`): calculators

```
input z: start 1.625; step 0.001; label "Find Q(z) for a z-score"
output "Q(z)" = Q(z) : 4
output "Φ(z)" = 1 - Q(z) : 4
```

`input` also takes `min` and `max` options. Outputs update as you type, and the inputs work as variables for any other panel in the figure. (The pop-out calculator in the app is a separate tool that every page has. `@calc` is for a small calculator built for one problem.)

## 7. What the load report catches

When a file is dropped in, TrainFrame lists problems with their line numbers. A **Copy report for AI** button copies the list in a form you can paste straight back to the AI that wrote the file.

**Errors** (the block or line is left out until fixed): an unknown block type ("did you mean `@formula`?"), a ref to an ID that doesn't exist, a duplicate ID, an expression that doesn't parse, a variable or function that isn't defined, a failed `check:`, an unknown visual line or option (often a `,` where a `;` belongs), unclosed `$` or `$$`, LaTeX that KaTeX can't render, and a `@step` outside any problem.

**Warnings** (shown, but the file still works): a formula no step uses, a part with no `@answer`, an unknown property, a numeric answer with no `check:`, and a missing `title`.

## 8. Writing tips (for people and for AI)

- One `@step` per move. Give it a short title, a sentence or two, and usually one `$$` block.
- Put a formula in the bank only if a step uses it, and tag that step with it.
- Never put `{{ }}` refs inside `$...$`.
- Write `*` between factors, except right after a plain number.
- Define the functions a problem is about with `let` on the `@problem`, so its plots and checks agree.
- Give every numeric answer a `check:`, and prefer checks that compute it a different way.
- Keep visual lines short. If a figure needs more than about 15 lines, split it into panels or two figures.

## 9. Growing the language

The language grows by **adding words**: block types for new kinds of classes (a `@circuit`, a `@code` listing, a `@truth-table`), visual types, options and styling words. Each one is a single entry in the app's list of block and visual types (name, allowed properties or options, how it draws, what the load report checks). Adding one doesn't touch the others.

Three promises keep old files working:

1. **Additions only.** A word never changes meaning and is never removed. A better way to write something can be added, but the old way keeps working.
2. **Unknown words are reported, not guessed.** A file that uses a word this copy of the app doesn't know yet gets a load-report error that names the word. The rest of the file still loads.
3. **Every change is listed below** with the version that added it, so an AI writing files can be told which version to target.

To ask for a new word, describe what it should show and write a sample block the way you'd want to type it. The sample becomes the spec entry.

## Version history

| Version | Changes |
|---|---|
| 0.2 | Semicolons separate the parts of visual lines (`y: 0 to 1.5; ticks 0, 0.5, 1; label "..."`), and `for ...` became an option. IDs on header lines go in braces (`@formula {F1} Valid PDF`); bare IDs still work. Added `folder` on `@frame`. The extension is `.frame` only. |
| 0.1 | First draft |
