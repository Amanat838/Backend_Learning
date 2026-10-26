---
kind: chapter
num: 5
title: "HTTP Up Close: Methods, Status Codes, Headers"
phase: Phase 1
time: about 3 hours
---
HTTP is the language your backend speaks all day. The good news: it's a simple language, and most of it is plain text. Once you can read an HTTP message, debugging APIs becomes much easier.

!!! learn "What you'll learn"
    - What a request and a response look like
    - The parts of a URL, and query strings
    - Methods, and what "idempotent" means
    - Which status code to return, and when
    - The headers you'll use every week
    - Statelessness, cookies, and JSON rules

## 5.1 HTTP is just text

This is the most important idea in this chapter. An HTTP/1.1 request is literally this text, sent over a TCP connection:

```http
GET /v1/services?category=hair HTTP/1.1
Host: api.slotify.app
Accept: application/json
User-Agent: curl/8.9.0

```

And the response that comes back:

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 54

[{"id":"svc_1","name":"Haircut","durationMinutes":30}]
```

Both have the same structure:

| Part | Request | Response |
|---|---|---|
| **Start line** | method, path, version: `GET /v1/services HTTP/1.1` | version, status code, reason: `HTTP/1.1 200 OK` |
| **Headers** | one `Name: value` per line | one `Name: value` per line |
| **Blank line** | marks the end of the headers | marks the end of the headers |
| **Body** (optional) | data you send, e.g. JSON for a POST | the data you get back |

!!! warning "Line endings matter"
    Each line ends with **`\r\n`** (carriage return + line feed), not just `\n`. The blank line is therefore `\r\n\r\n`. You'll need this in Chapter 6 when you write HTTP by hand.

## 5.2 The parts of a URL

```text
https://api.slotify.app:443/v1/services?category=hair&page=2#top
└─┬──┘  └──────┬──────┘└┬┘└────┬─────┘└─────────┬─────────┘└┬┘
scheme       host      port   path            query      fragment
```

| Part | Meaning |
|---|---|
| **scheme** | Which protocol: `http` or `https` |
| **host** | Which server (resolved by DNS) |
| **port** | Which program. Optional: `https` means 443 and `http` means 80 if you leave it out |
| **path** | Which resource on the server: `/v1/services` |
| **query** | Extra options, as `key=value` pairs joined with `&` |
| **fragment** | A position *inside* the page. **Never sent to the server.** The browser uses it. |

### Query strings and encoding

Some characters have special meanings in URLs (`&`, `=`, `?`, `#`, spaces). To send them as data, they're **percent-encoded**:

| You want to send | It travels as |
|---|---|
| `hair cut` | `hair%20cut` (or `hair+cut` in a query) |
| `a&b` | `a%26b` |
| `ali@mail.com` | `ali%40mail.com` |

In JavaScript, `encodeURIComponent("a&b")` gives `"a%26b"`, and `new URL(...)` handles this for you.

!!! warning "Query strings are always text"
    `?page=2` arrives at your server as the **string** `"2"`, not the number `2`. You'll have to convert and validate it yourself. (Chapter 15 shows how.)

## 5.3 Methods

The method says **what you want to do** with the resource in the path.

| Method | Meaning | Has a body? | Safe? | Idempotent? |
|---|---|---|---|---|
| `GET` | Read something | No | ✓ | ✓ |
| `POST` | Create something, or trigger an action | Yes | ✗ | ✗ |
| `PUT` | Replace something completely | Yes | ✗ | ✓ |
| `PATCH` | Change part of something | Yes | ✗ | Usually ✗ |
| `DELETE` | Remove something | Rarely | ✗ | ✓ |
| `HEAD` | Like `GET`, but headers only | No | ✓ | ✓ |
| `OPTIONS` | "What am I allowed to do here?" (used by CORS) | No | ✓ | ✓ |

**Safe** means it doesn't change anything on the server. Browsers, search engines and caches assume `GET` is safe and may call it whenever they like. **Never** change data in a `GET` handler.

**Idempotent** means doing it once or ten times leaves the server in the **same state**.

!!! analogy "Analogy: the lift button"
    Pressing the lift's "call" button is idempotent: press it once or ten times, one lift comes. Ordering a pizza is not idempotent: order ten times, ten pizzas arrive.

    - `DELETE /bookings/42` ten times: the booking is gone. Same final state. ✓ idempotent.
    - `PUT /services/7 {"price": 1500}` ten times: the price is 1500. ✓ idempotent.
    - `POST /bookings` ten times: **ten bookings**. ✗ not idempotent.

This matters because **networks retry**. A customer on a slow connection taps "Book" twice, or their phone resends a request after a timeout. If `POST /bookings` isn't protected, they get two bookings. You'll learn the fix (idempotency keys) in Book 4. For now, just notice the danger.

## 5.4 Status codes

The status code is the server's one-number summary of what happened. Clients (and monitoring tools) make decisions based on it, so choosing the right one matters.

