---
kind: project
title: "Project: Log Analyzer"
phase: Phase 2
time: about 6–8 hours
---
When a production system misbehaves, engineers dig through logs: "How many errors in the last hour? Which endpoint is slow? When did it start?" In this project you build a tool that answers those questions for an HTTP access log, using streams so it works on files of any size. Build it in `projects/log-analyzer/`.

## What you're building

```bash
node src/index.ts access.log
```

```output
Log report: access.log
──────────────────────────────────────────────
Lines read          20,000   (12 malformed, skipped)
Time range          2026-11-03 09:00:00 → 10:07:51 UTC
Requests            19,988

Status codes
  2xx   18,190   91.0%
  4xx    1,401    7.0%
  5xx      397    2.0%

Latency (ms)        avg 61 · median 38 · p95 210 · p99 980

Top routes
  GET  /v1/services              5,997
  GET  /v1/services/:id          3,981
  GET  /v1/bookings/:id          2,994
  ...

Slowest requests
  1,742 ms  POST /v1/bookings          2026-11-03T09:41:07.310Z
  ...
```

(Your numbers will differ, because the test data is random.)

## Step 0: Generate test data

This script creates realistic log files. It's supporting code, so you can copy it, but read it and make sure you understand it: it uses `once` and the `drain` event to respect backpressure while writing.

```ts
// scripts/generate-logs.ts
// Usage: node scripts/generate-logs.ts <lines> <output-file>
import { createWriteStream } from "node:fs";
import { once } from "node:events";

const total = Number(process.argv[2] ?? 10_000);
const outFile = process.argv[3] ?? "access.log";

const routes = [
  { method: "GET", path: () => "/v1/services", weight: 30, ms: 40 },
  { method: "GET", path: () => `/v1/services/${rand(1, 60)}`, weight: 20, ms: 30 },
  { method: "POST", path: () => "/v1/bookings", weight: 10, ms: 120 },
  { method: "GET", path: () => `/v1/bookings/${rand(1, 5000)}`, weight: 15, ms: 35 },
  { method: "DELETE", path: () => `/v1/bookings/${rand(1, 5000)}`, weight: 3, ms: 60 },
  { method: "GET", path: () => "/v1/staff", weight: 12, ms: 25 },
  { method: "GET", path: () => "/health", weight: 10, ms: 2 },
];
const totalWeight = routes.reduce((sum, r) => sum + r.weight, 0);

function rand(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function pickRoute() {
  let n = Math.random() * totalWeight;
  for (const r of routes) {
    n -= r.weight;
    if (n <= 0) return r;
  }
  return routes[0]!;
}

function pickStatus(method: string): number {
  const x = Math.random();
  if (x < 0.02) return 500;
  if (x < 0.06) return 404;
  if (x < 0.09) return method === "POST" ? 409 : 400;
  if (method === "POST") return 201;
  if (method === "DELETE") return 204;
  return 200;
}

const out = createWriteStream(outFile);
let time = Date.parse("2026-11-03T09:00:00Z");

for (let i = 1; i <= total; i++) {
  time += rand(5, 400);
  let line: string;
  if (Math.random() < 0.001) {
    line = "### corrupted line ###";
  } else {
    const route = pickRoute();
    const slow = Math.random() < 0.03 ? rand(5, 20) : 1;
    const duration = Math.max(1, Math.round(route.ms * slow * (0.5 + Math.random())));
    line = `${new Date(time).toISOString()} ${route.method} ${route.path()} ${pickStatus(route.method)} ${duration}ms`;
  }
  if (!out.write(line + "\n")) await once(out, "drain");
}
out.end();
await once(out, "finish");
console.log(`Wrote ${total} lines to ${outFile}`);
```

```bash
node scripts/generate-logs.ts 20000 access.log
node scripts/generate-logs.ts 2000000 huge.log     # about 100 MB, for the memory test
```

Each line looks like this:

```text
2026-11-03T09:00:00.225Z POST /v1/bookings 201 140ms
```

## Two new ideas

### Percentiles: a better way to measure "slow"

The **average** hides problems. If 99 requests take 10 ms and 1 takes 5,000 ms, the average is about 60 ms, which looks fine, yet one in a hundred users waited 5 seconds.

A **percentile** answers "how slow is it for the unluckiest X% of requests?":

