---
kind: project
title: "Project: Todo CLI"
phase: Phase 2
time: about 6–8 hours
---
Your first complete project. A todo list sounds simple, but done properly it uses almost everything from Phase 2: strict TypeScript types, command-line parsing, file storage, validation, error handling and exit codes. Build it in `projects/todo-cli/`.

!!! idea "Why build this?"
    It's small enough to finish in a weekend or two, and it has the same shape as a backend: **input** (commands instead of HTTP requests), **validation**, **business logic**, **storage** (a JSON file instead of a database) and **output**. In Phase 3 the input changes to HTTP, and the rest stays familiar.

## What you're building

```bash
todo add "Buy milk" --priority high --due 2026-11-01
todo add "Read chapter 12"
todo list
```

```output
 ID  PRI     DUE         TASK
  1  high    2026-11-01  Buy milk
  2  medium  —           Read chapter 12

2 open · 0 done
```

```bash
todo done 1
todo list --all
todo stats
todo remove 7
```

```output
Error: no todo with id 7
```

(and the exit code is 1)

To run it as `todo` instead of `node src/index.ts`, add a script `"todo": "node src/index.ts"` to `package.json` and use `npm run todo -- add "Buy milk"`. (The `--` passes the arguments through to your program.)

## Requirements

### The data

```ts
type Priority = "low" | "medium" | "high";

type Todo = {
  readonly id: number;
  text: string;
  done: boolean;
  priority: Priority;
  due?: string;          // "YYYY-MM-DD"
  createdAt: string;     // ISO timestamp
  completedAt?: string;  // ISO timestamp, set when marked done
};
```

### Commands

| Command | Behaviour |
|---|---|
| `add "<text>" [--priority low\|medium\|high] [--due YYYY-MM-DD]` | Adds a todo. Priority defaults to `medium`. Prints `Added #3: Buy milk`. |
| `list [--all] [--done] [--priority <p>]` | Shows **open** todos by default; `--all` shows everything; `--done` only finished ones. Sorted by priority (high first), then due date (earliest first, none last). |
| `done <id>` | Marks it done and sets `completedAt` |
| `undo <id>` | Marks it open again and removes `completedAt` |
| `edit <id> "<new text>"` | Changes the text |
| `remove <id>` | Deletes it |
| `clear-done` | Deletes all finished todos and prints how many were removed |
| `stats` | Open, done, overdue, and done in the last 7 days |
| `help` (or no command, or `--help`) | Prints usage instructions |

### Rules

1. **Validation.** Empty text, an unknown priority, an invalid date (`2026-13-45`), a missing or non-numeric id, or an unknown command must print a clear message to **stderr** and set **exit code 1**. Nothing in the file may change.
2. **IDs are never reused.** The next id is the highest existing id plus 1, so deleting #3 and adding a new todo gives #4 (or higher), never #3 again.
3. **Storage.** Save to `data/todos.json`, located using `import.meta.dirname`, so the command works from any folder. Allow an override through the environment variable `TODO_FILE` (great for testing with a throwaway file).
4. **Atomic saves.** Write to a temp file, then rename (Chapter 10).
5. **A missing file is fine** (start empty). A **corrupted** file must give a clear error, not a stack trace, and must **not** be overwritten.
6. **No `any`**, and `npm run check` passes.

## Suggested structure

```text
projects/todo-cli/
├── src/
│   ├── index.ts       ← parses arguments, calls the right command, sets the exit code
│   ├── types.ts       ← Todo, Priority, and friends
│   ├── storage.ts     ← loadTodos, saveTodos (the only file that touches the disk)
│   ├── todos.ts       ← pure logic: addTodo, completeTodo, sortTodos, getStats...
│   ├── format.ts      ← turns todos into the table and messages
│   └── errors.ts      ← a CliError class (message + exit code)
├── data/              ← in .gitignore
├── package.json
├── tsconfig.json
└── README.md
```

!!! idea "Keep the logic pure"
    Make the functions in `todos.ts` **pure**: they take todos in and return new todos (or a result) out, and never read files or print. For example, `addTodo(todos, input)` returns a new array. Pure functions are easy to reason about, and in Phase 6 they'll be trivial to test. Only `storage.ts` touches the disk, and only `index.ts` prints.

## Build it in milestones

1. **Skeleton.** `index.ts` reads the command with `parseArgs` and prints which command it got. `help` works.
2. **Add and list.** Implement `add` and `list` with in-memory data (no file yet).
3. **Storage.** Add `loadTodos` and `saveTodos`. Todos survive between runs.
4. **The rest of the commands.** `done`, `undo`, `edit`, `remove`, `clear-done`.
5. **Validation and errors.** Every bad input from the rules gives a clear message and exit code 1.
6. **Sorting, stats and polish.** Make the output look good, and write the README.

Commit after **each** milestone with a clear message.

## Acceptance checklist

Run these with `TODO_FILE=/tmp/test-todos.json` (or another throwaway path) so you don't mess up your real list:

<ul class="checklist">
<li>A fresh start with no file works, and <code>list</code> says there's nothing to do.</li>
<li><code>add</code> without text fails with exit code 1.</li>
<li><code>add "x" --priority urgent</code> fails with a message listing the valid priorities.</li>
<li><code>add "x" --due 2026-02-30</code> fails (February has no 30th).</li>
<li>Deleting #2 and adding a new todo never produces id 2 again.</li>
<li><code>done 99</code> fails with <code>no todo with id 99</code> and exit code 1.</li>
<li><code>list</code> is sorted by priority, then due date.</li>
<li>Writing <code>{oops</code> into the data file and running <code>list</code> gives a friendly error, and the file is left untouched.</li>
<li>The command works when run from a different folder.</li>
<li><code>npm run check</code> passes, and there's no <code>any</code>.</li>
<li>The README explains what it is, how to install and run it, every command, and one thing you learned.</li>
</ul>

## Stretch goals

- **Colour.** Use Node's built-in `styleText` from `node:util` to show overdue todos in red and high priority in bold: `styleText(["bold", "red"], "overdue")`.
- **Search:** `todo find milk`.
- **Undo the last action** (keep a backup of the previous file).
- **Export:** `todo export --format csv`.

!!! interview "Interview corner"
    Projects become interview stories. Be ready to answer: *"How do you make sure the data file can't be corrupted if the program crashes while saving?"* (atomic write: temp file and rename) and *"Why are your todo functions pure?"* (easier to reason about and test, and side effects stay at the edges).
