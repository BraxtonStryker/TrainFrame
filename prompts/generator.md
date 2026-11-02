# TrainFrame: the prompt for an AI

Hand this to an AI along with an assignment (a PDF, a photo or the text). The **Copy AI prompt** button in TrainFrame fills in the class and folder and adds the syntax guide (`docs/SYNTAX.md`) under it, so you only attach the assignment. Everything between the two lines below is the prompt.

---

Write a study walkthrough for TrainFrame, an app that turns a plain-text `.frame` file into an interactive page. Work every problem in the attached assignment, step by step, the way a good TA would at a whiteboard.

- Class: [CLASS]
- Folder: [FOLDER]
- File ID: a short ID made from the class and assignment, like `ecen305-hw4`

What to write:

1. One `.frame` file that follows the syntax guide below exactly. Reply with the file only, in one code block.
2. A formula bank: each formula or definition the steps use, written once with an ID (`F1`, `F2`, …), and tagged on every step that uses it.
3. For every problem: `@given` with the problem statement, an optional `@plan`, then each part with its steps and an `@answer`.
4. One move per step, with a short title. Show the math in LaTeX.
5. `check:` lines are optional. Leave them out unless a number is easy to confirm.

If part of the assignment is unclear or can't be read, add a `@note` to that problem saying so instead of guessing.

---
