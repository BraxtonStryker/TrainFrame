# How to write a .frame file

This guide is for an AI (or a person) writing a file for TrainFrame. A `.frame` file is plain text that TrainFrame turns into an interactive walkthrough: problems revealed one step at a time, formula tags that open the formula in place, and answers at the end of each part. The full reference is `docs/LANGUAGE.md`; this page is all you need to write a good file.

## A complete small file

```frame
@frame {ecen305-hw4}
title: Homework 4 Walkthrough
class: ECEN 305
folder: Homework
subtitle: ECEN 305 · Chapter 4
fact: Problems = 1
steps: per part
Work each step on paper first, then reveal it to check.

@formula {F1} Valid PDF
group: PDF & CDF
$$ \int_{-\infty}^{\infty} f_X(x)\,dx = 1 $$
Use it to solve for an unknown constant.

@formula {F2} CDF from the PDF
group: PDF & CDF
$$ F_X(x) = \int_{-\infty}^{x} f_X(u)\,du $$

@problem {P1} Find the constant, then a probability
points: 6
short: Normalization

@given
$X$ has PDF $f_X(x) = c\,x$ for $0 \le x \le 2$, and $0$ otherwise.

@part {a}
points: 3
Find $c$.

@step Set the total area to 1 {{F1}}
$$ \int_0^2 c\,x\,dx = 1 $$

@step Integrate and solve
$$ c\left[\frac{x^2}{2}\right]_0^2 = 2c = 1 \;\Rightarrow\; c = \frac12 $$

@answer
$$ c = \frac{1}{2} $$

@part {b}
points: 3
Find $P[X \le 1]$.

@step Use the CDF {{F2}}
$$ P[X \le 1] = \int_0^1 \frac{x}{2}\,dx = \frac{1}{4} $$

@answer
$$ P[X \le 1] = \frac{1}{4} $$
```

## How the lines work

- A **block** starts with a line that begins with `@` (at the very start of the line). Everything up to the next `@` line belongs to it.
- Right under the `@` line come **properties**, written `key: value`. The first other line (or a blank line) starts the **body**, which is the block's text.
- **IDs go in braces** right after the block type on `@frame`, `@formula`, `@definition`, `@problem` and `@part`: `@formula {F1} Valid PDF`. Use letters, digits, `-` or `_`. Formula, definition and problem IDs must all be different.

## The blocks

| Block | Header line | Properties | Body |
|---|---|---|---|
| `@frame` | `@frame {file-id}` (first line, once) | `title`, `class`, `folder`, `subtitle`, `fact` (repeat it: `fact: Due = Oct 6`), `steps` (`per part` or `per problem`) | A short intro |
| `@formula` | `@formula {F1} Title` | `group` | The formula in `$$...$$`, plus a one-line note |
| `@definition` | `@definition {D1} Term` | `group` | The definition |
| `@problem` | `@problem {P1} Title` | `points`, `short` (a short name for the side rail) | none |
| `@given` | `@given` | none | The problem statement |
| `@plan` | `@plan` | none | The approach, in a sentence or two (optional) |
| `@part` | `@part {a}` or `@part {a} Title` | `points` | The part's question |
| `@step` | `@step Short title {{F1}}` | none | One move: a sentence and usually one `$$` block |
| `@answer` | `@answer` | none | The final answer |
| `@explain` | `@explain Prompt` | none | A bullet list of what a full written explanation needs (optional) |
| `@note`, `@tip`, `@warning` | `@note Title` | none | A short callout |
| `@section` | `@section Title` | none | A heading and text (for notes files) |
| `@checklist` | `@checklist Title` | none | A `- ` list; each item gets a checkbox |

Order inside a problem: `@given`, `@plan`, then for each part: `@part`, its `@step`s, its `@answer`. A problem with no parts can go straight from `@given` to steps and an answer.

## Text

- Math is LaTeX: `$inline$` and `$$display$$`. Put display math on its own line.
- `**bold**`, `*italic*`, `` `code` ``, `==highlight==`, `- ` and `1. ` lists, and `| a | b |` tables (with a `|---|---|` row under the header).
- `{{F1}}` in text is a tag that opens formula F1. On a `@step` line, `{{F1}}` tags the step "Uses F1".
- No HTML and no `#` headings. A literal dollar sign is `\$`.

## Rules for a healthy file

1. Start with `@frame {id}` and give it `title:`, `class:` and `folder:`.
2. Put each formula the steps use in the bank once (`@formula`), and tag every step that uses it. Leave out formulas no step uses.
3. Only write `{{ID}}` for IDs you defined, and never inside `$...$`.
4. One move per `@step`, with a short title. Six small steps beat two long ones.
5. Give every `@part` an `@answer`.
6. Close every `$` and `$$`.
7. `@` only starts a line when it starts a block. Never write `#` headings or HTML.

## Optional extras

Leave these out unless you're asked for them.

- `let f(x) = 3/8 * x^2` on a `@problem` defines a function, and `{= f(1) : 3}` in text shows its value to 3 decimals.
- `check: f(2) = 1.5` under an `@answer` makes TrainFrame work out the left side and confirm the number. Checks are optional.
- Plots and other visuals (`@plot`, `@stem`, `@phasor`, `@table`, `@calc`) are described in `docs/LANGUAGE.md`.

Expressions use `+ - * / ^`, `pi`, `e`, `j`, `sqrt`, `exp`, `ln`, `sin`, `cos`, `abs`, `if(cond, a, b)`, `sum(n = 1 to N, ...)` and `integral(x = a to b, ...)`. Write `*` between factors (`2*x`; `2x` only works right after a plain number).

## Before you hand it over

- The first line is `@frame {id}`, and every `@frame`, `@formula`, `@definition`, `@problem` and `@part` has its `{ID}`.
- Every `{{ref}}` matches an ID in the file.
- Every `$` and `$$` is closed.
- Every `@part` has an `@answer`.
- The reply is the file and nothing else.
