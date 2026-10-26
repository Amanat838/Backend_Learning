---
kind: project
title: "Project: Slotify v0.1"
phase: Phase 3
time: about 15–20 hours
---
This is the start of your portfolio project. Slotify v0.1 is a booking API for small businesses: a business lists its services and staff, and customers book appointments, with a guarantee that **nobody can double-book a staff member**. Data lives in memory for now; Book 2 moves it to PostgreSQL, adds time zones and authentication, and later books add tests, deployment, reminders and an AI booking assistant.

!!! idea "Its own repository"
    Create Slotify as a **separate public GitHub repository** called `slotify`, not a folder in `Backend_Learning`. Recruiters will look at it on its own, so its history, README and code quality all count. Commit in small, clear steps from the very first day.

## The data

```ts
type Business = {
  id: string;
  name: string;
  timeZone: string;        // e.g. "Asia/Karachi". Stored now, used properly in Book 2
  openingHour: number;     // 0–23, in UTC for v0.1
  closingHour: number;     // 1–24, in UTC, must be after openingHour
  createdAt: string;
};

type Service = {
  id: string;
  businessId: string;
  name: string;
  durationMinutes: number; // 15–480, a multiple of 15
  priceCents: number;
  currency: "PKR" | "USD" | "AED";
  isActive: boolean;
  createdAt: string;
};

type Staff = {
  id: string;
  businessId: string;
  name: string;
  serviceIds: string[];    // services this person can perform
  createdAt: string;
};

type Booking = {
  id: string;
  businessId: string;
  serviceId: string;
  staffId: string;
  customer: { name: string; phone: string };
  startsAt: string;        // ISO, UTC
  endsAt: string;          // calculated: startsAt + service duration
  status: "confirmed" | "cancelled";
  cancelReason?: string;
  cancelledAt?: string;
  createdAt: string;
};
```

Generate the types from Zod schemas wherever the data comes from a request (Chapter 15).

!!! warning "Time zones: a deliberate simplification"
    In v0.1, opening hours and all booking times are in **UTC**. Real businesses think in local time, and getting that right (including daylight saving time) is a whole topic, covered in Book 2. Put it in your README under **Known limitations**. Writing down your limitations honestly is a sign of a mature engineer, not a weakness.

## Endpoints

This is the design from Chapter 16:

| Method | Path | Success | Errors |
|---|---|---|---|
| `POST` | `/v1/businesses` | `201` | `400` |
| `GET` | `/v1/businesses/:businessId` | `200` | `404` |
| `PATCH` | `/v1/businesses/:businessId` | `200` | `400`, `404` |
| `POST` | `/v1/businesses/:businessId/services` | `201` | `400`, `404` |
| `GET` | `/v1/businesses/:businessId/services` | `200` | `404` |
| `GET` | `/v1/services/:serviceId` | `200` | `404` |
| `PATCH` | `/v1/services/:serviceId` | `200` | `400`, `404` |
| `DELETE` | `/v1/services/:serviceId` | `204` | `404`, `409` |
| `POST` | `/v1/businesses/:businessId/staff` | `201` | `400`, `404`, `422` |
| `GET` | `/v1/businesses/:businessId/staff` | `200` | `404` |
| `GET` / `PATCH` / `DELETE` | `/v1/staff/:staffId` | `200` / `200` / `204` | `400`, `404`, `409`, `422` |
| `GET` | `/v1/staff/:staffId/availability?date=YYYY-MM-DD&serviceId=...` | `200` | `400`, `404`, `422` |
| `POST` | `/v1/bookings` | `201` | `400`, `404`, `409`, `422` |
| `GET` | `/v1/bookings?staffId=&date=&status=&page=&pageSize=` | `200` | `400` |
| `GET` | `/v1/bookings/:bookingId` | `200` | `404` |
| `POST` | `/v1/bookings/:bookingId/cancel` | `200` | `404`, `409` |

## The business rules

These rules are the heart of the project. Put them in the **service layer**, and give each one its own error code.

### Services and staff

