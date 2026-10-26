---
kind: chapter
num: 14
title: "Express: Routing and Middleware"
phase: Phase 3
time: about 4 hours
---
Express is the most widely used web framework for Node.js. It's small: it gives you routing, a clean way to read requests and send responses, and **middleware**, the idea that will shape how you think about servers. This chapter rebuilds the books API with Express, then shows what still goes wrong without validation.

!!! learn "What you'll learn"
    - Setting up an Express 5 app with TypeScript
    - Routes, path parameters and query strings
    - Reading JSON bodies
    - Middleware and the request pipeline
    - Routers for grouping routes
    - What Express does *not* protect you from

## 14.1 Setup

```bash
mkdir ch14 && cd ch14
npm init -y
npm install express
npm install -D typescript @types/node @types/express
npm pkg set type=module scripts.dev="node --watch src/server.ts" scripts.check="tsc --noEmit"
```

Copy your `tsconfig.json` from Chapter 8. `npm install express` installs **Express 5**, the current version.

!!! warning "Old tutorials use Express 4"
    Most tutorials online were written for Express 4. Two differences matter:

    1. **Express 5 catches errors in `async` handlers** and passes them to your error handler. Express 4 didn't, so old code wraps everything in `try`/`catch` or helper functions.
    2. **Path patterns changed.** `app.get("*", ...)` no longer works. A catch-all needs a name, like `"/*splat"`, or (better) use `app.use(...)` at the end for "not found" handling.

## 14.2 Your first Express app

```ts
// ch14/src/server.ts
import express from "express";

type Book = { id: number; title: string; author: string };
const books: Book[] = [{ id: 1, title: "Clean Code", author: "Robert C. Martin" }];
let nextId = 2;

const app = express();
app.use(express.json());   // parse JSON bodies into req.body

app.get("/books", (req, res) => {
  const author = req.query.author;            // /books?author=martin
  if (typeof author === "string") {
    return res.json(books.filter((b) => b.author.toLowerCase().includes(author.toLowerCase())));
  }
  res.json(books);
});

app.get("/books/:id", (req, res) => {
  const id = Number(req.params.id);
  const book = books.find((b) => b.id === id);
  if (!book) {
    return res.status(404).json({ error: "Book not found" });
  }
  res.json(book);
});

app.post("/books", (req, res) => {
  const { title, author } = req.body;
  const book: Book = { id: nextId++, title, author };
  books.push(book);
  res.status(201).json(book);
});

app.delete("/books/:id", (req, res) => {
  const index = books.findIndex((b) => b.id === Number(req.params.id));
  if (index === -1) return res.status(404).json({ error: "Book not found" });
  books.splice(index, 1);
  res.status(204).end();
});

app.listen(3000, () => console.log("Listening on http://localhost:3000"));
```

Compare this with Chapter 13: no `if` chains, no regular expressions, no manual body reading, no JSON headers. The same API in half the code.

### The everyday API

| Code | Meaning |
|---|---|
| `app.get(path, handler)` | Handle `GET` requests to `path` (also `post`, `put`, `patch`, `delete`) |
| `"/books/:id"` | A **path parameter**: `/books/42` gives `req.params.id === "42"` (a string!) |
| `req.query` | Parsed query string: `/books?author=martin` gives `req.query.author === "martin"` |
| `req.body` | The parsed JSON body (needs `express.json()`) |
| `req.headers` | Request headers, lowercase names |
| `res.json(data)` | Send JSON with the right headers (status 200 by default) |
| `res.status(201)` | Set the status code; chain it: `res.status(201).json(book)` |
| `res.status(204).end()` | Send no body |
| `res.location(url)` | Set the `Location` header |

!!! warning "Params and query values are strings"
    `req.params.id` is `"42"`, not `42`. `req.query.page` is `"2"`, or an array if the client sent `?page=1&page=2`, or `undefined`. Always convert and validate them. Chapter 15 does it properly.

## 14.3 Middleware: the request pipeline

**Middleware** is a function that runs *before* your route handler (or instead of it). Every request flows through a chain of middleware, in the order you registered them:

