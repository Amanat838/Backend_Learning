---
kind: chapter
num: 17
title: Structuring a Real Project
phase: Phase 3
time: about 4–5 hours
---
Putting every route, check and data access in one `server.ts` works for 100 lines. At 2,000 lines it's a swamp where every change breaks something else. Real teams split code into **layers** with clear jobs. This chapter walks through a complete, layered Books API (the structure your URL Shortener and Slotify will follow) file by file.

!!! learn "What you'll learn"
    - Why layers exist
    - Routes, controllers, services, repositories
    - Organising folders by feature
    - Separating the app from the server
    - Configuration and health checks
    - A README that impresses reviewers

## 17.1 The restaurant again

!!! analogy "Analogy: a well-run restaurant"
    - The **waiter** takes your order, checks it makes sense ("we don't serve breakfast after noon"), and brings the food back. They don't cook.
    - The **chef** knows the recipes and the rules of the kitchen. They don't talk to customers.
    - The **storeroom keeper** fetches and stores ingredients. They don't care what's being cooked.

    Each person has one job. The chef can change a recipe without retraining the waiters. You can reorganise the storeroom without the chef noticing.

That's exactly how a backend is layered:

<figure>
<svg viewBox="0 0 700 270" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, sans-serif" font-size="12">
  <defs><marker id="l1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#3b5bdb"/></marker></defs>
  <g>
    <rect x="30" y="12" width="400" height="44" rx="7" fill="#f3f4f7" stroke="#9aa3b5"/>
    <text x="50" y="39" font-weight="700" fill="#1d2433">Routes + middleware</text><text x="215" y="39" fill="#4a5468">URL → handler, validation, auth</text>
    <rect x="30" y="76" width="400" height="44" rx="7" fill="#f0f4ff" stroke="#3b5bdb"/>
    <text x="50" y="103" font-weight="700" fill="#1d2433">Controller</text><text x="215" y="103" fill="#4a5468">read req → call service → send res</text>
    <rect x="30" y="140" width="400" height="44" rx="7" fill="#effaf1" stroke="#2b8a3e"/>
    <text x="50" y="167" font-weight="700" fill="#1d2433">Service</text><text x="215" y="167" fill="#4a5468">business rules (no HTTP here!)</text>
    <rect x="30" y="204" width="400" height="44" rx="7" fill="#fff8eb" stroke="#c77700"/>
    <text x="50" y="231" font-weight="700" fill="#1d2433">Repository</text><text x="215" y="231" fill="#4a5468">store and fetch data</text>
  </g>
  <g stroke="#3b5bdb" stroke-width="1.8" marker-end="url(#l1)"><line x1="230" y1="57" x2="230" y2="73"/><line x1="230" y1="121" x2="230" y2="137"/><line x1="230" y1="185" x2="230" y2="201"/></g>
  <g font-size="11.5" fill="#4a5468">
    <text x="455" y="39">waiter at the door</text>
    <text x="455" y="103">waiter</text>
    <text x="455" y="167">chef</text>
    <text x="455" y="231">storeroom: a Map today,</text>
    <text x="455" y="246">PostgreSQL in Book 2</text>
  </g>
</svg>
<figcaption>Each layer only calls the layer directly below it. Dependencies point downwards.</figcaption>
</figure>

| Layer | Its job | Knows about HTTP? | Example |
|---|---|---|---|
| **Routes** | Map method + path to a handler; attach middleware | Yes | `router.post("/", validateBody(schema), controller.create)` |
| **Controller** | Take what it needs from `req`, call the service, send the response | Yes | `res.status(201).json(book)` |
| **Service** | Business rules: "titles must be unique", "can't book a taken slot" | **No** | `throw new ConflictError(...)` |
| **Repository** | Save and load data | **No** | `books.set(id, book)` |

!!! idea "Why the service must not know about HTTP"
    A service that never touches `req` or `res` can be reused from anywhere: an HTTP route today, a background job or a command-line script tomorrow, and an automated test in Phase 6. And when you swap the in-memory `Map` for PostgreSQL in Book 2, **only the repository changes**.

## 17.2 Organise folders by feature

