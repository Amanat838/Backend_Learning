---
kind: project
title: "Project: URL Shortener"
phase: Phase 3
time: about 8–10 hours
---
A URL shortener turns `https://www.example.com/some/very/long/path?with=tracking` into `http://localhost:3000/gh7Kp2x`. It's a classic project and a classic **system design interview question**, so building it gives you real experience to talk about. It uses everything from Phase 3: Express, Zod, the error handler, REST design and the layered structure. Build it in `projects/url-shortener/`.

## What you're building

```bash
curl -i -X POST localhost:3000/v1/links -H "Content-Type: application/json" \
  -d '{"url":"https://github.com/Amanat838/Backend_Learning"}'
```

```http
HTTP/1.1 201 Created
Location: /v1/links/gh7Kp2x
Content-Type: application/json; charset=utf-8

{
  "code": "gh7Kp2x",
  "url": "https://github.com/Amanat838/Backend_Learning",
  "shortUrl": "http://localhost:3000/gh7Kp2x",
  "clicks": 0,
  "createdAt": "2026-11-10T14:03:11.402Z",
  "lastClickedAt": null
}
```

```bash
curl -i localhost:3000/gh7Kp2x
```

```http
HTTP/1.1 302 Found
Location: https://github.com/Amanat838/Backend_Learning
```

Open the short URL in a browser and it takes you to GitHub.

## Endpoints

| Method | Path | Purpose | Success | Errors |
|---|---|---|---|---|
| `POST` | `/v1/links` | Create a short link. Body: `{ url, code? }` | `201` + `Location` | `400`, `409`, `422` |
| `GET` | `/v1/links` | List links (`page`, `pageSize`, newest first) | `200` page | `400` |
| `GET` | `/v1/links/:code` | Stats for one link | `200` | `404` |
| `DELETE` | `/v1/links/:code` | Delete a link | `204` | `404` |
| `GET` | `/:code` | **Redirect** to the original URL and count the click | `302` + `Location` | `404` |
| `GET` | `/health` | Health check | `200` | — |

## Rules

1. **`url`** must be a valid `http` or `https` URL, at most 2,048 characters. `javascript:alert(1)`, `ftp://...` and `not a url` are rejected with `400`. (Allowing `javascript:` URLs would let attackers create "short links" that run code in a victim's browser.)
2. **Generated codes** are 7 characters from `a–z`, `A–Z`, `0–9`, chosen with `crypto.randomInt` (not `Math.random`, which is predictable). If a generated code already exists, try again (up to 5 times).
3. **Custom codes** (optional `code` in the body) must match `^[a-zA-Z0-9_-]{3,30}$` → otherwise `400`.
    - Already taken → `409` with code `CODE_TAKEN`.
    - Reserved words (`v1`, `health`, `api`, `admin`) → `422` with code `RESERVED_CODE`, because they would clash with your own routes.
4. **Redirects** use status `302` and increment `clicks` and set `lastClickedAt`. A `GET` that changes data? Yes: redirect endpoints are a known exception. The *purpose* of the request is to be redirected, and counting is a side effect, like a web server's access log.
5. **`shortUrl`** is built from a `BASE_URL` environment variable (default `http://localhost:3000`), validated in `config.ts`.
6. **All errors** use the standard format from Chapter 15.
7. **Route order matters:** `GET /:code` matches *any* single path segment, so register it **after** `/health` and the `/v1` routes.

## Structure

Use the Chapter 17 layout, with one module:

```text
src/
├── modules/links/
│   ├── link.schemas.ts
│   ├── link.repository.ts     ← Map<string, Link>
│   ├── link.service.ts        ← code generation, uniqueness, reserved words, clicks
│   ├── link.controller.ts
│   └── link.routes.ts         ← the /v1/links routes
├── lib/errors.ts
├── lib/codes.ts               ← generateCode()
├── middleware/                ← logger, validate, error handler
├── config.ts
├── app.ts                     ← mounts /health, /v1/links, then GET /:code, then 404 + errors
└── server.ts
```

## Milestones

1. **Skeleton:** `createApp`, config, health check, logger, error handler, 404. Commit.
2. **Create and get:** `POST /v1/links` with Zod validation and generated codes; `GET /v1/links/:code`. Commit.
3. **Redirect:** `GET /:code` with click counting. Test it in a browser. Commit.
4. **Custom codes:** validation, `409` and `422`. Commit.
5. **List and delete:** pagination (newest first) and `DELETE`. Commit.
6. **Polish:** a complete `requests.http`, and a README with an endpoint table, the error codes, and design decisions. Commit.

## Acceptance checklist

<ul class="checklist">
<li>Creating a link returns <code>201</code>, a 7-character code, a correct <code>shortUrl</code> and a <code>Location</code> header.</li>
<li>Opening the short URL in a browser lands on the original page, and the stats show <code>clicks: 1</code>.</li>
<li><code>{"url":"javascript:alert(1)"}</code>, <code>{"url":"ftp://x.com"}</code>, <code>{"url":"hello"}</code> and <code>{}</code> all return <code>400</code> with field details.</li>
<li>Custom code <code>my-cv</code> works; using it again returns <code>409 CODE_TAKEN</code>; <code>health</code> returns <code>422 RESERVED_CODE</code>; <code>ab</code> returns <code>400</code>.</li>
<li><code>GET /nope123</code> returns a JSON <code>404</code>, not a redirect.</li>
<li><code>GET /health</code> still works (it isn't swallowed by <code>/:code</code>).</li>
<li><code>GET /v1/links?pageSize=500</code> returns <code>400</code>; the list is newest first.</li>
<li>Deleting a link returns <code>204</code>, and then both its stats and its redirect return <code>404</code>.</li>
<li>No service file imports <code>express</code>; <code>npm run check</code> passes; no <code>any</code>.</li>
<li>The README explains how to run it, every endpoint, the error codes, and at least two design decisions.</li>
</ul>

## Stretch goals

- **Expiry:** an optional `expiresAt` (ISO date in the future). Expired links return **`410 Gone`**. (Why `410` and not `404`? Look it up.)
- **Rate limiting:** at most 10 link creations per minute per IP address (`req.ip`); after that, return `429` with a `Retry-After` header. Store the counts in a `Map`.
- **Persistence:** add a second repository that saves links to a JSON file (atomic writes from Chapter 10) and choose between them with an environment variable. **Only the repository changes**, and that's the payoff of layering.
- **Daily stats:** record clicks per day and return them in the stats endpoint.

!!! interview "Interview corner: “Design a URL shortener”"
    You'll be able to discuss real decisions: how codes are generated (random vs counter-based, and why random codes are harder to guess), handling collisions, why `302` instead of `301` (a `301` gets cached by browsers forever, so you'd stop counting clicks), validating URLs for security, and what changes at scale: a database with a unique index on `code`, caching hot links in Redis, and counting clicks asynchronously. That last part is exactly what Books 2–4 teach.