| Rule | Status | Error code |
|---|---|---|
| `durationMinutes` must be 15–480 and a multiple of 15 | `400` | `VALIDATION_FAILED` |
| Every ID in a staff member's `serviceIds` must exist **and belong to the same business** | `422` | `INVALID_SERVICE_IDS` |
| A service with future confirmed bookings can't be deleted (deactivate it with `isActive: false` instead) | `409` | `SERVICE_HAS_BOOKINGS` |
| A staff member with future confirmed bookings can't be deleted | `409` | `STAFF_HAS_BOOKINGS` |

### Creating a booking

Request body:

```json
{
  "serviceId": "…",
  "staffId": "…",
  "startsAt": "2027-01-15T09:00:00Z",
  "customer": { "name": "Ayesha Khan", "phone": "+923001234567" }
}
```

Check, **in this order**, and stop at the first failure:

| # | Rule | Status | Error code |
|---|---|---|---|
| 1 | Body valid: `startsAt` is an ISO date-time **on a 15-minute boundary** (`:00`, `:15`, `:30`, `:45`, zero seconds); customer name non-empty; phone 7–20 characters of digits, spaces, `+` or `-` | `400` | `VALIDATION_FAILED` |
| 2 | The service exists | `404` | `NOT_FOUND` |
| 3 | The service is active | `422` | `SERVICE_INACTIVE` |
| 4 | The staff member exists | `404` | `NOT_FOUND` |
| 5 | The staff member works for the service's business **and** can perform this service | `422` | `STAFF_CANNOT_PERFORM_SERVICE` |
| 6 | `startsAt` is in the future | `422` | `BOOKING_IN_PAST` |
| 7 | The booking starts at or after opening time and **ends** at or before closing time | `422` | `OUTSIDE_OPENING_HOURS` |
| 8 | It doesn't overlap any **confirmed** booking of the same staff member | `409` | `SLOT_TAKEN` |

`endsAt` = `startsAt` + the service's duration. The overlap rule is the one from Task 9.1, now with real dates: compare `getTime()` values.

### Cancelling

- Only a `confirmed` booking that **hasn't started yet** can be cancelled; otherwise → `409 BOOKING_NOT_CANCELLABLE`.
- The body may include an optional `reason` (max 200 characters).
- Set `status: "cancelled"`, `cancelledAt` and `cancelReason`, and return the updated booking.
- A cancelled booking **frees its slot** (rule 8 only looks at confirmed bookings).

### Availability: the "boss level"

`GET /v1/staff/:staffId/availability?date=2027-01-15&serviceId=…` returns every start time on that date when this staff member could take that service:

```json
{
  "staffId": "…",
  "serviceId": "…",
  "date": "2027-01-15",
  "durationMinutes": 30,
  "slots": ["2027-01-15T09:30:00.000Z", "2027-01-15T09:45:00.000Z", "…"]
}
```

- Candidate start times run every 15 minutes from opening time, and the **last** candidate must still **end** by closing time.
- Remove candidates that overlap a confirmed booking of this staff member.
- Remove candidates in the past.
- `date` must be a valid `YYYY-MM-DD` (`400`); the staff member and service must exist (`404`); the staff member must be able to perform the service (`422`).

Reuse the same overlap function as the booking rule. **One rule, one implementation**, so availability and booking can never disagree.

## Suggested structure

```text
slotify/
├── src/
│   ├── modules/
│   │   ├── businesses/   (schemas, repository, service, controller, routes)
│   │   ├── services/
│   │   ├── staff/
│   │   └── bookings/     (also availability)
│   ├── lib/
│   │   ├── errors.ts
│   │   └── time.ts       ← overlaps(), addMinutes(), isOnQuarterHour()... pure functions
│   ├── middleware/
│   ├── config.ts
│   ├── app.ts
│   └── server.ts
├── requests.http
├── .env.example
├── README.md
└── package.json
```

Services may call **other modules' repositories or services**: the booking service needs to look up services and staff. That's fine. Keep the dependency direction clean (bookings depend on staff and services, never the reverse).

## Levels

Work through the levels in order. Each one ends with a commit (or several) and a working API.

!!! task "Level 1 · Foundation and businesses"
    Repository, `package.json`, `tsconfig.json`, config, `createApp`, logger, error classes, error handler, 404, `/health`. Then the businesses module: create, get, update. Validate that `closingHour > openingHour`.

    **Done when:** you can create and fetch a business, and invalid input gives clean `400`s. {: .done }

