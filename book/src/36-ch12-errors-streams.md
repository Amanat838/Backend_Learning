---
kind: chapter
num: 12
title: Errors, Debugging and Streams
phase: Phase 2
time: about 4 hours
---
Things go wrong in every real system: files go missing, input is invalid, other services time out. Good backend code expects this, handles it deliberately, and makes problems easy to find. This chapter covers throwing and catching errors properly, using a real debugger, and processing large files with streams without running out of memory.

!!! learn "What you'll learn"
    - `throw`, `try`, `catch` and `finally`
    - Custom error classes
    - Expected errors vs bugs
    - The VS Code debugger
    - Why streams exist
    - Reading huge files line by line

## 12.1 Throwing and catching

```ts
function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error("Cannot divide by zero");
  }
  return a / b;
}

try {
  divide(1, 0);
  console.log("never reached");
} catch (err) {
  console.log(err instanceof Error ? err.message : String(err));
} finally {
  console.log("finally always runs");   // cleanup: close files, release locks...
}
```

```output
Cannot divide by zero
finally always runs
```

When something throws, JavaScript stops the current function and jumps to the nearest `catch` up the call stack. If there is none, the program crashes with a stack trace.

- **Always throw `Error` objects**, never strings (`throw "oops"`). Only `Error` objects carry a **stack trace** showing where the problem happened.
- In TypeScript, the caught value is `unknown` (anything can be thrown). Check it with `instanceof Error` before reading `.message`.

!!! mistake "Swallowing errors"
    ```ts
    try {
      await saveBooking(booking);
    } catch (err) {
      // nothing here
    }
    ```
    An empty `catch` hides the problem completely. The booking silently wasn't saved, and nobody will ever know why. **Only catch an error if you can do something useful**: handle it, add context and re-throw it, or at least log it.

## 12.2 Custom error classes

Plain `Error` only has a message. A custom class can carry extra information and can be recognised with `instanceof`:

```ts
class AppError extends Error {
  readonly code: string;

  constructor(code: string, message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = "AppError";
    this.code = code;
  }
}

class InsufficientStockError extends AppError {
  readonly available: number;

  constructor(item: string, available: number) {
    super("INSUFFICIENT_STOCK", `Only ${available} ${item} left in stock`);
    this.name = "InsufficientStockError";
    this.available = available;
  }
}

try {
  throw new InsufficientStockError("chairs", 2);
} catch (err) {
  if (err instanceof InsufficientStockError) {
    console.log(err.code, err.message, err.available);
    // INSUFFICIENT_STOCK Only 2 chairs left in stock 2
  }
}
```

!!! warning "No parameter properties"
    You may see TypeScript code like `constructor(public code: string)`, which declares and assigns a field in one go. Your `erasableSyntaxOnly` setting forbids it, because Node can't simply strip it away. Declare the field and assign it in the constructor, as above.

### Adding context with `cause`

When you catch a low-level error and throw a more meaningful one, keep the original as the **cause**:

```ts
try {
  JSON.parse(text);
} catch (err) {
  throw new AppError("CONFIG_INVALID", "settings.json is not valid JSON", { cause: err });
}
```

The new error explains *what* failed in your terms ("settings.json is invalid"), and `err.cause` keeps the technical details ("Expected property name at position 1") for debugging.

In Chapter 15 you'll build an error class hierarchy like this (`NotFoundError`, `ConflictError`, `ValidationError`), and one central handler will turn each into the right HTTP status code.

## 12.3 Expected errors vs bugs

| | Expected (operational) errors | Bugs (programmer errors) |
|---|---|---|
| Examples | Invalid input, slot taken, file not found, a service timed out | `undefined` where it shouldn't be, a typo, wrong logic |
| Can you predict them? | Yes, they're part of normal life | No, they're mistakes |
| What to do | Handle them: return a `Result`, or throw a specific error and turn it into a clear message (`400`, `404`, `409`) | Log the full details, show a generic message (`500`), then **fix the code** |

Showing a user "Only 2 chairs left" is good. Showing a user "TypeError: Cannot read properties of undefined" is not, both because it's useless to them and because it leaks details of your code to anyone curious.

## 12.4 Debugging with VS Code

`console.log` is fine for quick checks, but a **debugger** lets you pause the program at any line and look at everything.

**The easiest way to start:**

1. In VS Code, open the Command Palette (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>) and run **Debug: JavaScript Debug Terminal**.
2. Click in the margin left of a line number to set a **breakpoint** (a red dot).
3. In that special terminal, run your program as usual: `node src/index.ts`.
4. The program pauses at the breakpoint.

While paused:

| Panel or button | What it does |
|---|---|
| **Variables** | Every variable's current value. Expand objects to look inside. |
| **Watch** | Add expressions to track, like `bookings.length` |
| **Call Stack** | Which functions called which to get here |
| **Continue** (<kbd>F5</kbd>) | Run until the next breakpoint |
| **Step Over** (<kbd>F10</kbd>) | Run the current line and stop at the next one |
| **Step Into** (<kbd>F11</kbd>) | Go inside the function called on this line |
| **Step Out** (<kbd>Shift</kbd>+<kbd>F11</kbd>) | Finish this function and return to its caller |

Two power tools:

- **Conditional breakpoint:** right-click the margin → *Add Conditional Breakpoint*, e.g. `booking.id === 42`. It only pauses when the condition is true. Great inside loops.
- **The `debugger;` statement:** write `debugger;` in your code, and the program pauses there whenever a debugger is attached.

