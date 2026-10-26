---
kind: chapter
num: 15
title: Validation With Zod, and Error Handling
phase: Phase 3
time: about 5 hours
---
In Chapter 14 the API accepted a "book" with no title, returned HTML stack traces, and crashed on a missing header. This chapter fixes all of that with two tools every professional API needs: **validation** at the edge, and **one central error handler** that turns every problem into a clean, consistent JSON response.

!!! learn "What you'll learn"
    - What validation must check
    - Zod schemas, `safeParse` and error issues
    - One schema as the source of truth for types
    - Validation middleware
    - An error class hierarchy
    - A central error handler

## 15.1 Never trust the client

Anyone can send anything to your API: not just your own frontend, but curl, scripts, bots and attackers. Validation checks every piece of incoming data **at runtime**, before your logic touches it:

| Check | Example |
|---|---|
| Is it present? | `title` is required |
| Is it the right type? | `year` is a number, not `"2008"` |
| Is it in range? | `year` between 1450 and this year; `pageSize` at most 50 |
| Is the format right? | a valid email, URL or ISO date |
| Is it one of the allowed values? | `genre` is `fiction`, `non-fiction` or `tech` |
| Is it clean? | trim spaces: `"  Clean Code "` becomes `"Clean Code"` |
| Are there unexpected fields? | ignore or reject `{"isAdmin": true}` |

You wrote checks like this by hand in Chapter 9 (`parseUser`). It worked, but two fields took fifteen lines. **Zod** lets you describe the shape once and does the checking for you.

## 15.2 Zod basics

```bash
npm install zod
```

```ts
import { z } from "zod";

const createBookSchema = z.object({
  title: z.string().trim().min(1, "title is required").max(200),
  author: z.string().trim().min(1, "author is required"),
  year: z.number().int().min(1450).max(new Date().getFullYear()),
  genre: z.enum(["fiction", "non-fiction", "tech"]),
});
```

A **schema** describes what valid data looks like. To check data, use `safeParse`:

```ts
const result = createBookSchema.safeParse(data);

if (result.success) {
  result.data;            // the validated, cleaned data, fully typed
} else {
  result.error.issues;    // a list of everything that's wrong
}
```

There's also `.parse(data)`, which returns the data or **throws** a `ZodError`. In handlers, `safeParse` gives you more control.

### What the issues look like

For `{"title": "  ", "year": "2008", "genre": "poetry"}`, the real issues are:

```output
title   → title is required
author  → Invalid input: expected string, received undefined
year    → Invalid input: expected number, received string
genre   → Invalid option: expected one of "fiction"|"non-fiction"|"tech"
```

Each issue has a `path` (which field) and a `message`. Zod reports **all** the problems at once, so the client can fix everything in one go.

### The building blocks you'll use most

| Schema | Accepts |
|---|---|
| `z.string()` | any string. Add `.trim()`, `.min(1)`, `.max(200)`, `.regex(/.../)` |
| `z.number()` | any number. Add `.int()`, `.positive()`, `.min(0)`, `.max(100)` |
| `z.boolean()` | `true` or `false` |
| `z.enum(["a", "b"])` | one of these strings |
| `z.email()` | a valid email address |
| `z.url()` | a valid URL. `z.url({ protocol: /^https?$/ })` allows only http and https |
| `z.iso.datetime()` | an ISO timestamp like `"2026-11-03T09:30:00Z"` |
| `z.iso.date()` | a calendar date like `"2026-11-03"` (rejects `"2026-02-30"`) |
| `z.array(schema)` | an array of items matching the schema |
| `z.object({...})` | an object with these fields |
| `.optional()` | the field may be missing |
| `.default(x)` | if missing, use `x` |
| `.refine(fn, { message })` | your own rule |

```ts
const durationSchema = z
  .number()
  .int()
  .positive()
  .refine((n) => n % 15 === 0, { message: "must be a multiple of 15" });
```

!!! idea "Unknown fields are removed"
    By default, `z.object` **strips** fields it doesn't know. If an attacker sends `{"title": "x", ..., "isAdmin": true}`, `result.data` simply won't contain `isAdmin`. This prevents a classic security hole called **mass assignment**. Use `z.strictObject({...})` if you'd rather reject unknown fields with an error.

## 15.3 One source of truth for types

Here's the best part. Zod can produce the TypeScript type **from** the schema:

```ts
export type CreateBookInput = z.infer<typeof createBookSchema>;
// { title: string; author: string; year: number; genre: "fiction" | "non-fiction" | "tech" }
```

You describe the shape once. The runtime check and the compile-time type can never disagree, because they come from the same place.

For updates (`PATCH`), every field becomes optional:

```ts
export const updateBookSchema = createBookSchema.partial();
export type UpdateBookInput = z.infer<typeof updateBookSchema>;
```

