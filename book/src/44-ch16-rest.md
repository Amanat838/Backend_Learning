---
kind: chapter
num: 16
title: Designing REST APIs
phase: Phase 3
time: about 4 hours
---
Code that works isn't the same as an API that's pleasant to use. A well-designed API is predictable: once a developer has used one endpoint, they can guess how the others work. This chapter covers the conventions that make APIs predictable, then you'll design Slotify's API, which becomes the spec for your project.

!!! learn "What you'll learn"
    - Resources and URL design
    - Which method and status for each operation
    - Actions that don't fit CRUD
    - Response shapes, pagination, filtering
    - Versioning and naming conventions
    - The mistakes reviewers spot first

## 16.1 Think in resources

In REST, URLs name **things** (resources), and the HTTP method says **what to do** with them.

!!! analogy "Analogy: a library"
    A library has collections (shelves of books) and items (one specific book). You don't need a special door for "borrow-a-book" and another for "return-a-book". You go to the book and say what you want to do. In REST, the URL is the book and the method is what you want to do.

| Rule | Good | Bad |
|---|---|---|
| Use **nouns**, not verbs | `GET /bookings` | `GET /getBookings` |
| Use **plural** collection names | `/services/42` | `/service/42` |
| Lowercase, words joined with hyphens | `/time-slots` | `/TimeSlots`, `/time_slots` |
| Put the **ID in the path** | `/bookings/b_91` | `/bookings?id=b_91` |
| Put **filters in the query** | `/bookings?status=confirmed` | `/confirmed-bookings` |
| Nest only to show ownership, one level deep | `/businesses/42/services` | `/businesses/42/services/7/staff/3/bookings` |

### Shallow nesting

Nesting shows that something belongs to something else: "the services *of* business 42". Use it to **create** and **list** children. But once a resource has its own ID, give it a top-level address:

```text
POST /v1/businesses/42/services     ← create a service inside business 42
GET  /v1/businesses/42/services     ← list business 42's services
GET  /v1/services/7                 ← one service, by its own ID
PATCH /v1/services/7
DELETE /v1/services/7
```

Deep URLs like `/businesses/42/services/7` force clients to know the parent's ID just to fetch a child, and they get very long very fast.

## 16.2 Methods and status codes for each operation

This table is the heart of REST. Learn it:

| Operation | Request | Success | Common errors |
|---|---|---|---|
| List | `GET /v1/books` | `200` + list | `400` bad query |
| Get one | `GET /v1/books/:id` | `200` + item | `404` |
| Create | `POST /v1/books` | `201` + item + `Location` header | `400`, `409` duplicate |
| Replace | `PUT /v1/books/:id` | `200` + item | `400`, `404` |
| Update part | `PATCH /v1/books/:id` | `200` + updated item | `400`, `404` |
| Delete | `DELETE /v1/books/:id` | `204`, no body | `404` |

Two details reviewers check:

- **`201` responses include a `Location` header** pointing at the new resource: `Location: /v1/books/9c2...`.
- **Return the resource after create and update.** The client then has the server's version, including generated fields like `id` and `createdAt`, without another request.

## 16.3 Actions that don't fit CRUD

Some operations are actions with rules attached, not simple field edits: cancelling a booking, confirming a payment, sending a reminder. You have two options:

```text
Option A:  PATCH /v1/bookings/b_91        {"status": "cancelled"}
Option B:  POST  /v1/bookings/b_91/cancel {"reason": "Feeling unwell"}
```

Option A looks pure, but status changes usually carry **rules**: you can't cancel a completed booking; cancelling might trigger a refund; you might need a reason. Hiding those rules behind "just change a field" makes them easy to bypass by accident.

**Option B** (an action sub-resource) makes the action explicit. It's easy to document, easy to protect with permissions, and it's what large, well-known APIs (Stripe, GitHub) do. Slotify will use it for `cancel`. Reserve `PATCH` for ordinary edits like changing a note or a name.

## 16.4 Response shapes

### Single resources: the object itself

```json
{
  "id": "svc_7",
  "businessId": "biz_42",
  "name": "Haircut",
  "durationMinutes": 30,
  "priceCents": 150000,
  "currency": "PKR",
  "createdAt": "2026-10-25T09:12:00.000Z"
}
```

### Collections: always wrap them

```json
{
  "items": [ { "id": "svc_7", "name": "Haircut" } ],
  "page": 1,
  "pageSize": 10,
  "total": 23,
  "totalPages": 3
}
```

!!! mistake "Returning a bare array"
    `GET /services` → `[ {...}, {...} ]` works today. But later you'll want to add pagination info, and there's nowhere to put it without breaking every client. **Always return an object for collections**, even before you need pagination.

### Conventions for the values

| Topic | Convention |
|---|---|
| Field names | **camelCase**: `durationMinutes`, not `duration_minutes`. Pick one style and never mix. |
| Dates and times | ISO 8601 strings in UTC: `"2026-11-03T09:30:00.000Z"` |
| Money | Integer minor units plus currency: `"priceCents": 150000, "currency": "PKR"` |
| IDs | Strings, even if they look like numbers |
| Booleans | Name them like questions: `isActive`, `pinned`, `hasParking` |
| Missing values | Be consistent: either omit the field, or send `null` |
| Errors | One format everywhere (Chapter 15) |

## 16.5 Pagination, filtering and sorting

```text
GET /v1/bookings?status=confirmed&staffId=st_4&from=2026-11-01&sort=-startsAt&page=2&pageSize=20
```

| Feature | Convention |
|---|---|
| **Pagination** | `page` (starting at 1) and `pageSize`, with a sensible default (10–20) and a **maximum** (50–100) |
| **Filtering** | One query parameter per field: `status=confirmed`, `staffId=st_4` |
| **Ranges** | `from` and `to` for dates; `minPrice` and `maxPrice` for amounts |
| **Sorting** | `sort=startsAt` ascending, `sort=-startsAt` descending (the `-` means reverse) |
| **Search** | `q=hair` for free-text search |