<figure>
<svg viewBox="0 0 700 170" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, sans-serif" font-size="12">
  <defs><marker id="m1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#3b5bdb"/></marker>
  <marker id="m2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#d6336c"/></marker></defs>
  <text x="18" y="62" font-weight="700" fill="#1d2433">Request</text>
  <g text-anchor="middle">
    <rect x="80" y="35" width="105" height="48" rx="7" fill="#f0f4ff" stroke="#3b5bdb"/><text x="132" y="56" font-weight="700" fill="#1d2433">logger</text><text x="132" y="72" font-size="10.5" fill="#4a5468">start a timer</text>
    <rect x="215" y="35" width="105" height="48" rx="7" fill="#f0f4ff" stroke="#3b5bdb"/><text x="267" y="56" font-weight="700" fill="#1d2433">express.json()</text><text x="267" y="72" font-size="10.5" fill="#4a5468">parse the body</text>
    <rect x="350" y="35" width="105" height="48" rx="7" fill="#f0f4ff" stroke="#3b5bdb"/><text x="402" y="56" font-weight="700" fill="#1d2433">requireApiKey</text><text x="402" y="72" font-size="10.5" fill="#4a5468">allowed?</text>
    <rect x="485" y="35" width="105" height="48" rx="7" fill="#effaf1" stroke="#2b8a3e"/><text x="537" y="56" font-weight="700" fill="#1d2433">route handler</text><text x="537" y="72" font-size="10.5" fill="#4a5468">your logic</text>
  </g>
  <text x="612" y="62" font-weight="700" fill="#1d2433">Response</text>
  <g stroke="#3b5bdb" stroke-width="1.8" marker-end="url(#m1)"><line x1="70" y1="59" x2="77" y2="59"/><line x1="187" y1="59" x2="212" y2="59"/><line x1="322" y1="59" x2="347" y2="59"/><line x1="457" y1="59" x2="482" y2="59"/><line x1="592" y1="59" x2="608" y2="59"/></g>
  <g font-family="Cascadia Mono, Consolas, monospace" font-size="10.5" fill="#22348c" text-anchor="middle"><text x="200" y="28">next()</text><text x="335" y="28">next()</text><text x="470" y="28">next()</text></g>
  <path d="M402,85 C402,130 402,130 470,138" stroke="#d6336c" stroke-width="1.6" fill="none" stroke-dasharray="4 3" marker-end="url(#m2)"/>
  <text x="478" y="142" fill="#d6336c" font-size="11.5">no key → res.status(401) and stop here</text>
</svg>
<figcaption>Each middleware either calls next() to pass the request on, or sends a response itself and ends the chain.</figcaption>
</figure>

!!! analogy "Analogy: airport security"
    Before you reach your gate (the route handler), you pass checkpoints in order: ticket check, ID check, bag scan. Each checkpoint either waves you through ("next!") or stops you right there. Middleware is the same: each one either calls `next()` or ends the request with a response.

A middleware function receives `req`, `res` and `next`:

```ts
import type { Request, Response, NextFunction } from "express";

function logger(req: Request, res: Response, next: NextFunction): void {
  const start = Date.now();
  res.on("finish", () => {   // runs after the response has been sent
    console.log(`${req.method} ${req.originalUrl} ${res.statusCode} ${Date.now() - start}ms`);
  });
  next();                    // pass the request along
}

app.use(logger);             // run for EVERY request
```

```output
GET /books 200 6ms
GET /books?author=robert 200 1ms
GET /books/5 404 1ms
POST /books 201 0ms
DELETE /books/1 204 1ms
```

A middleware can also **stop** the request:

```ts
function requireApiKey(req: Request, res: Response, next: NextFunction) {
  if (req.headers["x-api-key"] !== process.env.API_KEY) {
    return res.status(401).json({ error: "Missing or invalid API key" });
  }
  next();
}

app.post("/books", requireApiKey, (req, res) => { /* ... */ });   // only on this route
```

!!! idea "Order matters"
    Middleware runs in the order you `use` it. `express.json()` must come **before** any route that reads `req.body`. A logger should come **first**, so it sees every request, even ones that fail later. The "not found" handler must come **last**, after all routes.

