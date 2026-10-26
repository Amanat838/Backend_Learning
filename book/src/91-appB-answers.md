---
kind: appendix
num: B
title: Checkpoint Answers
---
Check your own answers first. If your wording is different but the idea is the same, count it as right.

### Checkpoint 1: The terminal, VS Code and Node.js
1. `cp` makes a copy and keeps the original; `mv` moves or renames, so the original is gone.
2. The number of lines in `app.log` that contain `404`.
3. Windows PowerShell's `>` writes UTF-16, while Linux tools expect UTF-8, so every other byte shows up as junk.
4. Read and write files, open network ports, start processes, read environment variables (any two).
5. Commit `package.json` and `package-lock.json`; never commit `node_modules/`.

### Checkpoint 2: Git and GitHub
1. `commit` saves a snapshot in your **local** history; `push` uploads your commits to the **remote** (GitHub).
2. `git add` the files for the first reason and commit; then `git add` the rest and commit again.
3. It doesn't say what changed or why, and it isn't in the imperative mood. Better: `Add input validation to signup form`.
4. **Revoke** the password or key and create a new one. Removing it from the code isn't enough, because it stays in the history.
5. Safe for commits that only exist locally (not pushed). Unsafe for commits that others may already have.

### Checkpoint 3: How professionals learn
1. The first `at ...` line that points at **your** file (not `node:internal`), plus the file and line shown at the very top.
2. The file really doesn't exist yet, or the program was run from a different folder, so the relative path points elsewhere.
3. Reproduce → read the error → form a guess → test the guess → fix one thing → understand why.
4. The docs match the current version; tutorials go out of date and may show old APIs.

### Checkpoint 4: The journey of a request
1. The IP address identifies the **computer**; the port identifies the **program** on that computer.
2. Your own computer (`localhost` = 127.0.0.1), the program listening on port 3000.
3. DNS answers are cached for their TTL at many levels, so old answers stay around until they expire.
4. That data arrives completely and in the right order (or you get an error).
5. Reading (privacy), tampering (integrity) and impersonation (authenticity).
6. Keep-alive: the connection is reused, so DNS, TCP and TLS don't have to happen again. Cached files help too.

### Checkpoint 5: HTTP up close
1. An empty line (`\r\n\r\n` marks the end of the headers).
2. No. The fragment is only used by the browser.
3. `GET` is assumed to be safe: browsers, crawlers and caches may call it at any time, even prefetch it.
4. (a) 201 (b) 409 (c) 401 (d) 403 (e) 204.
5. A string: `"3"`.
6. The client sends proof (a cookie or token) with **every** request, and the server checks it every time.

### Checkpoint 6: Your HTTP toolkit
1. `>` lines are what you sent; `<` lines are what the server sent back.
2. The backend's. "Waiting for server response" (TTFB) is time the server spent working.
3. They're saved in the project, committed, shared with the team, and act as documentation.
4. TCP delivers data in chunks as it arrives; a big response arrives in several pieces.

### Checkpoint 7: Modern JavaScript
1. `"x"`. The property is missing, so the default is used.
2. `||` replaces `0` (a valid value) with `3`. Use `settings.retries ?? 3`.
3. (a) `filter` (b) `find` (c) `reduce` (d) `map`.
4. `[100, 25, 5]`, because the default sort compares values as **text**, and "1" comes before "2" and "5".
5. As the integer `249950` (cents or paisa).

### Checkpoint 8: TypeScript I
1. Types are erased at runtime; TypeScript only checks code you write, not data that arrives while the program runs.
2. Phone: `string`. Price: `number` in cents. Status: a union of string literals. Time zone: `string`.
3. `description?: string` may be missing (`string | undefined`); `description: string` must always be present.
4. `tags[0]` has type `string | undefined`, so you must check before using it.
5. When everything you import is a type. Types don't exist at runtime, so the import must be removed completely when the code runs.