## 12.5 Streams: handling data piece by piece

`readFile` loads an **entire** file into memory. That's fine for a small JSON file, but a server's log file can be gigabytes. Load that all at once and your program runs out of memory.

!!! analogy "Analogy: drinking from a glass vs a tap"
    `readFile` is like filling a giant glass with the whole river and only then starting to drink. A stream is a tap: water arrives a little at a time, you drink it as it comes, and you never need a glass bigger than one sip.

A **stream** delivers data in chunks as it becomes available. You've already met streams: the TCP socket in Chapter 6, and every HTTP request body (Chapter 13). There are three main kinds:

| Kind | Data flows... | Examples |
|---|---|---|
| **Readable** | out of it | `createReadStream(file)`, an incoming HTTP request |
| **Writable** | into it | `createWriteStream(file)`, an HTTP response |
| **Transform** | in, changed, out | `createGzip()` (compression) |

### Reading a file line by line

```ts
import { createReadStream } from "node:fs";
import { createInterface } from "node:readline";

const input = createReadStream("big.log", { encoding: "utf8" });
const lines = createInterface({ input, crlfDelay: Infinity });

let total = 0;
let errors = 0;
for await (const line of lines) {      // one line at a time
  total++;
  if (line.includes(" 500 ")) errors++;
}
console.log({ total, errors });
```

`for await` loops over an async source, waiting for each item. `crlfDelay: Infinity` makes Windows line endings (`\r\n`) count as one line break.

Real measurement on a 13.7 MB log file with 300,000 lines:

| Approach | Extra memory used |
|---|---|
| `readFile` + `split("\n")` | about 50 MB |
| Stream + `readline` | about 9 MB |

With a 5 GB file, the first approach crashes; the stream version still uses about 9 MB.

### Piping streams together

`pipeline` connects streams and handles errors and cleanup for you:

```ts
import { createReadStream, createWriteStream } from "node:fs";
import { pipeline } from "node:stream/promises";
import { createGzip } from "node:zlib";

await pipeline(
  createReadStream("big.log"),        // read...
  createGzip(),                        // ...compress...
  createWriteStream("big.log.gz"),     // ...write
);
```

That 13.7 MB log compresses to about 0.8 MB, and at no point is the whole file in memory.

!!! note "Backpressure"
    What if you read faster than you can write? Streams handle this automatically. When the writable side is full, the readable side pauses until it catches up. This is called **backpressure**, and `pipeline` takes care of it. It's one reason to prefer `pipeline` over wiring streams together by hand.

!!! checkpoint "Checkpoint 12"
    1. Why throw `new Error("...")` rather than a string?
    2. What's wrong with an empty `catch` block?
    3. "Slot already booked" and "Cannot read properties of undefined": which is an expected error and which is a bug? How should each reach the user?
    4. What does a conditional breakpoint do?
    5. Why would `readFile` fail on a 5 GB file when a stream doesn't?

## Tasks

!!! task "Task 12.1 · An error hierarchy · Core"
    In `ch12/src/errors.ts`, create `AppError` (with `code` and `statusCode`), plus three subclasses: `NotFoundError(resource, id)` → 404, `ConflictError(message)` → 409, `ValidationError(message)` → 400.

    Then write `findService(services, id)` that throws `NotFoundError` when the service is missing, and a `describeError(err: unknown): string` function that returns lines like `404 NOT_FOUND: Service 'svc_9' was not found` for `AppError`s, and `500 INTERNAL_ERROR` for anything else.

    **Done when:** you've tested all three error types plus a plain `Error`, and `npm run check` passes. {: .done }

!!! task "Task 12.2 · Debugger practice · Core"
    This function should return the average price of **confirmed** bookings, but it returns the wrong number:

    ```ts
    type B = { priceCents: number; status: string };

    export function averageConfirmed(bookings: B[]): number {
      let total = 0;
      for (const b of bookings) {
        if (b.status === "confirmed") total += b.priceCents;
      }
      return total / bookings.length;
    }
    ```

    Find the bug **with the debugger** (breakpoints and the Variables panel), not by staring. Write down what you saw at each step in `ch12/answers.md`, then fix it. What should happen if there are no confirmed bookings?

!!! task "Task 12.3 · Stream line counter · Core"
    Write `ch12/src/count.ts`, which takes a file path and a search word and prints how many lines contain the word, using `readline` (not `readFile`). Print the memory used with `process.memoryUsage().rss`.

    Create a test file with this generator (supporting code, so copying is fine):

    ```ts
    // ch12/src/make-log.ts
    import { writeFile } from "node:fs/promises";
    const paths = ["/v1/books", "/v1/books/42", "/health", "/v1/authors"];
    const statuses = [200, 200, 200, 201, 404, 500];
    const lines: string[] = [];
    for (let i = 0; i < 300_000; i++) {
      const minute = String(i % 60).padStart(2, "0");
      lines.push(`2026-11-03T09:${minute}:00Z GET ${paths[i % 4]} ${statuses[i % 6]} ${(i * 7) % 900}ms`);
    }
    await writeFile("big.log", lines.join("\n") + "\n");
    ```

    **Done when:** `node src/count.ts big.log " 500 "` prints `50000`. {: .done }

!!! task "Task 12.4 · Compress and compare · Stretch"
    Write `gzip.ts` that compresses any file with `pipeline`, and prints the original size, the compressed size and the percentage saved. Then compare the memory used by your stream counter with a `readFile` version, and record the numbers in `answers.md`.