!!! mistake "Forgetting `next()`"
    A middleware that neither calls `next()` nor sends a response leaves the request hanging forever, just like forgetting `res.end()` in Chapter 13.

## 14.4 Routers: grouping related routes

As an API grows, put each resource's routes in its own file with `express.Router()`:

```ts
// src/books.routes.ts
import { Router } from "express";

export const booksRouter = Router();

booksRouter.get("/", (req, res) => { /* list */ });
booksRouter.get("/:id", (req, res) => { /* get one */ });
booksRouter.post("/", (req, res) => { /* create */ });
```

```ts
// src/server.ts
import { booksRouter } from "./books.routes.ts";
app.use("/books", booksRouter);   // "/" in the router becomes "/books"
```

## 14.5 Handling "not found"

Put a final middleware **after all your routes**. If a request reaches it, nothing else matched:

```ts
app.use((req, res) => {
  res.status(404).json({ error: `Cannot ${req.method} ${req.originalUrl}` });
});
```

## 14.6 What Express does *not* do for you

Express made routing easy. But try sending it bad data. Here are real results from the app in section 14.2:

**1. It accepts garbage.** A body with no title or author:

```bash
curl -s -X POST localhost:3000/books -H "Content-Type: application/json" -d '{"price":5}'
```

```output
{"id":3}     ← status 201 Created! A "book" with no title and no author.
```

**2. Broken JSON returns an HTML page with a stack trace:**

```output
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Error</title></head>
<body>
<pre>SyntaxError: Expected property name or '}' in JSON at position 1 ...<br>
 &nbsp; &nbsp;at JSON.parse (&lt;anonymous&gt;)<br>
 &nbsp; &nbsp;at parse (C:\Users\...\node_modules\body-parser\lib\types\json.js:93:21)
```

An API client expects JSON, not HTML. And it reveals file paths on your server to anyone who sends a broken request.

**3. A missing `Content-Type` crashes the handler.** Without `Content-Type: application/json`, `express.json()` skips the body, so `req.body` is `undefined`, and destructuring it throws:

```output
TypeError: Cannot destructure property 'title' of 'req.body' as it is undefined.
```

The client gets a `500`, plus another HTML stack-trace page.

!!! idea "Why this matters"
    `req.body` is typed as `any`, so TypeScript can't help. Chapter 8 warned you: types are erased at runtime, and request data comes from strangers. Chapter 15 fixes all three problems: **validation** with Zod and **one central error handler** that always returns clean JSON.

!!! checkpoint "Checkpoint 14"
    1. What's the type of `req.params.id`, and why does that matter?
    2. What are the three things a middleware function receives?
    3. A middleware does neither `next()` nor `res.send()`. What happens?
    4. Why must the 404 handler be registered last?
    5. Why should the logger be registered before `express.json()`?

## Tasks

!!! task "Task 14.1 · Port the notes API · Core"
    Rebuild your Chapter 13 notes API (all routes, including search, `pinned` filtering and `PATCH`) with Express in `ch14/`. Reuse your `requests.http` file. The behaviour must be the same.

    **Done when:** every request in the `.http` file gives the same result as your raw version, in noticeably less code. {: .done }

!!! task "Task 14.2 · Logging middleware · Core"
    Write `src/middleware/logger.ts` that logs `METHOD path → status (duration ms)` for every request, using `res.on("finish")` and `performance.now()` for precise timing. Register it first.

!!! task "Task 14.3 · Protect the write routes · Core"
    Write `requireApiKey` middleware that checks the `x-api-key` header against `process.env.API_KEY` (loaded with `--env-file`). Apply it to `POST`, `PATCH` and `DELETE`, but not to the `GET` routes. Missing or wrong key → `401` with a JSON error. Add both cases to `requests.http`.

!!! task "Task 14.4 · Routers · Core"
    Move the notes routes into `src/notes.routes.ts` using `Router()`, and mount them at `/notes`. Add a `GET /health` route in `server.ts` and a final JSON 404 handler.

!!! task "Task 14.5 · Request IDs · Stretch"
    Write middleware that gives every request a unique ID (`crypto.randomUUID()`), sends it back in an `X-Request-Id` response header, and includes it in the log line. When something breaks in production, this ID lets you find every log line for one specific request.
