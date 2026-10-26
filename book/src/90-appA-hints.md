---
kind: appendix
num: A
title: Hints for the Tasks
---
Read only one level at a time. **Level 1** is a nudge, **Level 2** names the concept or API you need, and **Level 3** is close to pseudo-code. If you need Level 3, that's fine. Afterwards, close the book and write the solution again from memory a day later.

## Phase 0

!!! hint "Task 1.1 · Terminal drills"
    **1 ·** Every step uses a command from section 1.3. Check `pwd` often so you know where you are.

    **2 ·** `mkdir -p` makes nested folders; `echo "..." > file` writes, `>>` appends; `cp` copies, `mv` renames.

    **3 ·** `grep -r "actually" drills/` searches recursively. `wc -l drills/a/b/c/notes.txt` counts lines.

!!! hint "Task 1.2 · System info script"
    **1 ·** Print `process.argv` first to see where the name ends up.

    **2 ·** The name is `process.argv[2]`; use `??` for the default. `(bytes / 1024 ** 3).toFixed(1)` gives GB with one decimal. Import `os` with `import os from "node:os"` (and name the file `.mjs`, or add a `package.json` with `"type": "module"`).

    **3 ·** `function toGB(bytes) { return (bytes / 1024 ** 3).toFixed(1); }`, then build each line with a template string. A name with spaces works if you quote it on the command line, because the quotes make it one argument.

!!! hint "Task 1.3 · Pipe detective"
    **1 ·** `ls -la` prints one line per file, plus a "total" line and the `.` and `..` entries.

    **2 ·** In `ls -la` output, the size is column 5. `sort -k5 -n` sorts numerically by column 5.

    **3 ·** `ls -la /c/Windows/System32 | sort -k5 -n -r | head -n 5`