```text
books-api/
├── src/
│   ├── modules/
│   │   └── books/
│   │       ├── book.schemas.ts      ← Zod schemas + types
│   │       ├── book.repository.ts   ← data access
│   │       ├── book.service.ts      ← business rules
│   │       ├── book.controller.ts   ← HTTP in, HTTP out
│   │       └── book.routes.ts       ← URL → controller
│   ├── middleware/
│   │   ├── request-logger.ts
│   │   ├── validate.ts
│   │   └── error-handler.ts
│   ├── lib/
│   │   └── errors.ts
│   ├── config.ts
│   ├── app.ts                       ← builds the Express app
│   └── server.ts                    ← starts listening
├── requests.http
├── .env.example
├── package.json
├── tsconfig.json
└── README.md
```

Everything about books lives in one folder. When you add authors, you add `modules/authors/` with the same five files. Grouping **by feature** (books, authors) scales much better than grouping **by type** (all controllers in one folder, all services in another), because a change to one feature touches one folder.

## 17.3 The files, one by one

### Schemas: the shape of the data

```ts
// src/modules/books/book.schemas.ts
import { z } from "zod";

export const genreSchema = z.enum(["fiction", "non-fiction", "tech"]);

export const createBookSchema = z.object({
  title: z.string().trim().min(1, "title is required").max(200),
  author: z.string().trim().min(1, "author is required"),
  year: z.number().int().min(1450).max(new Date().getFullYear()),
  genre: genreSchema,
});

export const updateBookSchema = createBookSchema.partial();

export const listBooksQuerySchema = z.object({
  genre: genreSchema.optional(),
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(50).default(10),
});

export type CreateBookInput = z.infer<typeof createBookSchema>;
export type UpdateBookInput = z.infer<typeof updateBookSchema>;
export type ListBooksQuery = z.infer<typeof listBooksQuerySchema>;

export type Book = CreateBookInput & {
  id: string;
  createdAt: string;
};
```

`Book` is built from the create input plus server-generated fields, using `&` (an **intersection** type: "all the fields of both").

### Repository: the only code that touches storage

```ts
// src/modules/books/book.repository.ts
import type { Book } from "./book.schemas.ts";

// For now the "database" is a Map in memory. In Book 2 this file is the
// only one that changes when we switch to PostgreSQL.
const books = new Map<string, Book>();

export const bookRepository = {
  findAll(): Book[] {
    return [...books.values()];
  },
  findById(id: string): Book | undefined {
    return books.get(id);
  },
  findByTitle(title: string): Book | undefined {
    return [...books.values()].find((b) => b.title.toLowerCase() === title.toLowerCase());
  },
  save(book: Book): Book {
    books.set(book.id, book);
    return book;
  },
  delete(id: string): boolean {
    return books.delete(id);
  },
};
```

### Service: the business rules

```ts
// src/modules/books/book.service.ts
import { randomUUID } from "node:crypto";
import { ConflictError, NotFoundError } from "../../lib/errors.ts";
import { bookRepository } from "./book.repository.ts";
import type { Book, CreateBookInput, ListBooksQuery, UpdateBookInput } from "./book.schemas.ts";

export type Page<T> = { items: T[]; page: number; pageSize: number; total: number; totalPages: number };

export const bookService = {
  list(query: ListBooksQuery): Page<Book> {
    const all = bookRepository
      .findAll()
      .filter((b) => (query.genre ? b.genre === query.genre : true));
    const start = (query.page - 1) * query.pageSize;
    return {
      items: all.slice(start, start + query.pageSize),
      page: query.page,
      pageSize: query.pageSize,
      total: all.length,
      totalPages: Math.ceil(all.length / query.pageSize),
    };
  },

  get(id: string): Book {
    const book = bookRepository.findById(id);
    if (!book) throw new NotFoundError("Book", id);
    return book;
  },

  create(input: CreateBookInput): Book {
    if (bookRepository.findByTitle(input.title)) {
      throw new ConflictError(`A book titled '${input.title}' already exists`);
    }
    const book: Book = { ...input, id: randomUUID(), createdAt: new Date().toISOString() };
    return bookRepository.save(book);
  },

  update(id: string, patch: UpdateBookInput): Book {
    const existing = bookService.get(id);
    const updated: Book = { ...existing, ...patch };
    return bookRepository.save(updated);
  },

  remove(id: string): void {
    const deleted = bookRepository.delete(id);
    if (!deleted) throw new NotFoundError("Book", id);
  },
};
```

