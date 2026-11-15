# TrainFrame

Interactive homework walkthroughs from plain-text **frame files**. You (or an AI) write a `.frame` file for a homework set, a lecture or an exam review, and TrainFrame turns it into a page where you can:

- reveal a problem one step at a time,
- open a formula from a tag without losing your place,
- move a slider and watch a plot follow.

The app is written once. Every new file is only content.

**Use it:** https://braxtonstryker.github.io/TrainFrame/

**Status: 0.6.** Files are checked when they load (a load report lists errors with line numbers, with a **Copy report for AI** button) and open as walkthroughs with live plots. Each class has a formula sheet and a search, a class or a file can be saved as one offline HTML page, and the calculator is a full TI-36X Pro style one. See Help > What's new in the app for each version.

- **Classes and folders.** The Library lists every class. A file's `class:` line picks its class and its `folder:` line picks the folder. You can move files, and rename, archive or delete classes, in the app.
- **Tabs that remember.** Open classes get tabs next to Library, and each class's open files get tabs above its sections (Assignments, Formula sheet, Search, Add files). Every tab keeps its place.
- **An open file** has a problem rail on the left, a notes box on the right edge (one per file, saved as you type), and a calculator window that floats over every screen: a keypad with history and exact answers, solvers, statistics, a function table, matrices and number bases.
- Installable, works offline, and keeps everything in your browser. Files are always dropped in, and nothing is uploaded.

## Writing a frame file

```
@frame {my-hw3}
title: Homework 3
class: ECEN 305
folder: Homework

@problem {P1} Find the constant
points: 8
let f(x) = if(0 <= x <= 2, 3/8 * x^2, 0)

@step Normalize {{F1}}
$$ \int_0^2 c\,x^2\,dx = 1 $$

@plot Density
x: -0.4 to 2.4; ticks 0, 1, 2
slider b: 0 to 2; step 0.05; start 1
curve f
shade f from 0 to b
```

The whole language is in [docs/LANGUAGE.md](docs/LANGUAGE.md). [examples/demo.frame](examples/demo.frame) is a complete small file.

## Repository

- `index.html`: the whole app, one file with inline CSS and JS, no build step and nothing loaded from other sites.
- `docs/LANGUAGE.md`: the frame language. `PLAN.md`: the build plan and the decisions behind it.
- `examples/demo.frame`: invented problems, offered by the app's "Add the demo file". Real coursework stays out of this public repo (`examples-private/` is gitignored).
- `vendor/katex.min.js`: KaTeX (MIT, see `vendor/LICENSE-katex.txt`), for the math.
- `sw.js`, `manifest.webmanifest`, `icons/`: the installable offline app. After changing any precached file, run `python -I tools/sw_version.py --sync` so browsers pick up the new version.
- `tools/harness.py`: drives the app in headless Chrome and checks it. Run `python -I tools/harness.py`.
- See [CLAUDE.md](CLAUDE.md) for development notes.