- **median (p50):** half the requests were faster than this.
- **p95:** 95% were faster; 5% were slower.
- **p99:** 99% were faster; the slowest 1% were slower.

To calculate p95: sort all durations from fastest to slowest, and take the value at position `Math.ceil(0.95 × count) − 1`.

```text
durations sorted: [5, 8, 9, 12, 15, 20, 22, 30, 41, 500]   (10 values)
p50 → position ceil(0.50 × 10) − 1 = 4 → 15 ms
p95 → position ceil(0.95 × 10) − 1 = 9 → 500 ms
```

Real teams set goals like "p95 under 200 ms" because percentiles reflect what users actually experience.

### Route patterns: grouping similar paths

`/v1/bookings/17` and `/v1/bookings/4031` are the same endpoint with different IDs. Counting them separately gives a useless "top paths" list with thousands of entries. Normalise them: replace each purely numeric path segment with `:id`, so both become `/v1/bookings/:id`.

## Requirements

1. **Use streams** (`createReadStream` + `readline`). Never load the whole file at once.
2. **Parse each line** into a typed object: `{ timestamp: Date; method: string; path: string; route: string; status: number; durationMs: number }`. Write the parser as a pure function returning `LogEntry | null` (`null` for malformed lines).
3. **Malformed lines are skipped and counted.** Report the line numbers of the first three.
4. The **report** includes:
    - lines read, malformed count, valid requests
    - time range (first and last timestamp)
    - counts and percentages by status class (2xx, 3xx, 4xx, 5xx)
    - average, median, p95 and p99 latency
    - the top 5 routes by request count (using route patterns)
    - the 5 slowest individual requests
    - the busiest minute and how many requests it had
5. **Options:**
    - `--route <pattern>` to only analyse matching routes, e.g. `--route /v1/bookings/:id`
    - `--status <class>` to only count, e.g., `5xx`
    - `--json` to print the report as JSON instead of the table
6. **Errors:** a missing file or no arguments → a friendly message on stderr and exit code 1.
7. **No `any`**, and `npm run check` passes.

## Suggested structure

```text
projects/log-analyzer/
├── scripts/generate-logs.ts
├── src/
│   ├── index.ts      ← arguments, streaming the file, printing
│   ├── parse.ts      ← parseLine(line): LogEntry | null, toRoute(path)
│   ├── stats.ts      ← percentile(), and a Stats collector (add entries, get the report)
│   └── format.ts     ← the table output
└── README.md
```

## Build it in milestones

1. **Count lines** with a stream (you did this in Task 12.3).
2. **Parse lines** into `LogEntry` objects; count the malformed ones.
3. **Status classes and time range.**
4. **Latency stats:** average, then percentiles.
5. **Top routes** with route patterns, and the slowest requests.
6. **Options** (`--route`, `--status`, `--json`).
7. **Formatting and README.**

## Acceptance checklist

<ul class="checklist">
<li>A 20,000-line file is analysed correctly; the status percentages add up to 100%.</li>
<li>Corrupted lines are skipped, counted, and the first three line numbers are reported.</li>
<li><code>percentile([5, 8, 9, 12, 15, 20, 22, 30, 41, 500], 95)</code> returns <code>500</code>, and the median returns <code>15</code>.</li>
<li><code>/v1/bookings/17</code> and <code>/v1/bookings/4031</code> are both counted as <code>/v1/bookings/:id</code>.</li>
<li>The 2,000,000-line file works, and the memory used (<code>process.memoryUsage().rss</code>) stays far below the file size.</li>
<li><code>--json</code> prints valid JSON (check with <code>node src/index.ts access.log --json | node -e "JSON.parse(require('fs').readFileSync(0,'utf8'))"</code>).</li>
<li>A missing file gives a friendly error and exit code 1.</li>
<li>The README shows an example report and explains what p95 means.</li>
</ul>

## Stretch goals

- **Latency histogram** in ASCII: `0–50 ms ████████████ 61%`.
- **Errors over time:** 5xx count per minute, to spot *when* an incident started.
- **Compare two files:** "p95 went from 180 ms to 420 ms after the deploy".
- **Follow mode:** keep reading as new lines are appended, like `tail -f`.

!!! interview "Interview corner"
    "Why is p95 more useful than the average?" and "How would you process a 50 GB log file?" (stream it line by line, keep only running totals; and for percentiles at huge scale, approximate algorithms exist). These are real questions, and you'll have built the answer.