!!! warning "Always cap `pageSize`"
    Without a maximum, someone sends `?pageSize=1000000` and your server tries to load and send a million records. That's an easy way to take an API down, by accident or on purpose.

**Page numbers** (offset pagination) are simple and fine for most cases. They have one weakness: if new items are added while someone is paging, items can shift between pages. For feeds and very large tables, APIs use **cursor pagination** (`?after=b_91`). You'll meet it in Book 2.

## 16.6 Versioning

Put a version in the path: `/v1/...`. When you must make a **breaking change** (removing a field, renaming something, changing a type), you release `/v2/...` and keep `/v1` running until clients have moved over. Adding a new optional field is **not** breaking: clients ignore fields they don't know.

## 16.7 Documenting your API

At minimum, every API project's README has an **endpoint table**:

| Method | Path | Body | Success | Errors |
|---|---|---|---|---|
| `GET` | `/v1/books` | — | `200` page of books | `400` |
| `POST` | `/v1/books` | `{ title, author, year, genre }` | `201` book | `400`, `409` |
| `GET` | `/v1/books/:id` | — | `200` book | `404` |

Professional teams also write an **OpenAPI** specification: a YAML file describing every endpoint, which tools turn into interactive documentation and client code. A tiny taste:

```yaml
paths:
  /v1/books/{id}:
    get:
      summary: Get one book
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string }
      responses:
        "200": { description: The book }
        "404": { description: Book not found }
```

You'll generate OpenAPI docs automatically from your Zod schemas in a later book. For now, a clear README table plus a `requests.http` file is excellent.

## 16.8 Designing Slotify's API

Here's the v0.1 design you'll implement in the Slotify project. Read it and check it against the rules in this chapter:

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/businesses` | Register a business |
| `GET` | `/v1/businesses/:businessId` | Get a business |
| `PATCH` | `/v1/businesses/:businessId` | Update a business |
| `POST` | `/v1/businesses/:businessId/services` | Add a service to a business |
| `GET` | `/v1/businesses/:businessId/services` | List a business's services |
| `GET` / `PATCH` / `DELETE` | `/v1/services/:serviceId` | One service |
| `POST` | `/v1/businesses/:businessId/staff` | Add a staff member |
| `GET` | `/v1/businesses/:businessId/staff` | List staff |
| `GET` / `PATCH` / `DELETE` | `/v1/staff/:staffId` | One staff member |
| `GET` | `/v1/staff/:staffId/availability?date=&serviceId=` | Free start times for a day |
| `POST` | `/v1/bookings` | Book an appointment |
| `GET` | `/v1/bookings?staffId=&date=&status=` | List bookings |
| `GET` | `/v1/bookings/:bookingId` | Get a booking |
| `POST` | `/v1/bookings/:bookingId/cancel` | Cancel a booking |

!!! interview "Interview corner"
    "Design a REST API for X" is a very common interview task. Work through it out loud: identify the **resources** (nouns), their **relationships** (which belong to which), the **endpoints** with methods and status codes, the **request and response shapes**, then **edge cases**: validation, conflicts, pagination, permissions. That structure alone puts you ahead of most candidates.

!!! checkpoint "Checkpoint 16"
    1. Rewrite as REST: `POST /createService`, `GET /getStaffById?id=4`, `POST /deleteBooking`.
    2. Why `GET /services/7` instead of `GET /businesses/42/services/7`?
    3. What status and header does a successful create return?
    4. Why should collections be wrapped in an object?
    5. Why cancel with `POST /bookings/:id/cancel` rather than `PATCH {"status": "cancelled"}`?
    6. Is adding a new optional field to a response a breaking change?

## Tasks

!!! task "Task 16.1 · Review a bad API · Core"
    A junior developer designed this API for a gym. In `ch16/answers.md`, list **every problem** you can find, then write a corrected endpoint table:

    ```text
    GET    /getAllMembers                        → 200 [ ...members ]
    POST   /member/create                        → 200 { "success": true, "member": {...} }
    GET    /member?id=12                         → 200 { "success": false, "error": "not found" }
    POST   /member/12/update                     → 200 { "success": true }
    GET    /deleteMember/12                      → 200 { "success": true }
    GET    /Classes/Yoga/Members/12/Bookings     → 200 [ ... ]
    POST   /bookClass  { "member_id": 12, "classId": "yoga-mon" } → 200
    ```

    (Hint: there are at least ten problems.)

!!! task "Task 16.2 · Design an API on paper · Core"
    Design a REST API for a **clinic appointment system**: clinics, doctors, patients, and appointments, which can be booked, rescheduled and cancelled. In `ch16/clinic-api.md`, write:

    1. The resources and how they relate.
    2. A full endpoint table (method, path, purpose, success status, error statuses).
    3. Example request and response bodies for booking an appointment, including a `409` conflict.
    4. Which list endpoints need pagination and filters, and which filters.

!!! task "Task 16.3 · Make the notes API RESTful · Core"
    Upgrade your notes API:

    1. Move it under `/v1`.
    2. `GET /v1/notes` returns the wrapped pagination format, with `page` and `pageSize` (default 10, maximum 50) validated by Zod.
    3. Add `sort` with `createdAt` and `-createdAt` (the default is newest first).
    4. `POST` returns `201` with a `Location` header.
    5. Write a README with an endpoint table.

!!! task "Task 16.4 · OpenAPI · Stretch"
    Write an `openapi.yaml` describing two of your notes endpoints. Paste it into the online Swagger Editor (editor.swagger.io) to see the interactive documentation it generates.
