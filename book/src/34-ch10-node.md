---
kind: chapter
num: 10
title: "Node.js Core: Files, Processes and Configuration"
phase: Phase 2
time: about 4 hours
---
A backend program reads configuration, takes input, reads and writes files, and reports success or failure to whoever started it. This chapter covers the Node.js tools for all of that, and these are exactly the tools you'll use in the Todo CLI project.

!!! learn "What you'll learn"
    - ES modules vs CommonJS
    - `process`: arguments, environment, exit codes
    - Parsing command-line options with `parseArgs`
    - File paths that work from any folder
    - Reading and writing files (and JSON)
    - Environment variables and `.env` files

## 10.1 Two module systems

You'll see two styles of imports in Node code:

```js
// ES modules (ESM): the modern standard. Use this.
import { readFile } from "node:fs/promises";
export function hello() {}

// CommonJS (CJS): the older Node style. You'll see it in older code and tutorials.
const { readFile } = require("node:fs/promises");
module.exports = { hello };
```

Your projects use ESM because `package.json` has `"type": "module"`. The `node:` prefix (`node:fs`, `node:path`) makes it clear that a module is built into Node rather than downloaded from npm.

## 10.2 `process`: talking to the outside world

`process` is a global object that represents your running program.

| Property | What it gives you |
|---|---|
| `process.argv` | Command-line words: `[nodePath, scriptPath, ...yourArgs]` |
| `process.env` | Environment variables (always strings, or `undefined`) |
| `process.cwd()` | The folder the command was run **from** |
| `process.exitCode` | Set it to report success (`0`) or failure (anything else) |
| `process.platform` | `"win32"`, `"linux"`, `"darwin"` (Mac) |
| `process.uptime()` | Seconds since the program started |
| `process.memoryUsage()` | How much memory the program is using |

### Exit codes

When a program finishes, it reports a number to whoever started it. **`0` means success; anything else means failure.** Scripts, CI pipelines and servers that restart crashed apps all rely on this.

```ts
if (!fileFound) {
  console.error("Error: todos.json is corrupted");   // errors go to stderr
  process.exitCode = 1;                               // report failure
}
```

```bash
node app.ts; echo "exit code: $?"    # $? shows the last exit code in Git Bash
```

Prefer `process.exitCode = 1` over `process.exit(1)`. `process.exit` stops immediately, even if files are still being written.

`console.log` writes to **stdout** (normal output). `console.error` writes to **stderr** (error output). They look the same in your terminal, but tools and servers treat them separately, so send errors to stderr.

## 10.3 Parsing command-line options

Reading `process.argv[2]` by hand gets messy quickly. Node has a built-in parser:

```ts
import { parseArgs } from "node:util";

const { values, positionals } = parseArgs({
  args: process.argv.slice(2),
  options: {
    name:  { type: "string",  short: "n", default: "stranger" },
    shout: { type: "boolean", default: false },
    times: { type: "string",  default: "1" },
  },
  allowPositionals: true,
});

console.log(values, positionals);
```

```bash
node src/greet.ts add "buy milk" -n Ali --shout --times 3
```

```output
[Object: null prototype] { name: 'Ali', shout: true, times: '3' } [ 'add', 'buy milk' ]
```

- **Options** start with `--` (or `-` for the short form). `values` holds them.
- **Positionals** are the plain words. `positionals` holds them in order.
- Unknown options throw an error, which protects you from typos like `--shuot`.
- Option values are always strings (or booleans). `--times 3` gives `"3"`, so convert and validate it.

## 10.4 Paths that work from any folder

A relative path like `"data/todos.json"` is resolved from `process.cwd()`, which is **wherever the user ran the command**. Run your script from a different folder and you get `ENOENT: no such file or directory`.

To find files relative to **your source file**, use `import.meta.dirname`:

```ts
import path from "node:path";

import.meta.dirname;    // folder of the current file, e.g. E:\Backend_Learning\ch10\src
import.meta.filename;   // full path of the current file

const dataFile = path.join(import.meta.dirname, "..", "data", "todos.json");
// E:\Backend_Learning\ch10\data\todos.json, wherever you run it from
```

