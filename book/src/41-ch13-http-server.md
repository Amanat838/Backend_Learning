---
kind: chapter
num: 13
title: A Web Server From Scratch With node:http
phase: Phase 3
time: about 4 hours
---
In Chapter 6 you wrote an HTTP *client* that sent text over a socket. Now you'll build the other side: a server that receives requests and sends responses. You'll build it with nothing but Node's built-in `http` module, so that when you use Express in the next chapter, you'll know exactly what it's doing for you.

!!! learn "What you'll learn"
    - Creating a server and listening on a port
    - The request and response objects
    - Routing by hand
    - Sending JSON correctly
    - Reading a request body (a stream!)
    - Why frameworks exist

## 13.1 The smallest server

```ts
// ch13/src/hello.ts
import http from "node:http";

const server = http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8" });
  res.end("Hello from my own server!");
});

server.listen(3000, () => {
  console.log("Listening on http://localhost:3000");
});
```

```bash
node --watch src/hello.ts
```

Open `http://localhost:3000` in your browser, or run `curl -i localhost:3000` in another terminal:

```output
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Date: Sun, 25 Oct 2026 13:37:41 GMT
Connection: keep-alive
Keep-Alive: timeout=5
Transfer-Encoding: chunked

Hello from my own server!
```

That's the same text format you parsed by hand in Chapter 6, and now **you** are producing it.

- `http.createServer(handler)` creates a server. The handler runs **once for every request**.
- `server.listen(3000)` starts listening on port 3000. The program keeps running, waiting for requests, until you press <kbd>Ctrl</kbd>+<kbd>C</kbd>.
- `--watch` restarts the server whenever you save a file.

!!! warning "EADDRINUSE"
    `Error: listen EADDRINUSE: address already in use :::3000` means another program, usually an old copy of your server in another terminal, is already using the port. Stop it with <kbd>Ctrl</kbd>+<kbd>C</kbd>, or pick another port.

## 13.2 The request and the response

The handler receives two objects:

| `req` (the request: `IncomingMessage`) | |
|---|---|
| `req.method` | `"GET"`, `"POST"`... |
| `req.url` | The path and query: `"/books?author=martin"` |
| `req.headers` | An object of headers, **names in lowercase**: `req.headers["content-type"]` |
| The body | `req` is a **readable stream**. You read the body from it (section 13.5). |

| `res` (the response: `ServerResponse`) | |
|---|---|
| `res.writeHead(status, headers)` | Set the status code and headers |
| `res.setHeader(name, value)` | Set one header |
| `res.end(body)` | Send the body and finish the response |
| | `res` is a **writable stream**. |

!!! mistake "Forgetting `res.end()`"
    If a code path never calls `res.end()`, the client just waits, and waits, until it times out. Every possible path through your handler must end the response exactly once.

## 13.3 Routing by hand

**Routing** means choosing which code runs based on the method and the path:

```ts
const server = http.createServer((req, res) => {
  const url = new URL(req.url ?? "/", `http://${req.headers.host}`);

  if (req.method === "GET" && url.pathname === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify({ status: "ok" }));
  }

  if (req.method === "GET" && url.pathname === "/time") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify({ now: new Date().toISOString() }));
  }

  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: `Cannot ${req.method} ${url.pathname}` }));
});
```

`new URL(...)` parses the path and query for you. `req.url` is only the path, so you give `URL` a base to make it a full address. Then `url.pathname` is `/time`, and `url.searchParams.get("author")` reads query parameters.

For paths with an ID, like `/books/42`, a regular expression extracts the number:

```ts
const match = url.pathname.match(/^\/books\/(\d+)$/);
if (req.method === "GET" && match) {
  const id = Number(match[1]);   // "42" → 42
  // ...
}
```

## 13.4 Sending JSON properly

Every JSON response needs the right headers. A small helper avoids repeating yourself:

```ts
function sendJson(res: http.ServerResponse, status: number, data: unknown): void {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
  });
  res.end(body);
}
```

!!! warning "Length is measured in bytes, not characters"
    `"café".length` is 4, but in UTF-8 it takes **5 bytes**, because `é` needs two. `Content-Length` must count bytes, which is why the helper uses `Buffer.byteLength(body)` and not `body.length`. Get it wrong and clients cut off the end of your response, or hang waiting for bytes that never come.

## 13.5 Reading the request body

For a `POST`, the data arrives in the request body. Since `req` is a stream, the body can arrive in several chunks (like the socket in Chapter 6), so you collect them all:

```ts
async function readBody(req: http.IncomingMessage): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString("utf8");
}
```

Then parse it, and **never trust it**:

```ts
const raw = await readBody(req);
let data: unknown;
try {
  data = JSON.parse(raw);
} catch {
  return sendJson(res, 400, { error: "Body must be valid JSON" });
}
// data is unknown: check it before using it (Chapter 9!)
```

## 13.6 A complete little API

Here's a full in-memory books API with no framework. Type it in (`ch13/src/books-raw.ts`) and run it: every line uses something from this chapter.

```ts
import http from "node:http";

type Book = { id: number; title: string; author: string };

const books: Book[] = [
  { id: 1, title: "Clean Code", author: "Robert C. Martin" },
  { id: 2, title: "Designing Data-Intensive Applications", author: "Martin Kleppmann" },
];

function sendJson(res: http.ServerResponse, status: number, data: unknown): void {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
  });
  res.end(body);
}