!!! hint "Task 2.1 · Clean up your repository"
    **1 ·** Start with `git status` and handle one item at a time.

    **2 ·** `git add <path>` then `git commit -m "..."` for each logical group. `git branch -d experiment` deletes the branch (it's already merged).

    **3 ·** Suggested commits: "Add Lesson 00 answers and drills", "Add raw TCP HTTP client", "Add Lesson 02 TypeScript project". Then `git push`.

!!! hint "Task 2.2 · Branch, commit, merge"
    **1 ·** Make the first change, `add` and `commit` it; then make the second change and commit that separately.

    **2 ·** `git switch -c improve-sysinfo`, two commits, `git switch main`, `git merge improve-sysinfo`, `git push`, `git branch -d improve-sysinfo`.

    **3 ·** Messages like `Show current date and time in sysinfo` and `Show hostname in sysinfo`.

!!! hint "Task 2.3 · Practise undoing"
    **1 ·** Run `git status` after every step, so you can see what each command changed.

    **2 ·** `git restore undo.txt` throws away unstaged changes; `git restore --staged undo.txt` unstages (the change stays in the file); `git commit --amend -m "Fixed message"` rewrites the last commit.

!!! hint "Task 3.2 · Error detective"
    **1 ·** Read the error from the top: the file and line, the error type, then the trace.

    **2 ·** On the last item, `i + 1` is past the end of the array, so `list[i + 1]` is `undefined`.

    **3 ·** Use `u` (the current item) instead: `list.map((u) => shout(u))`, or simply `list.map(shout)`. For the four errors: use an undeclared name; reassign a `const`; call `JSON.parse("")`; call `readFileSync` on a missing file.

!!! hint "Task 3.3 · Docs scavenger hunt"
    **1 ·** Use the search box on each docs site.

    **2 ·** `path.join` normalises `..`. `find` returns one item, `filter` returns an array. The `.env` flag is in the Node docs under "Command-line options".

## Phase 1

!!! hint "Task 4.1 · DNS explorer"
    **1 ·** The first `Address` in the output belongs to the `Server` line: that's who answered.

    **2 ·** `MX` records list the mail servers for a domain, with a priority number (lower = preferred). `localhost` resolves to the loopback addresses `127.0.0.1` and `::1`.

!!! hint "Task 4.2 · Explain it like an interview"
    **1 ·** Use the seven steps as headings, then write one or two sentences under each.

    **2 ·** Say what problem each step solves: DNS (names → addresses), TCP (reliability), TLS (privacy and identity), HTTP (the request itself), server (your code), rendering.

!!! hint "Task 5.1 · Status code judge"
    **1 ·** Use the decision guide in section 5.4 for every 4xx.

    **2 ·** Watch for the traps: #8 has no body (`204`), #10 is unexpected (`500`), #12 doesn't create anything (`200`), and #9 is valid JSON that breaks a business rule (`422`).

    **3 ·** 1: 201 · 2: 409 · 3: 400 · 4: 400 · 5: 401 · 6: 403 · 7: 404 · 8: 204 · 9: 422 · 10: 500 · 11: 429 · 12: 200. Check your *reasons* as well as the numbers.

!!! hint "Task 5.2 · Decode real messages"
    **1 ·** Read the start line, then each header, then the body.

    **2 ·** For the conflict response, use status `409 Conflict`, a JSON `Content-Type`, and a body with a machine-readable code and a human message, for example `{"error":{"code":"SLOT_TAKEN","message":"..."}}`.

!!! hint "Task 5.4 · URL surgery"
    **1 ·** `const url = new URL("...")`, then look at `url.protocol`, `url.hostname`, `url.port`, `url.pathname`, `url.hash`.

    **2 ·** `for (const [key, value] of url.searchParams) { ... }`. Print `url.href` to see how the space was encoded.

!!! hint "Task 6.3 · Your first .http file"
    **1 ·** Copy the structure from section 6.3: `@baseUrl` at the top, `###` between requests.

    **2 ·** A `PATCH` needs a `Content-Type: application/json` header, a blank line, then the JSON body.

!!! hint "Task 6.4 · Speak HTTP by hand"
    **1 ·** Work strictly step by step and run the program after each one. Step 1 is five lines.

    **2 ·** The request is the lines `GET / HTTP/1.1`, `Host: example.com`, `Connection: close`, then an empty line, joined with `\r\n`. So the string must end with `\r\n\r\n`. In `data`, use `chunk.toString()` (or call `socket.setEncoding("utf8")` once). In `end`, find the split with `raw.indexOf("\r\n\r\n")`; don't use `split`, because the body might contain the same sequence.

    **3 ·**
    ```text
    sep = raw.indexOf("\r\n\r\n")
    head = raw.slice(0, sep);  body = raw.slice(sep + 4)
    [statusLine, ...headerLines] = head.split("\r\n")
    for each line: i = line.indexOf(":")
        name = line.slice(0, i).toLowerCase();  value = line.slice(i + 1).trim()
    print statusLine, headers object, body.slice(0, 200)
    ```
    Split each header at the **first** colon only, because values like dates contain colons too.

!!! hint "Task 6.5 · Break it on purpose"
    **2 ·** Without `Host`, the server replies `400 Bad Request`, because HTTP/1.1 requires it. Many servers accept bare `\n` line endings, but the standard says `\r\n`. HTTP/1.0 has no chunked encoding, so the numbers disappear. For TLS, `tls.connect({ host, port: 443, servername: host }, ...)` works almost exactly like `net.connect`, because TLS just adds an encrypted layer underneath the same text.

## Phase 2

!!! hint "Task 7.1 · Booking report"
    **1 ·** Each question is one chain of array methods. Decide filter → map → reduce for each.

    **2 ·** Revenue: `filter` out cancelled, `reduce` the cents, divide by 100, format with `toLocaleString("en-US", { style: "currency", currency: "PKR" })`. Per staff: `reduce` into an object (section 7.6). Most expensive: `reduce` keeping the bigger one, or `toSorted(...)[0]`. Times: `startsAt.slice(11, 16)` gives `"09:00"`.

    **3 ·** Day filter: `b.startsAt.startsWith("2026-11-03")`. Sort with `toSorted((a, b) => a.startsAt.localeCompare(b.startsAt))`. ISO strings sort correctly as text. That's one reason they're used everywhere.

!!! hint "Task 7.2 · Fix the bugs"
    **2 ·** a) `??` instead of `||`. b) A compare function: `(a, b) => a - b`. c) Spread is shallow; copy the array too: `{ ...original, tags: [...original.tags] }` or use `structuredClone`. d) Compare money in integer cents, or check `Math.abs(a - b) < Number.EPSILON`.

!!! hint "Task 8.2 · Model Slotify"
    **1 ·** Check every field against the table in section 8.3 before writing it.

    **2 ·** `export type BookingStatus = "pending" | "confirmed" | "cancelled" | "completed";`. Optional fields use `?`. IDs are `readonly id: string`. `serviceIds: string[]`, the same type as `Service["id"]`.