Notice: no `req`, no `res`, no status codes, just rules and errors. `randomUUID()` (built into Node) creates IDs like `ecabc0d4-c371-490f-98df-fdc50f116ec8`, which never repeat, so the `books.length + 1` bug from Chapter 13 can't happen.

### Controller: translate between HTTP and the service

```ts
// src/modules/books/book.controller.ts
import type { Request, Response } from "express";
import { parseQuery } from "../../middleware/validate.ts";
import { listBooksQuerySchema } from "./book.schemas.ts";
import { bookService } from "./book.service.ts";

type IdParams = { id: string };

export const bookController = {
  list(req: Request, res: Response) {
    const query = parseQuery(listBooksQuerySchema, req.query);
    res.json(bookService.list(query));
  },

  get(req: Request<IdParams>, res: Response) {
    res.json(bookService.get(req.params.id));
  },

  create(req: Request, res: Response) {
    const book = bookService.create(req.body);
    res.status(201).location(`/v1/books/${book.id}`).json(book);
  },

  update(req: Request<IdParams>, res: Response) {
    res.json(bookService.update(req.params.id, req.body));
  },

  remove(req: Request<IdParams>, res: Response) {
    bookService.remove(req.params.id);
    res.status(204).end();
  },
};
```

Controllers stay **thin**: a few lines each. `Request<IdParams>` tells TypeScript that `req.params.id` exists and is a string.

### Routes: the map

```ts
// src/modules/books/book.routes.ts
import { Router } from "express";
import { validateBody } from "../../middleware/validate.ts";
import { bookController } from "./book.controller.ts";
import { createBookSchema, updateBookSchema } from "./book.schemas.ts";

export const bookRouter = Router();

bookRouter.get("/", bookController.list);
bookRouter.get("/:id", bookController.get);
bookRouter.post("/", validateBody(createBookSchema), bookController.create);
bookRouter.patch("/:id", validateBody(updateBookSchema), bookController.update);
bookRouter.delete("/:id", bookController.remove);
```

You can read the whole API surface of a feature in five lines.

### Config: validated once, at startup

```ts
// src/config.ts
const port = Number(process.env.PORT ?? 3000);

if (!Number.isInteger(port) || port <= 0) {
  throw new Error(`PORT must be a positive whole number, got "${process.env.PORT}"`);
}

export const config = {
  port,
  nodeEnv: process.env.NODE_ENV ?? "development",
};
```

### App and server: two separate files

```ts
// src/app.ts
import express from "express";
import { errorHandler, notFoundHandler } from "./middleware/error-handler.ts";
import { requestLogger } from "./middleware/request-logger.ts";
import { bookRouter } from "./modules/books/book.routes.ts";

export function createApp() {
  const app = express();

  app.use(requestLogger);   // first, so it sees every request, even broken ones
  app.use(express.json());

  app.get("/health", (_req, res) => {
    res.json({ status: "ok", uptime: process.uptime() });
  });
  app.use("/v1/books", bookRouter);

  app.use(notFoundHandler); // no route matched
  app.use(errorHandler);    // something threw
  return app;
}
```

```ts
// src/server.ts
import { createApp } from "./app.ts";
import { config } from "./config.ts";

const app = createApp();

app.listen(config.port, () => {
  console.log(`Books API running on http://localhost:${config.port} (${config.nodeEnv})`);
});
```

**Why separate them?** `createApp()` builds the app without starting a server. In Phase 6, your automated tests will call `createApp()` and send requests to it directly, with no real port and no running server. Only `server.ts` actually listens.

### The request logger

```ts
// src/middleware/request-logger.ts
import type { Request, Response, NextFunction } from "express";