| Range | Meaning | Think of it as |
|---|---|---|
| **1xx** | Informational | Rare; you can ignore these for now |
| **2xx** | Success | "Done." |
| **3xx** | Redirect | "Look over there." |
| **4xx** | **Client** error | "*You* sent something wrong." |
| **5xx** | **Server** error | "*We* broke something." |

### The codes you must know

| Code | Name | Use it when | Slotify example |
|---|---|---|---|
| `200` | OK | Success, with data in the body | `GET /services` returns the list |
| `201` | Created | A new resource was created | `POST /bookings` succeeded. Add a `Location` header pointing at it. |
| `204` | No Content | Success, nothing to send back | `DELETE /bookings/42` succeeded |
| `301` | Moved Permanently | The resource lives at a new URL forever | `http://` → `https://` |
| `304` | Not Modified | "Your cached copy is still fine" | Browser caching |
| `400` | Bad Request | The request is malformed or invalid | Missing `serviceId`, broken JSON |
| `401` | Unauthorized | **Not logged in** (no or invalid credentials) | No token on `GET /me/bookings` |
| `403` | Forbidden | **Logged in, but not allowed** | A customer opening someone else's booking |
| `404` | Not Found | The resource doesn't exist | `GET /services/does-not-exist` |
| `409` | Conflict | Clashes with the current state | **The slot was just taken** |
| `422` | Unprocessable Content | Valid format, but breaks a business rule | Booking at 3 a.m. when the salon is closed |
| `429` | Too Many Requests | Rate limit exceeded | 300 booking attempts in a minute |
| `500` | Internal Server Error | An unexpected bug | Code threw an exception nobody caught |
| `503` | Service Unavailable | Deliberately unavailable for now | Maintenance mode, overloaded |

!!! warning "401 has a confusing name"
    The official name is "Unauthorized", but it really means **unauthenticated**: "I don't know who you are". `403` means "I know who you are, and you're not allowed".

!!! mistake "Lessons from Lesson 01"
    - **`DELETE` that returns nothing → `204`**, not `200`. `200` promises a body.
    - **An unexpected exception → `500`**, not `503`. `503` is for when you *knowingly* refuse, like during maintenance.
    - **`201` is about the outcome, not the method.** `POST /login` doesn't create anything, so it returns `200`.

### Choosing a 4xx: a quick decision guide

1. Is the request broken (bad JSON, missing or wrong-type fields)? → **400**
2. Do we know who the user is? If not → **401**
3. Are they allowed to do this? If not → **403**
4. Does the thing exist? If not → **404**
5. Does it clash with existing data (duplicate, already booked)? → **409**
6. Is it well-formed, but against a business rule? → **422**

## 5.5 Headers you'll use every week

| Header | Direction | Purpose | Example |
|---|---|---|---|
| `Host` | request | Which website (one IP can host many sites). **Required in HTTP/1.1.** | `Host: api.slotify.app` |
| `Content-Type` | both | Format of the body | `application/json; charset=utf-8` |
| `Content-Length` | both | Body size in **bytes** | `Content-Length: 54` |
| `Accept` | request | Formats the client can handle | `Accept: application/json` |
| `Authorization` | request | Credentials | `Authorization: Bearer eyJhbGci...` |
| `User-Agent` | request | Which client is calling | `User-Agent: curl/8.9.0` |
| `Location` | response | Where a redirect goes, or where the new resource lives | `Location: /v1/bookings/b_91` |
| `Cache-Control` | response | How long the response may be cached | `Cache-Control: max-age=60` |
| `ETag` | response | A version fingerprint of the resource | `ETag: "a1b2c3"` |
| `Set-Cookie` / `Cookie` | response / request | Store and send back small pieces of state | `Set-Cookie: session=abc; HttpOnly` |

Header names are **case-insensitive**: `content-type` and `Content-Type` are the same header. Node.js gives you header names in lowercase.

!!! tryit "Try it"
    In Git Bash: `curl -i https://jsonplaceholder.typicode.com/posts/1`. Find `Content-Type`, `Cache-Control` and `ETag`. Can you spot `X-Powered-By: Express`? That API is built with the same framework you'll use in Chapter 14. (Advertising your tech stack like this is a small security leak; you'll learn to hide it.)

## 5.6 HTTP is stateless

Each request stands completely alone. The server doesn't remember that you sent a request a second ago.

So how does "being logged in" work? **The client sends proof with every single request**: usually a cookie or an `Authorization` header. The server checks that proof each time.

!!! analogy "Analogy: a goldfish receptionist"
    Imagine a receptionist with a 3-second memory. Every time you walk up, you must show your visitor badge again. That's HTTP. The badge is your cookie or token.

### Cookies in 30 seconds

1. You log in. The server's response includes `Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax`.
2. The browser stores it, and automatically sends `Cookie: session=abc123` with every later request to that site.
3. The server looks up `abc123` and knows who you are.