!!! hint "Task 8.3 · Formatting functions"
    **1 ·** The input is **cents**. What must happen before formatting?

    **2 ·** `new Intl.NumberFormat("en-US", { style: "currency", currency, minimumFractionDigits: 2 }).format(cents / 100)`. For durations: `Math.floor(minutes / 60)` hours and `minutes % 60` minutes, then build the string from the parts that aren't zero.

    **3 ·** If you compare results in code, note that `Intl` puts a **non-breaking space** (` `) between `PKR` and the number, so `=== "PKR 1,500.00"` with a normal space is `false`. Comparing by eye in the terminal is fine.

!!! hint "Task 8.4 · Narrowing practice"
    **2 ·** Check `v === null` first, then `typeof v`. For `firstWord`: `const first = sentence.split(" ")[0];` is `string | undefined`. Return `first ?? ""`.

!!! hint "Task 9.1 · Overlap"
    **1 ·** Write the rule from the task as code, word for word.

    **3 ·** `return aStart < bEnd && bStart < aEnd;`. Touching ranges (`aEnd === bStart`) give `false` because `<` is strict.

!!! hint "Task 9.2 · Errors to status codes"
    **2 ·** Copy the traffic-light pattern from section 9.3: one `case` per error, then `default: { const unreachable: never = error; throw new Error(...) }`. The compile error you'll see says something like *Type '"STAFF_BUSY"' is not assignable to type 'never'*.

!!! hint "Task 9.3 · Book a slot"
    **1 ·** Calculate `endHour` first. Then check the rules in the order given.

    **2 ·** Use `existing.filter((b) => b.staffId === staffId).some((b) => overlaps(...))`.

    **3 ·**
    ```text
    end = start + duration
    if start < 9 or end > 18 → return { ok: false, error: "OUTSIDE_HOURS" }
    if any booking with same staffId overlaps (start, end) → return { ok: false, error: "SLOT_TAKEN" }
    return { ok: true, value: { staffId, startHour: start, endHour: end } }
    ```