async function readBody(req: http.IncomingMessage): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString("utf8");
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url ?? "/", `http://${req.headers.host}`);
  console.log(req.method, url.pathname);

  if (req.method === "GET" && url.pathname === "/books") {
    return sendJson(res, 200, books);
  }

  const match = url.pathname.match(/^\/books\/(\d+)$/);
  if (req.method === "GET" && match) {
    const id = Number(match[1]);
    const book = books.find((b) => b.id === id);
    if (!book) return sendJson(res, 404, { error: "Book not found" });
    return sendJson(res, 200, book);
  }

  if (req.method === "POST" && url.pathname === "/books") {
    const raw = await readBody(req);
    let data: unknown;
    try {
      data = JSON.parse(raw);
    } catch {
      return sendJson(res, 400, { error: "Body must be valid JSON" });
    }
    if (typeof data !== "object" || data === null || !("title" in data) || typeof data.title !== "string" ||
        !("author" in data) || typeof data.author !== "string") {
      return sendJson(res, 400, { error: "title and author are required strings" });
    }
    const book: Book = { id: books.length + 1, title: data.title, author: data.author };
    books.push(book);
    return sendJson(res, 201, book);
  }

  sendJson(res, 404, { error: `Cannot ${req.method} ${url.pathname}` });
});

server.listen(3000, () => {
  console.log("Server listening on http://localhost:3000");
});
```

Real results from running it:

```bash
curl -s localhost:3000/books/2
curl -s -X POST localhost:3000/books -d '{"title":"Refactoring","author":"Martin Fowler"}'
curl -s -X POST localhost:3000/books -d '{bad'
curl -s -X POST localhost:3000/books -d '{"title":5}'
curl -s localhost:3000/nope
```

```output
{"id":2,"title":"Designing Data-Intensive Applications","author":"Martin Kleppmann"}
{"id":3,"title":"Refactoring","author":"Martin Fowler"}
{"error":"Body must be valid JSON"}
{"error":"title and author are required strings"}
{"error":"Cannot GET /nope"}
```

!!! mistake "`books.length + 1` as an ID"
    It looks fine until you delete a book: with books 1, 2, 3, delete #2, and the next new book gets id `3`, a duplicate! Keep a separate counter (`let nextId = 3; nextId++`), or use random IDs like `crypto.randomUUID()`. You'll fix this in a task.

## 13.7 Why frameworks exist

Look at what you had to do by hand:

- Match methods and paths with `if`s and regular expressions.
- Read and parse the body for every `POST`.
- Repeat the JSON headers everywhere (or write a helper).
- Validate data with long chains of checks.
- Handle errors in each route separately, and remember to end every response.

With 5 routes that's fine. With 50, it's a mess. A framework like Express handles routing, body parsing and errors in one place, so you can focus on your actual logic. Underneath, it's doing exactly what you just did, using this same `http` module.

!!! interview "Interview corner"
    "What does a web framework actually do for you?" Now you can answer from experience: routing, body parsing, a middleware pipeline for shared logic (logging, auth), and centralised error handling, all on top of Node's `http` module.

!!! checkpoint "Checkpoint 13"
    1. How many times does the `createServer` handler run?
    2. Why must `Content-Length` use `Buffer.byteLength` instead of `string.length`?
    3. Why is the request body read with `for await`?
    4. What happens to a client if your handler never calls `res.end()`?
    5. Why is `books.length + 1` a bad ID generator?

## Tasks

!!! task "Task 13.1 · Hello server · Core"
    In `ch13/src/server.ts`, build a server with:

    - `GET /` → plain text `Welcome to my server`
    - `GET /health` → `{"status":"ok","uptime":12.3}`
    - `GET /time` → `{"now":"<ISO timestamp>"}`
    - `GET /greet?name=Ali` → `{"message":"Hello, Ali!"}` (`name` defaults to `stranger`)
    - anything else → status `404` with `{"error":"Cannot <METHOD> <path>"}`

    **Done when:** all five work with `curl -i` and show the right status codes and `Content-Type` headers. {: .done }

!!! task "Task 13.2 · A raw notes API · Core"
    In `ch13/src/notes.ts`, build an in-memory API for notes `{ id: number; text: string; pinned: boolean; createdAt: string }`:

    | Request | Success |
    |---|---|
    | `GET /notes` | `200` with all notes |
    | `GET /notes/:id` | `200` with one note, or `404` |
    | `POST /notes` with `{"text":"...","pinned":false}` | `201` with the new note |
    | `DELETE /notes/:id` | `204` with no body, or `404` |

    Validate the body: `text` is a non-empty string; `pinned` is optional and defaults to `false`. Invalid JSON or data → `400`. IDs must never repeat, even after deletes.

    Write `ch13/requests.http` with at least one request for each success and each error case.

    **Done when:** every request in your `.http` file returns the status you expect. {: .done }

!!! task "Task 13.3 · Search and update · Core"
    Extend the notes API:

    - `GET /notes?search=milk` returns only notes whose text contains the word (case-insensitive).
    - `GET /notes?pinned=true` returns only pinned notes.
    - `PATCH /notes/:id` with `{"text":"..."}` and/or `{"pinned":true}` updates only those fields.

!!! task "Task 13.4 · Defensive server · Stretch"
    1. Log every request as `GET /notes 200 3ms` (hint: listen for `res.on("finish", ...)`).
    2. Reject bodies larger than 10 KB with `413 Payload Too Large`, by counting bytes while reading the stream.
    3. Respond to `POST` requests whose `Content-Type` isn't `application/json` with `415 Unsupported Media Type`.