| Function | Example | Result |
|---|---|---|
| `path.join(...)` | `path.join("data", "todos.json")` | `data\todos.json` on Windows, `data/todos.json` on Linux |
| `path.resolve(...)` | `path.resolve("data")` | an absolute path, based on the current folder |
| `path.dirname(p)` | `path.dirname("/a/b/notes.txt")` | `/a/b` |
| `path.basename(p)` | `path.basename("/a/b/notes.txt")` | `notes.txt` |
| `path.extname(p)` | `path.extname("notes.txt")` | `.txt` |

!!! idea "Never build paths by gluing strings"
    `dir + "/" + file` breaks on Windows (which uses `\`), and on double slashes. `path.join` handles it correctly on every system.

## 10.5 Reading and writing files

Use the promise-based API from `node:fs/promises` together with `await` (Chapter 11 explains `async`/`await` in detail; for now, `await` means "wait for this to finish").

```ts
import { readFile, writeFile, mkdir, readdir, rm } from "node:fs/promises";

const text = await readFile("notes.txt", "utf8");          // read as text
await writeFile("out.txt", "Hello\n", "utf8");               // create or overwrite
await writeFile("log.txt", "more\n", { flag: "a" });         // append
await mkdir("data/backups", { recursive: true });            // like mkdir -p
const files = await readdir(".");                            // list a folder
await rm("old.txt", { force: true });                        // delete (no error if missing)
```

Always pass `"utf8"`, or you get a `Buffer` of raw bytes instead of a string.

### Reading and writing JSON, safely

```ts
import { readFile, writeFile, mkdir, rename } from "node:fs/promises";
import path from "node:path";

type Todo = { id: number; text: string; done: boolean };

function isNodeError(err: unknown): err is NodeJS.ErrnoException {
  return err instanceof Error && "code" in err;
}

async function loadTodos(file: string): Promise<Todo[]> {
  try {
    const text = await readFile(file, "utf8");
    return JSON.parse(text) as Todo[];
  } catch (err) {
    if (isNodeError(err) && err.code === "ENOENT") {
      return [];          // no file yet: that's fine, start empty
    }
    throw err;            // anything else (broken JSON, no permission) is a real problem
  }
}

async function saveTodos(file: string, todos: Todo[]): Promise<void> {
  await mkdir(path.dirname(file), { recursive: true });
  const tmp = `${file}.tmp`;
  await writeFile(tmp, JSON.stringify(todos, null, 2) + "\n", "utf8");
  await rename(tmp, file);   // swap the new file in at once
}
```

Three professional details in that code:

1. **A missing file isn't an error** on first run. Check `err.code === "ENOENT"` and start empty. Re-throw any other error, so you don't silently hide real problems.
2. **`JSON.stringify(data, null, 2)`** writes nicely indented JSON that people can read and Git can diff.
3. **Write to a temporary file, then rename.** If the program crashes halfway through writing, the old file is still intact. Renaming is effectively instant, so you never end up with a half-written file. This is called an **atomic write**.

!!! warning "`as Todo[]` trusts the file"
    `JSON.parse(text) as Todo[]` tells TypeScript to trust that the file contains todos. That's acceptable for a file only your own program writes. It's **never** acceptable for data from users or other systems. Validate those (Chapter 9, and Zod in Chapter 15).

### File error codes you'll meet

| Code | Meaning |
|---|---|
| `ENOENT` | No such file or directory |
| `EACCES` / `EPERM` | No permission |
| `EISDIR` | Expected a file, got a folder |
| `EEXIST` | It already exists |

## 10.6 Configuration and environment variables

Your app needs settings that change between your laptop and production: a port, a database URL, API keys. Hard-coding them is a bad idea (and putting secrets in code is dangerous). The standard answer is **environment variables**.

```ts
const port = process.env.PORT;   // string | undefined
```

During development, keep them in a `.env` file:

```ini
# .env  (never commit this file)
PORT=4000
APP_NAME="Slotify"
```

Node can load it for you:

```bash
node --env-file=.env src/server.ts
node --env-file-if-exists=.env src/server.ts   # no error if the file is missing
```

Professional habits:

- **`.env` goes in `.gitignore`.** Commit a **`.env.example`** with the variable names and dummy values, so teammates know what to set.
- **Validate configuration at startup.** If `PORT` is `"abc"`, crash immediately with a clear message, rather than failing mysteriously later. This is called **failing fast**.

```ts
const port = Number(process.env.PORT ?? 3000);
if (!Number.isInteger(port) || port <= 0) {
  throw new Error(`PORT must be a positive whole number, got "${process.env.PORT}"`);
}
```

## 10.7 npm in more depth

```json
{
  "name": "todo-cli",
  "type": "module",
  "scripts": {
    "start": "node src/index.ts",
    "dev": "node --watch src/index.ts",
    "check": "tsc --noEmit"
  },
  "dependencies": { "zod": "^4.6.7" },
  "devDependencies": { "typescript": "^7.0.2", "@types/node": "^26.6.5" }
}
```

- **`dependencies`** are needed to *run* the app. **`devDependencies`** are only needed while developing (compilers, type definitions).
- **Version ranges:** `^4.6.7` means "4.6.7 or any newer 4.x". Bumping the first number (`5.0.0`) means breaking changes, so npm won't do that automatically. This scheme is called **semantic versioning**: `MAJOR.MINOR.PATCH`.
- **`package-lock.json`** pins the exact versions that were installed. `npm ci` installs exactly those, which is what servers and CI should use.
- **`npm run dev`** with `node --watch` restarts your program every time you save a file.

!!! checkpoint "Checkpoint 10"
    1. What's the difference between `process.cwd()` and `import.meta.dirname`?
    2. Why use `process.exitCode = 1` instead of `process.exit(1)`?
    3. Your program reads `data/todos.json` and works, but fails with `ENOENT` when run from another folder. Why, and how do you fix it?
    4. Why write to a `.tmp` file and then rename it?
    5. What goes in `.env`, and what goes in `.env.example`?
    6. What's the difference between `npm install` and `npm ci`?

## Tasks

Set up `ch10/` like the Chapter 8 project.

!!! task "Task 10.1 · A greeting CLI · Core"
    Write `ch10/src/greet.ts` using `parseArgs`:

    ```bash
    node src/greet.ts --name Sana                  # Hello, Sana!
    node src/greet.ts -n Sana --shout              # HELLO, SANA!
    node src/greet.ts -n Sana --times 3            # prints it 3 times
    node src/greet.ts --times abc                  # error message on stderr, exit code 1
    node src/greet.ts --help                       # prints usage instructions
    ```

    **Done when:** all five behave as shown, and `echo $?` shows `1` only for the invalid case. {: .done }

!!! task "Task 10.2 · Word counter · Core"
    Write `ch10/src/wc.ts`, a small version of the Unix `wc` command. Given a folder path, print the number of lines, words and characters in every `.txt` and `.md` file in that folder, plus a total.

    ```output
      lines   words   chars  file
         12      85     512  notes.md
          3      10      52  todo.txt
         15      95     564  total
    ```

    - Use `readdir`, `path.extname`, `path.join` and `readFile`.
    - A missing folder prints a friendly error and sets exit code 1.
    - Bonus: align the columns with `padStart`.

!!! task "Task 10.3 · Config loader · Core"
    Write `ch10/src/config.ts` that reads `PORT`, `APP_NAME` and `LOG_LEVEL` (`"debug" | "info" | "warn" | "error"`, default `"info"`) from the environment and exports a typed `config` object. Invalid values must **throw at startup** with a clear message. Create `.env` and `.env.example`, check that `.env` is ignored by Git, and run it with `node --env-file=.env`.

!!! task "Task 10.4 · Crash-safe saving · Stretch"
    Write a script that saves a 10,000-item array to JSON using the temp-file-and-rename approach, and another that writes directly with `writeFile`. Explain in `ch10/answers.md` what could go wrong with the direct approach if the power went out halfway through.