!!! hint "Task 9.4 · Generic pagination"
    **2 ·** `const start = (page - 1) * pageSize; items.slice(start, start + pageSize)`. `totalPages = Math.ceil(items.length / pageSize)`. Make it generic by replacing `string` with `T` and adding `<T>` after the function name.

    **3 ·** For invalid input, a clear choice is to throw an `Error` (page below 1, or a pageSize that isn't a positive integer), since it's a programming mistake. In Phase 3, Zod will reject these before they ever reach the function.

!!! hint "Task 9.5 · Parse a service"
    **1 ·** Copy the shape of `parseUser` and add one `if` block per field.

    **2 ·** Multiple of 15: `input.durationMinutes % 15 === 0`. Currency guard: `const CURRENCIES = ["PKR", "USD", "AED"] as const;` and `CURRENCIES.some((c) => c === value)`. For the optional description: `if ("description" in input && typeof input.description !== "string") return error`.

    **3 ·** Build the returned object field by field from the narrowed `input`. Include `description` only when it's present, e.g. `...(typeof d === "string" ? { description: d } : {})`.

!!! hint "Task 10.1 · A greeting CLI"
    **2 ·** `const times = Number(values.times)`; check `Number.isInteger(times) && times > 0`. On failure: `console.error(...)`, `process.exitCode = 1`, `return`. Add a `help: { type: "boolean", short: "h" }` option.

!!! hint "Task 10.2 · Word counter"
    **2 ·** `readdir(dir)`, keep names whose `path.extname` is `.txt` or `.md`. Lines: `text.split("\n").length` (careful with a final newline). Words: `text.split(/\s+/).filter(Boolean).length`. Characters: `text.length`.

    **3 ·** Wrap the `readdir` in `try`/`catch` and check for `ENOENT` (section 10.5). Use `String(n).padStart(7)` to align the columns.

!!! hint "Task 10.3 · Config loader"
    **2 ·** Read each variable, apply the default with `??`, check it, and `throw new Error("...")` with the bad value in the message. For `LOG_LEVEL`, use an `as const` array and a type guard.

!!! hint "Task 11.1 · Predict the output"
    **2 ·** Rule: synchronous code first, then **all** microtasks (promise callbacks, code after `await`, `queueMicrotask`), then the next timer.

    **3 ·** Answers: A: `A D C B`. B: `1 3 2`. C: `sync`, `promise 1`, `microtask`, `promise 2`, `timeout` (microtasks run in the order they were queued, and `promise 2` is only queued after `promise 1` runs). D: `Promise { 42 }`, `end`, `42`.

!!! hint "Task 11.2 · Sequential vs parallel"
    **2 ·** `const t = performance.now(); ...; console.log(performance.now() - t)`. For the failure: wrap `await Promise.all(...)` in `try`/`catch`; `Promise.allSettled` never throws, so map over its results and print each `status`.

!!! hint "Task 11.3 · A timeout helper"
    **2 ·** Race the real promise against one that rejects after `ms`.

    **3 ·**
    ```text
    timeout = new Promise((_, reject) => setTimeout(() => reject(new Error(...)), ms))
    return Promise.race([promise, timeout])
    ```
    Bonus: store the timer ID and `clearTimeout` it in a `finally`, so the timer doesn't keep the program alive.

!!! hint "Task 11.4 · Retry with backoff"
    **3 ·**
    ```text
    for attempt from 1 to attempts:
        try: return await fn()
        catch err: lastError = err
            if attempt < attempts: await sleep(100 * 2 ** (attempt - 1))
    throw lastError
    ```

!!! hint "Task 12.1 · An error hierarchy"
    **2 ·** Follow section 12.2, adding a `statusCode` field to `AppError`. In `describeError`, check `err instanceof AppError` first; everything else is a 500.

!!! hint "Task 12.2 · Debugger practice"
    **1 ·** Put a breakpoint on the `return` line and look at `total` and `bookings.length`.

    **2 ·** The total only includes confirmed bookings, but you divide by **all** bookings. Count the confirmed ones separately. With zero confirmed bookings, you'd divide by zero: return `0` (or throw), and say which in a comment.

!!! hint "Task 12.3 · Stream line counter"
    **2 ·** Copy the `readline` pattern from section 12.5. The search word is `process.argv[3]`.

!!! hint "Project · Todo CLI"
    **1 ·** Do the milestones in order. Get `add` and `list` working in memory before touching files.

    **2 ·** Dispatch commands with a `switch (command)`. Throw a `CliError` (with a message) for bad input, and catch it once in `index.ts` to print the message to stderr and set the exit code. For dates: `z.iso.date()` from Zod, or check the pattern and that `new Date(s).toISOString().slice(0, 10) === s` (that rejects `2026-02-30`). The next id: `Math.max(0, ...todos.map((t) => t.id)) + 1`.

    **3 ·** Sorting with two keys: `toSorted((a, b) => rank[b.priority] - rank[a.priority] || compareDue(a, b))`, where `rank = { low: 0, medium: 1, high: 2 }`. The `||` moves on to the second key when the first is equal (`0`).

!!! hint "Project · Log Analyzer"
    **1 ·** Write `parseLine` first, and test it on a few lines (including a corrupted one) before connecting it to the stream.

    **2 ·** Split each line on spaces: you should get exactly 5 parts. Check that the timestamp parses (`!Number.isNaN(Date.parse(t))`), the status is a 3-digit number, and the duration matches `/^\d+ms$/`. Route pattern: `path.split("/").map((seg) => (/^\d+$/.test(seg) ? ":id" : seg)).join("/")`. Use a `Map<string, number>` for counts.

    **3 ·** Percentile: `const sorted = values.toSorted((a, b) => a - b); return sorted[Math.ceil((p / 100) * sorted.length) - 1];` (handle an empty list). Busiest minute: count by `timestamp.toISOString().slice(0, 16)`.

## Phase 3

!!! hint "Task 13.2 · A raw notes API"
    **2 ·** Keep `let nextId = 1` and use `nextId++`. For `DELETE`, find the index with `findIndex`, `splice` it out, then `res.writeHead(204); res.end();`, with no body. Validate `pinned` with `typeof data.pinned === "boolean"` when it's present.

!!! hint "Task 13.3 · Search and update"
    **2 ·** `url.searchParams.get("search")` returns `string | null`. For `PATCH`, check each field only if it's present, then copy across only the fields that were sent.

!!! hint "Task 13.4 · Defensive server"
    **2 ·** Logging: record `performance.now()` at the start and log inside `res.on("finish", ...)`. Size limit: add up `chunk.length` inside the `for await` loop and stop as soon as the total exceeds 10,240. Media type: check `req.headers["content-type"]?.startsWith("application/json")`.

!!! hint "Task 14.3 · Protect the write routes"
    **2 ·** Pass the middleware as an extra argument on each write route: `app.post("/notes", requireApiKey, handler)`. Start the server with `node --env-file=.env --watch src/server.ts`. In `.http` files, add the header `x-api-key: {{apiKey}}`.

!!! hint "Task 14.5 · Request IDs"
    **2 ·** Set it with `res.setHeader("X-Request-Id", id)`. To share it with later middleware, store it in `res.locals.requestId`.

!!! hint "Task 15.1 · Schemas for notes"
    **2 ·** Tags: `z.array(z.string().trim().min(1)).max(5).default([])`. For `pinned` in the query: Zod 4 has `z.stringbool()`, which turns `"true"`/`"false"` (and `"1"`/`"0"`, `"yes"`/`"no"`) into booleans and rejects anything else. Make it `.optional()`.

!!! hint "Task 15.2 · Errors and the central handler"
    **1 ·** Do it one route at a time and re-run `requests.http` after each change.

    **2 ·** The service (or the handler, for now) throws `new NotFoundError("Note", id)`; the error handler turns it into `404`. Remember: the error handler needs all **four** parameters and must be registered last.

!!! hint "Task 15.3 · Prove it"
    **2 ·** For #5, send a body without the `Content-Type` header: `req.body` will be `undefined`, and `validateBody` turns that into a `400`. For #9, check your terminal: the full error must be logged there, but not sent to the client.

!!! hint "Task 16.1 · Review a bad API"
    **2 ·** Look for: verbs in URLs, singular names, IDs in query strings, `200` for errors, `success` flags instead of status codes, `GET` that deletes data (dangerous: browsers and crawlers prefetch `GET` links!), deep nesting, capital letters, mixed `snake_case` and `camelCase`, bare arrays, no versioning, and `POST` used for updates.

!!! hint "Task 16.3 · Make the notes API RESTful"
    **2 ·** Validate `sort` with `z.enum(["createdAt", "-createdAt"]).default("-createdAt")`. ISO timestamps compare correctly with `localeCompare`. Set the header with `res.location(...)`.

!!! hint "Task 17.1 · Layer the notes API"
    **1 ·** Create the folders and empty files first, then move code over one layer at a time, running `requests.http` as you go.

    **2 ·** Anything that touches `req` or `res` stays in the controller. Anything that's a rule ("a note must exist", "a notebook must exist") goes in the service. Only the repository touches the `Map`.

!!! hint "Task 17.2 · A second module"
    **2 ·** The **notes** service checks that a notebook exists when creating a note (it calls the notebook repository). The **notebooks** service checks for notes before deleting (it calls the note repository). Throw an `AppError(422, "NOTEBOOK_NOT_FOUND", ...)` for the first case and a `ConflictError` for the second.

!!! hint "Task 17.4 · Graceful shutdown"
    **2 ·** `const server = app.listen(...)`; `process.on("SIGINT", () => { console.log("Shutting down..."); server.close(() => process.exit(0)); });`

!!! hint "Project · URL Shortener"
    **1 ·** Build the service functions first: `createLink`, `getLink`, `recordClick`, `deleteLink`, `listLinks`. The controllers are then tiny.

    **2 ·** Validate `url` with `z.url({ protocol: /^https?$/ }).max(2048)` and `code` with `.regex(/^[a-zA-Z0-9_-]{3,30}$/)`. Generate codes with `crypto.randomInt(ALPHABET.length)` in a 7-step loop. Redirect with `res.redirect(302, link.url)`. Register `app.get("/:code", ...)` after `/health` and `/v1/links`.

    **3 ·** Generating a unique code:
    ```text
    repeat up to 5 times:
        code = generateCode()
        if repository has no link with this code → return code
    throw an AppError(500, "CODE_GENERATION_FAILED", ...)
    ```

!!! hint "Project · Slotify v0.1"
    **1 ·** Write `lib/time.ts` first, with small pure functions: `overlaps(aStart, aEnd, bStart, bEnd)` on `Date`s, `addMinutes(date, n)`, `isOnQuarterHour(date)`. Everything else builds on them.

    **2 ·** On a 15-minute boundary: `date.getUTCMinutes() % 15 === 0 && date.getUTCSeconds() === 0 && date.getUTCMilliseconds() === 0`, as a Zod `.refine` on `z.iso.datetime()`. Opening hours: compare `startsAt` with `Date.UTC(year, month, day, openingHour)` for the same day. The booking must satisfy `start >= opening` and `end <= closing`.

    **3 ·** Availability:
    ```text
    opening = date at openingHour UTC;  closing = date at closingHour UTC
    confirmed = this staff member's confirmed bookings
    for (t = opening; t + duration <= closing; t += 15 minutes):
        if t is in the past → skip
        if any confirmed booking overlaps (t, t + duration) → skip
        add t.toISOString() to slots
    ```
    Use the **same** `overlaps` function in the booking service and in availability.