### Query strings: coercion

Query values arrive as strings (`?page=2` gives `"2"`). `z.coerce.number()` converts them first, then validates:

```ts
export const listBooksQuerySchema = z.object({
  genre: z.enum(["fiction", "non-fiction", "tech"]).optional(),
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(50).default(10),
});

listBooksQuerySchema.parse({});              // { page: 1, pageSize: 10 }
listBooksQuerySchema.parse({ page: "3" });   // { page: 3, pageSize: 10 }
listBooksQuerySchema.safeParse({ page: "abc" }).success;   // false
```

## 15.4 Errors as classes

You want every error response to look the same, with the right status code. Start with a class hierarchy, like the one you built in Chapter 12:

```ts
// src/lib/errors.ts
export type ErrorDetail = { field: string; message: string };

export class AppError extends Error {
  readonly statusCode: number;
  readonly code: string;
  readonly details: ErrorDetail[];

  constructor(statusCode: number, code: string, message: string, details: ErrorDetail[] = []) {
    super(message);
    this.name = "AppError";
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(404, "NOT_FOUND", `${resource} '${id}' was not found`);
  }
}

export class ConflictError extends AppError {
  constructor(message: string) {
    super(409, "CONFLICT", message);
  }
}

export class ValidationError extends AppError {
  constructor(details: ErrorDetail[]) {
    super(400, "VALIDATION_FAILED", "The request contains invalid data", details);
  }
}
```

Now any code, however deep, can simply `throw new NotFoundError("Book", id)`, without knowing anything about HTTP responses.

## 15.5 Validation middleware

Instead of validating in every handler, write one reusable middleware:

```ts
// src/middleware/validate.ts
import type { Request, Response, NextFunction } from "express";
import type { z } from "zod";
import { ValidationError } from "../lib/errors.ts";

function toDetails(error: z.ZodError) {
  return error.issues.map((issue) => ({
    field: issue.path.join(".") || "(body)",
    message: issue.message,
  }));
}

export function validateBody(schema: z.ZodType) {
  return (req: Request, _res: Response, next: NextFunction) => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      throw new ValidationError(toDetails(result.error));
    }
    req.body = result.data;   // replace the raw body with the cleaned, validated version
    next();
  };
}

export function parseQuery<T extends z.ZodType>(schema: T, query: unknown): z.infer<T> {
  const result = schema.safeParse(query);
  if (!result.success) {
    throw new ValidationError(toDetails(result.error));
  }
  return result.data;
}
```

`validateBody(schema)` is a function that **returns** a middleware. That pattern (a "middleware factory") lets you plug in a different schema for each route:

```ts
router.post("/", validateBody(createBookSchema), bookController.create);
router.patch("/:id", validateBody(updateBookSchema), bookController.update);
```

By the time the handler runs, `req.body` is guaranteed to be valid.

The parameter `_res` starts with an underscore by convention: "this parameter is required by the signature, but I don't use it".

## 15.6 The central error handler

Express recognises an **error-handling middleware** by its **four** parameters: `(err, req, res, next)`. When anything throws (in a route, in middleware, even inside an `async` handler in Express 5), Express skips straight to it.

```ts
// src/middleware/error-handler.ts
import type { Request, Response, NextFunction } from "express";
import { AppError } from "../lib/errors.ts";

export function notFoundHandler(req: Request, res: Response) {
  res.status(404).json({
    error: { code: "ROUTE_NOT_FOUND", message: `Cannot ${req.method} ${req.originalUrl}` },
  });
}

export function errorHandler(err: unknown, req: Request, res: Response, _next: NextFunction) {
  // 1. Errors we threw on purpose
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: { code: err.code, message: err.message, details: err.details },
    });
  }

  // 2. Broken JSON in the request body (thrown by express.json())
  if (typeof err === "object" && err !== null && "type" in err && err.type === "entity.parse.failed") {
    return res.status(400).json({
      error: { code: "INVALID_JSON", message: "Request body is not valid JSON" },
    });
  }

  // 3. Anything else is a bug: log everything, reveal nothing
  console.error(`Unexpected error on ${req.method} ${req.originalUrl}:`, err);
  res.status(500).json({
    error: { code: "INTERNAL_ERROR", message: "Something went wrong on our side" },
  });
}
```

Register both **after all routes**:

```ts
app.use("/v1/books", bookRouter);
app.use(notFoundHandler);   // nothing matched
app.use(errorHandler);      // something threw
```

!!! warning "All four parameters are required"
    Even though `_next` is never used, removing it turns the function into normal middleware, and Express will stop treating it as an error handler. Keep all four.

### One error format, everywhere