!!! task "Level 2 · Services"
    Create and list under a business; get, update and delete by ID. Duration validation. (Leave the `SERVICE_HAS_BOOKINGS` rule until Level 4.)

!!! task "Level 3 · Staff"
    Create and list under a business; get, update and delete by ID. The `INVALID_SERVICE_IDS` rule, on both create and update.

!!! task "Level 4 · Bookings"
    Create (all 8 rules, in order), get, list with filters and pagination, and cancel. Then go back and add `SERVICE_HAS_BOOKINGS` and `STAFF_HAS_BOOKINGS`.

    **Done when:** every row of the acceptance scenario below gives the expected result. {: .done }

!!! task "Level 5 · Availability"
    The availability endpoint, reusing your overlap function.

!!! task "Level 6 · Make it portfolio-ready"
    - A `requests.http` that walks through the whole acceptance scenario, top to bottom.
    - A README with: what Slotify is and why it exists; how to run it; the endpoint table; the **error code table**; the business rules; the folder structure; **known limitations** (memory storage, UTC only, no auth yet); and **design decisions** (for example: why `POST /cancel` instead of `PATCH`, why the overlap logic lives in one place, why amounts are in cents).
    - A clean commit history, and the repository pinned on your GitHub profile.
    - A LinkedIn post about what you built and one hard problem you solved.

## Acceptance scenario

Use a date in the future (here, 15 January 2027). Set up: business **Glow Salon**, open 9–18 UTC; services **Haircut** (30 min) and **Colour** (90 min); staff **Bilal** (Haircut only) and **Sana** (both).

| # | Request | Expected |
|---|---|---|
| 1 | Book Bilal, Haircut, 09:00 | `201`, `endsAt` 09:30 |
| 2 | Book Bilal, Haircut, 09:15 | `409 SLOT_TAKEN` |
| 3 | Book Bilal, Haircut, 09:30 | `201` (touching is fine) |
| 4 | Book Sana, Haircut, 09:15 | `201` (a different staff member) |
| 5 | Book Bilal, **Colour**, 11:00 | `422 STAFF_CANNOT_PERFORM_SERVICE` |
| 6 | Book Sana, Colour, 17:00 | `422 OUTSIDE_OPENING_HOURS` (it would end at 18:30) |
| 7 | Book Sana, Colour, 16:30 | `201` (ends exactly at 18:00) |
| 8 | Book Bilal, Haircut, 08:45 | `422 OUTSIDE_OPENING_HOURS` |
| 9 | Book Bilal, Haircut, 10:10 | `400` (not on a 15-minute boundary) |
| 10 | Book Bilal, Haircut, yesterday at 10:00 | `422 BOOKING_IN_PAST` |
| 11 | Availability for Bilal, Haircut: the first slots | `10:00`, `10:15`, ... (09:00–09:59 is taken) |
| 12 | Cancel booking #1 | `200`, status `cancelled` |
| 13 | Cancel booking #1 again | `409 BOOKING_NOT_CANCELLABLE` |
| 14 | Availability for Bilal again | `09:00` is back, but `09:15` is **not** |
| 15 | Book Bilal, Haircut, 09:00 again | `201` (the slot was freed) |
| 16 | Delete the Haircut service | `409 SERVICE_HAS_BOOKINGS` |
| 17 | Create staff with a service ID from another business | `422 INVALID_SERVICE_IDS` |
| 18 | `GET /v1/bookings?staffId=<Bilal>&date=2027-01-15` | Bilal's bookings for that day, in start-time order |

Row 14 is worth a careful look. Cancelling booking #1 frees 09:00–09:30. A haircut at 09:00 ends at 09:30, exactly when booking #3 starts, so it fits. A haircut at 09:15 would run until 09:45 and overlap booking #3, so it stays unavailable. If your API gets this right, your overlap logic is right. Reasoning through cases like this is a big part of real backend work.

!!! interview "This is your best interview story"
    When an interviewer says "Tell me about a project you're proud of", talk about Slotify: the double-booking problem, why the overlap rule must live in one place, why rules are checked in a specific order, how you'd handle two requests arriving at the *same moment* (in memory, Node's single thread happens to protect you; with a real database you'll need transactions and constraints, which is Book 2), and the limitations you documented. That's a story about engineering judgement, which is exactly what they're hiring for.