### Checkpoint 9: TypeScript II
1. The shared tag field with a different literal value in each variant (like `method` or `ok`).
2. `Result` for expected failures the caller should handle; `throw` for unexpected problems and bugs.
3. A compile error at the `never` line, pointing at the switch that's missing a case.
4. `boolean`.
5. It can't include server-controlled fields like `id`, `createdAt` or an owner ID, so clients can't change them.
6. `any` turns checking off; `unknown` forces you to check the value before using it.

### Checkpoint 10: Node.js core
1. `process.cwd()` is the folder the command was run from; `import.meta.dirname` is the folder of the source file.
2. `process.exit` stops immediately and can cut off unfinished work, like writes still in progress.
3. Relative paths are resolved from `process.cwd()`. Build the path from `import.meta.dirname` instead.
4. If the program crashes mid-write, the old file is still intact; the rename swaps in the new file all at once.
5. `.env` holds real values (including secrets) and is never committed; `.env.example` lists the variable names with dummy values and **is** committed.
6. `npm install` may update the lock file within the allowed ranges; `npm ci` installs exactly what's in `package-lock.json`.

### Checkpoint 11: Async and the event loop
1. The waiter is your JavaScript (the single thread); the kitchen is the OS and background workers doing the I/O.
2. Promise callbacks are microtasks, and all microtasks run before the next task (timer).
3. A promise, always.
4. About 600 ms sequentially; about 300 ms (the slowest one) with `Promise.all`.
5. By default, Node crashes the whole process (an unhandled rejection).

### Checkpoint 12: Errors, debugging and streams
1. Only `Error` objects carry a stack trace showing where the problem happened.
2. It hides the problem completely: nothing is logged and nobody knows something failed.
3. "Slot already booked" is expected: return a clear `409` message. "Cannot read properties of undefined" is a bug: log it in full, return a generic `500`, then fix the code.
4. It only pauses when its condition is true.
5. `readFile` tries to load all 5 GB into memory at once; a stream only holds one small chunk at a time.

### Checkpoint 13: A server from scratch
1. Once for every request.
2. `Content-Length` is in bytes, and characters like `é` take more than one byte in UTF-8.
3. The body is a stream that can arrive in several chunks.
4. It waits until it times out.
5. After a delete, the next ID can repeat an existing one.

### Checkpoint 14: Express
1. A `string`. You must convert it (`Number(...)`) and validate it before use.
2. `req`, `res` and `next`.
3. The request hangs until the client times out.
4. Express tries handlers in order; the 404 handler should only run if nothing else matched.
5. So it logs every request, including ones that fail inside `express.json()` (like broken JSON).

### Checkpoint 15: Validation and errors
1. Any five of: presence, type, range, format, allowed values, cleanliness (trimming), unexpected fields.
2. `parse` throws on invalid data; `safeParse` returns `{ success, data }` or `{ success, error }`.
3. The runtime check and the type come from one definition, so they can never disagree.
4. Query strings and path parameters are always strings; coercion converts them before validating.
5. It has four parameters: `(err, req, res, next)`.
6. Clients can rely on a stable `code` in their logic, while the `message` can be reworded freely.

### Checkpoint 16: REST design
1. `POST /services`, `GET /staff/4`, `DELETE /bookings/:id`.
2. Once a resource has its own ID, clients shouldn't need the parent's ID to reach it, and URLs stay short.
3. `201 Created`, with a `Location` header pointing at the new resource.
4. So you can add pagination information later without breaking clients.
5. Cancelling has rules and side effects; an explicit action endpoint makes those clear and hard to bypass.
6. No. Clients ignore fields they don't know.

### Checkpoint 17: Project structure
1. The **service** layer (a business rule).
2. The **controller**.
3. Only the **repository** files.
4. So tests can build the app and send requests without starting a real server.
5. A change to one feature then touches one folder, which scales better as the project grows.