Every error from your API now has the same shape, so clients can handle them all with one piece of code:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "The request contains invalid data",
    "details": [
      { "field": "year", "message": "Invalid input: expected number, received string" }
    ]
  }
}
```

- **`code`**: a stable, machine-readable string. Clients write `if (code === "CONFLICT")`. You can reword the message without breaking them.
- **`message`**: human-readable, safe to show.
- **`details`**: per-field problems, so a form can highlight the exact fields.

## 15.7 Before and after

The three broken requests from Chapter 14, now (real output from the finished API):

```bash
# Garbage data
curl -s -X POST localhost:3000/v1/books -H "Content-Type: application/json" \
  -d '{"title":"  ","year":"2008","genre":"poetry"}'
```

```output
{"error":{"code":"VALIDATION_FAILED","message":"The request contains invalid data","details":[{"field":"title","message":"title is required"},{"field":"author","message":"Invalid input: expected string, received undefined"},{"field":"year","message":"Invalid input: expected number, received string"},{"field":"genre","message":"Invalid option: expected one of \"fiction\"|\"non-fiction\"|\"tech\""}]}}   [400]
```

```bash
# Broken JSON
curl -s -X POST localhost:3000/v1/books -H "Content-Type: application/json" -d '{bad'
```

```output
{"error":{"code":"INVALID_JSON","message":"Request body is not valid JSON"}}   [400]
```

```bash
# Missing Content-Type
curl -s -X POST localhost:3000/v1/books -d 'title=x'
```

```output
{"error":{"code":"VALIDATION_FAILED","message":"The request contains invalid data","details":[{"field":"(body)","message":"Invalid input: expected object, received undefined"}]}}   [400]
```

No HTML, no stack traces, no crashes. Each problem gets a clear `400` that tells the client exactly what to fix.

!!! interview "Interview corner"
    - "Where should validation happen?" *At the edge, as soon as data enters the system, before any business logic. Never trust the client, even your own frontend.*
    - "How do you handle errors in an Express API?" *Throw typed errors from anywhere; one error-handling middleware maps them to status codes and a consistent JSON format; unexpected errors are logged in full but return a generic 500.*
    - "What is mass assignment?" *Copying all incoming fields onto a model, so an attacker can set fields they shouldn't, like `isAdmin`. Prevent it by only accepting known fields.*

!!! checkpoint "Checkpoint 15"
    1. Name five different things validation should check.
    2. What's the difference between `parse` and `safeParse`?
    3. Why is `z.infer<typeof schema>` better than writing the type by hand?
    4. Why does `z.coerce.number()` exist?
    5. How does Express recognise an error-handling middleware?
    6. Why does the error response include a `code` as well as a `message`?

## Tasks

!!! task "Task 15.1 · Schemas for notes · Core"
    In your Chapter 14 notes API, create `src/notes.schemas.ts` with:

    - `createNoteSchema`: `text` (trimmed, 1–500 characters), `pinned` (boolean, default `false`), `tags` (array of strings, default `[]`, max 5 tags)
    - `updateNoteSchema` = the create schema, `.partial()`
    - `listNotesQuerySchema`: `search` (optional), `pinned` (optional; coerce `"true"`/`"false"` correctly. Careful: `z.coerce.boolean()` turns `"false"` into `true`! Use `z.enum(["true","false"])` and convert it.)
    - Export the types with `z.infer`, and delete any hand-written versions.

!!! task "Task 15.2 · Errors and the central handler · Core"
    Add `src/lib/errors.ts`, `src/middleware/validate.ts` and `src/middleware/error-handler.ts` as shown in this chapter (type them, don't paste them). Change every route to **throw** errors (`NotFoundError` and friends) instead of sending error responses itself. Remove all the old `res.status(404).json(...)` calls from your routes.

!!! task "Task 15.3 · Prove it · Core"
    Add these to `requests.http` and check that each returns the right status and the standard error format:

    1. A `POST` with an empty `text`
    2. A `POST` with `"pinned": "yes"`
    3. A `POST` with six tags
    4. A `POST` with broken JSON
    5. A `POST` without a `Content-Type` header
    6. A `PATCH` to a note that doesn't exist
    7. `GET /notes?pinned=maybe`
    8. `GET /does-not-exist`
    9. A route that throws a plain `new Error("boom")` on purpose (add a temporary `/boom` route): it must return a generic `500`, and the real error must appear in your terminal.

    **Done when:** all nine return clean JSON in the same format, and none returns HTML. {: .done }

!!! task "Task 15.4 · Strict mode · Stretch"
    Switch `createNoteSchema` to `z.strictObject` and send a note with an extra field `"isAdmin": true`. Compare the behaviour with the default `z.object`. Which would you choose for a public API, and why? Write your reasoning in `answers.md`.