export function requestLogger(req: Request, res: Response, next: NextFunction) {
  const start = performance.now();
  res.on("finish", () => {
    const ms = (performance.now() - start).toFixed(1);
    console.log(`${req.method} ${req.originalUrl} -> ${res.statusCode} (${ms} ms)`);
  });
  next();
}
```

`validate.ts`, `error-handler.ts` and `lib/errors.ts` are exactly as in Chapter 15.

## 17.4 It works: real output

```output
Books API running on http://localhost:3001 (development)
GET /health -> 200 (4.4 ms)
POST /v1/books -> 201 (3.0 ms)
GET /v1/books -> 200 (2.5 ms)
POST /v1/books -> 409 (0.9 ms)
POST /v1/books -> 400 (1.5 ms)
GET /v1/books?page=0 -> 400 (0.9 ms)
GET /v1/books?genre=tech&pageSize=5 -> 200 (0.8 ms)
PATCH /v1/books/ecabc0d4-c371-490f-98df-fdc50f116ec8 -> 200 (1.3 ms)
GET /v1/books/nope -> 404 (0.8 ms)
DELETE /v1/books/ecabc0d4-c371-490f-98df-fdc50f116ec8 -> 204 (0.9 ms)
DELETE /v1/books/ecabc0d4-c371-490f-98df-fdc50f116ec8 -> 404 (0.6 ms)
GET /v2/whatever -> 404 (0.5 ms)
```

Every status code is the one Chapter 16's table says it should be.

## 17.5 A README that impresses reviewers

Recruiters and reviewers often read the README **before** (or instead of) the code. A strong API README has:

```markdown
# Books API

A REST API for managing a book catalogue, built with Node.js, TypeScript, Express 5 and Zod.

## Features
- CRUD for books with validation and consistent JSON errors
- Pagination and filtering
- Layered architecture (routes → controllers → services → repositories)

## Getting started
    npm install
    cp .env.example .env
    npm run dev

## API
| Method | Path | Description | Success |
|---|---|---|---|
| GET | /v1/books | List books (`genre`, `page`, `pageSize`) | 200 |
| ... |

## Error format
    { "error": { "code": "NOT_FOUND", "message": "...", "details": [] } }

## Project structure
(short folder tree, with one line per folder)

## What I learned / design decisions
- Why services don't know about HTTP
- Why IDs are UUIDs
```

The last section matters most. It shows you **think** about your code, not just write it.

!!! checkpoint "Checkpoint 17"
    1. Which layer should contain "a staff member can't be booked twice at the same time"?
    2. Which layer reads `req.params`?
    3. When you move from a `Map` to PostgreSQL, which files change?
    4. Why is `createApp()` separate from `app.listen()`?
    5. Why group files by feature rather than by type?

## Tasks

!!! task "Task 17.1 · Layer the notes API · Core"
    Restructure your notes API into the layout from section 17.2: `modules/notes/` with schemas, repository, service, controller and routes; shared middleware; `lib/errors.ts`; `config.ts`; `app.ts` and `server.ts`. Switch IDs to `randomUUID()`.

    **Done when:** every request in `requests.http` still behaves exactly as before, `npm run check` passes, and no service file imports anything from `express`. {: .done }

!!! task "Task 17.2 · A second module · Core"
    Add **notebooks**: `{ id, name, createdAt }` with the full CRUD routes under `/v1/notebooks`. Then give notes an optional `notebookId`:

    - Creating a note with a `notebookId` that doesn't exist → `422` with code `NOTEBOOK_NOT_FOUND` (the request is well-formed, but refers to something that doesn't exist).
    - `GET /v1/notebooks/:id/notes` lists that notebook's notes.
    - Deleting a notebook that still has notes → `409`.

    Which service is responsible for each of these rules? Write your reasoning in a comment.

!!! task "Task 17.3 · README · Core"
    Write a README for the notes API following section 17.5, including the endpoint table, the error format and three design decisions you made.

!!! task "Task 17.4 · Graceful shutdown · Stretch"
    When the server receives <kbd>Ctrl</kbd>+<kbd>C</kbd> (the `SIGINT` signal), log `Shutting down...`, stop accepting new connections with `server.close()`, and exit once open requests have finished. Real servers do this so that deploying a new version doesn't cut users off mid-request.