- `HttpOnly`: JavaScript in the page can't read the cookie (protects against stolen sessions).
- `Secure`: only sent over HTTPS.
- `SameSite`: limits sending the cookie on requests that come from other websites.

Cookies are also used for preferences (language, dark mode), consent choices, and analytics and tracking. You'll go deep into sessions and tokens in Book 2.

## 5.7 JSON: the language of APIs

```json
{
  "id": "svc_1",
  "name": "Haircut",
  "priceCents": 150000,
  "active": true,
  "tags": ["hair", "men"],
  "description": null
}
```

The rules are strict:

- Keys must be in **double quotes**. `{name: 1}` is invalid.
- Strings use **double quotes** only.
- **No trailing commas**, **no comments**.
- Values can be: string, number, `true`/`false`, `null`, array, object. **There is no date type.** Dates travel as strings, usually in ISO 8601 format: `"2026-11-03T09:30:00Z"` (the `Z` means UTC).

```js
const text = JSON.stringify({ name: "Haircut", price: 1500 }); // object → string
const data = JSON.parse('{"name":"Haircut","price":1500}');    // string → object
```

## 5.8 REST and RPC, a first look

There are two main styles of API:

- **REST**: URLs name **things** (resources), and the method says what to do with them. `GET /v1/bookings/42`, `DELETE /v1/bookings/42`.
- **RPC**: URLs name **actions**, usually all sent as `POST`. `POST /api/getBooking`, `POST /api/cancelBooking`.

In Lesson 01 you found YouTube calling `POST /youtubei/v1/guide` just to *read* the sidebar. That's RPC style. Most public APIs, and this book, use REST. Chapter 16 covers REST design in depth.

!!! interview "Interview corner"
    - "What's the difference between `PUT` and `PATCH`?" `PUT` replaces the whole resource; `PATCH` changes only the fields you send.
    - "What's the difference between 401 and 403?" Not authenticated vs. authenticated but not allowed.
    - "What does idempotent mean? Is `POST` idempotent?" Same final state no matter how many times you repeat it. `POST` is not, which is why retries can create duplicates.

!!! checkpoint "Checkpoint 5"
    1. What separates the headers from the body in an HTTP message?
    2. Is the `#fragment` part of a URL sent to the server?
    3. Why must a `GET` handler never change data?
    4. Which status code: (a) booking created, (b) slot already taken, (c) not logged in, (d) logged in but it's someone else's booking, (e) booking deleted, nothing returned?
    5. A request arrives with `?page=3`. What JavaScript type is `3` when it reaches your server?
    6. How does a server "remember" a logged-in user if HTTP is stateless?

## Tasks

!!! task "Task 5.1 · Status code judge · Core"
    In `ch05/answers.md`, give the status code **and a one-sentence reason** for each:

    1. A customer books a free slot.
    2. A customer books a slot someone else took a second ago.
    3. The body is `{"serviceId": 12}` but `serviceId` must be a string.
    4. The body isn't valid JSON at all.
    5. The request has no login token, for `GET /me/bookings`.
    6. A logged-in staff member tries to delete the business.
    7. `GET /services/abc` and there's no service `abc`.
    8. `DELETE /bookings/42` succeeds.
    9. A booking for 3 a.m., but the salon opens at 9 a.m.
    10. The database connection fails unexpectedly while saving.
    11. A script calls the login endpoint 500 times in a minute.
    12. `POST /login` with correct credentials. (Careful!)

!!! task "Task 5.2 · Decode real messages · Core"
    For each message, write down the method or status, the important headers, and what's happening:

    ```http
    POST /v1/bookings HTTP/1.1
    Host: api.slotify.app
    Content-Type: application/json
    Authorization: Bearer abc.def.ghi
    Content-Length: 72

    {"serviceId":"svc_1","staffId":"st_4","startsAt":"2026-11-03T09:30:00Z"}
    ```

    ```http
    HTTP/1.1 201 Created
    Location: /v1/bookings/b_91
    Content-Type: application/json; charset=utf-8

    {"id":"b_91","status":"confirmed","endsAt":"2026-11-03T10:00:00Z"}
    ```

    Then answer: what would the response look like if the slot were already taken? Write the full response (status line, headers, a sensible JSON body).

!!! task "Task 5.3 · Idempotency in your own words · Core"
    In `ch05/answers.md`, explain idempotency using an example that isn't from this book. Then explain why a double-tap on "Book" is dangerous for `POST /bookings`, but not for `DELETE /bookings/42`.

!!! task "Task 5.4 · URL surgery · Stretch"
    Write `ch05/url.mjs` that uses the built-in `URL` class to take `https://api.slotify.app:8443/v1/services?category=hair cut&page=2#top` and print its protocol, host, port, path, each query parameter (use `url.searchParams`) and fragment. What happened to the space in `hair cut`?
