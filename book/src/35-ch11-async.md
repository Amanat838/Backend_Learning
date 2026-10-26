---
kind: chapter
num: 11
title: Async JavaScript and the Event Loop
phase: Phase 2
time: about 4–5 hours
---
A single Node.js process can serve thousands of users at once, while running your JavaScript on **one thread**. That sounds impossible until you understand the event loop. This chapter explains it, then teaches the async tools you'll use in every handler you write: promises, `async`/`await` and `Promise.all`.

!!! learn "What you'll learn"
    - Blocking vs non-blocking code
    - How the event loop works
    - Callbacks, promises and `async`/`await`
    - Sequential vs parallel work
    - Handling async errors
    - The mistakes that crash servers

## 11.1 The waiter who never waits

!!! analogy "Analogy: one very efficient waiter"
    A restaurant has one waiter. A bad waiter takes your order, walks to the kitchen, and **stands there** until your food is cooked, while every other table waits. A good waiter takes your order, hands it to the kitchen, and immediately serves the next table. When the kitchen rings the bell, the waiter brings the food.

    Node is the good waiter. Your JavaScript is the waiter (one person, one thread). The "kitchen" is the operating system and Node's background workers, which handle slow things: reading files, network requests, database queries, timers.

Most of a backend's time is spent **waiting**: for the database, for another API, for a file. Node never waits idly. It starts the slow operation, moves on to other work, and comes back when the result is ready. That's **non-blocking I/O** (I/O means input/output).

## 11.2 The event loop

<figure>
<svg viewBox="0 0 700 312" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, sans-serif" font-size="12">
  <defs><marker id="e1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#3b5bdb"/></marker></defs>
  <rect x="20" y="20" width="190" height="220" rx="8" fill="#f0f4ff" stroke="#3b5bdb"/>
  <text x="115" y="44" text-anchor="middle" font-weight="700" font-size="13" fill="#1d2433">Call stack</text>
  <text x="115" y="62" text-anchor="middle" fill="#4a5468" font-size="11">your JavaScript, one thing at a time</text>
  <rect x="45" y="160" width="140" height="28" rx="4" fill="#fff" stroke="#9aa3b5"/><text x="115" y="179" text-anchor="middle" font-family="Cascadia Mono, Consolas, monospace" font-size="11">handler()</text>
  <rect x="45" y="196" width="140" height="28" rx="4" fill="#fff" stroke="#9aa3b5"/><text x="115" y="215" text-anchor="middle" font-family="Cascadia Mono, Consolas, monospace" font-size="11">main()</text>
  <rect x="255" y="20" width="190" height="110" rx="8" fill="#effaf1" stroke="#2b8a3e"/>
  <text x="350" y="44" text-anchor="middle" font-weight="700" font-size="13" fill="#1d2433">Background ("kitchen")</text>
  <text x="350" y="68" text-anchor="middle" fill="#4a5468" font-size="11">timers · files · network</text>
  <text x="350" y="86" text-anchor="middle" fill="#4a5468" font-size="11">database queries</text>
  <text x="350" y="110" text-anchor="middle" fill="#7b8496" font-size="10.5" font-style="italic">handled by the OS and libuv</text>
  <rect x="490" y="20" width="190" height="95" rx="8" fill="#fff8eb" stroke="#c77700"/>
  <text x="585" y="44" text-anchor="middle" font-weight="700" font-size="13" fill="#1d2433">Microtask queue</text>
  <text x="585" y="64" text-anchor="middle" fill="#4a5468" font-size="11">promise callbacks, await</text>
  <text x="585" y="90" text-anchor="middle" fill="#c77700" font-size="11" font-weight="700">runs FIRST, all of it</text>
  <rect x="490" y="145" width="190" height="95" rx="8" fill="#f5f2ff" stroke="#7048e8"/>
  <text x="585" y="169" text-anchor="middle" font-weight="700" font-size="13" fill="#1d2433">Task queue</text>
  <text x="585" y="189" text-anchor="middle" fill="#4a5468" font-size="11">setTimeout, I/O callbacks</text>
  <text x="585" y="215" text-anchor="middle" fill="#7048e8" font-size="11" font-weight="700">one at a time, after microtasks</text>
  <g stroke="#3b5bdb" stroke-width="1.8" fill="none" marker-end="url(#e1)">
    <path d="M212,80 L251,80"/>
    <path d="M447,62 L486,62"/>
    <path d="M447,110 C470,130 470,170 486,185"/>
    <path d="M585,243 C585,285 115,290 115,243"/>
  </g>
  <text x="232" y="72" text-anchor="middle" fill="#22348c" font-size="10.5">start</text>
  <text x="350" y="304" text-anchor="middle" fill="#22348c" font-size="11.5" font-weight="700">event loop: when the stack is empty, take the next callback</text>
</svg>
<figcaption>Your code starts slow work, the background does it, and finished callbacks queue up to run when the stack is free.</figcaption>
</figure>

1. Your JavaScript runs on the **call stack**, one function at a time.
2. When you start something slow (a timer, a file read, a query), Node hands it to the **background** and your code carries on.
3. When the slow work finishes, its callback is put in a **queue**.
4. Whenever the call stack is empty, the **event loop** takes the next callback from a queue and runs it.
5. **Microtasks** (promise callbacks, code after an `await`) run before the next **task** (timers, I/O callbacks). All waiting microtasks run first.

Predict this before reading the answer:

```ts
console.log("1");
setTimeout(() => console.log("2"), 0);
Promise.resolve().then(() => console.log("3"));
console.log("4");
```

```output
1
4
3
2
```

Why: `1` and `4` are normal code and run immediately. `3` is a promise callback (microtask), so it runs as soon as the stack is empty. `2` is a timer callback (task), so it runs after the microtasks, **even with a delay of 0**.

!!! warning "Don't block the event loop"
    Because there's one thread, a long-running calculation freezes **everything**, including every other user's request. In this experiment, a timer is supposed to tick every 200 ms, but one second of heavy work freezes it:

    ```output
    tick at 200 ms
    tick at 400 ms
    starting 1 second of heavy work...
    heavy work done
    tick at 1501 ms      ← no ticks for over a second!
    tick at 1716 ms
    ```

    On a server, that means every user waits. Slow *waiting* is fine (Node is great at it); slow *computing* in a request handler is not.

## 11.3 Callbacks: the original style

The first async style was passing a function to be called when the work is done:

```ts
import fs from "node:fs";

fs.readFile("notes.txt", "utf8", (err, text) => {
  if (err) {
    console.error("Could not read:", err.message);
    return;
  }
  console.log(text);
});
console.log("this prints first");
```

It works, but when one step depends on another, the callbacks nest deeper and deeper ("callback hell"), and error handling must be repeated at every level. You'll see callbacks in older code and in event APIs (`socket.on("data", ...)`), but new code uses promises.

## 11.4 Promises

A **promise** is an object representing a result that will arrive later.

!!! analogy "Analogy: the restaurant buzzer"
    You order at a food court and get a buzzer. The buzzer isn't your food; it's a *promise* of food. Later it either buzzes (your order is ready: **fulfilled**) or the staff tell you they ran out (**rejected**). Until then it's **pending**.

```ts
// Creating a promise (you'll rarely need to do this yourself)
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Using one with .then and .catch
sleep(500)
  .then(() => console.log("half a second later"))
  .catch((err) => console.error("failed:", err));
```

## 11.5 `async` and `await`: promises that read like normal code

```ts
async function showBooking(id: string): Promise<void> {
  try {
    const booking = await getBooking(id);           // wait here without blocking Node
    const staff = await getStaff(booking.staffId);  // runs after the line above
    console.log(`${booking.id} with ${staff.name}`);
  } catch (err) {
    console.error("Could not load booking:", err);  // catches rejections from either await
  }
}
```

- An `async` function **always returns a promise**. `return 42` inside it gives `Promise<number>`.
- `await` pauses **this function only**, until the promise settles. Node keeps serving other work in the meantime.
- A rejected promise makes `await` **throw**, so normal `try`/`catch` works.

!!! mistake "Forgetting `await`"
    ```ts
    const user = loadUser();      // forgot await!
    console.log(user);            // Promise { <pending> }
    console.log(user.name);       // undefined
    ```
    If you see `Promise { <pending> }` in your output, you forgot an `await`. TypeScript usually catches this (`Property 'name' does not exist on type 'Promise<User>'`), another reason to keep it strict.

## 11.6 Sequential vs parallel

Imagine a booking page needs a service (300 ms), a staff member (200 ms) and reviews (400 ms). These don't depend on each other.

```ts
// Sequential: each one waits for the previous one
const service = await getService();
const staff = await getStaff();
const reviews = await getReviews();
// total ≈ 300 + 200 + 400 = 900 ms

// Parallel: start all three, then wait for all of them
const [service2, staff2, reviews2] = await Promise.all([getService(), getStaff(), getReviews()]);
// total ≈ the slowest one = 400 ms
```

Real measurement:

```output
sequential: 919 ms
parallel: 413 ms
```

!!! idea "Rule"
    If tasks **depend** on each other (you need the booking before you can load its staff member), use sequential `await`s. If they're **independent**, start them together with `Promise.all`.

| Tool | Waits for | If one fails... |
|---|---|---|
| `Promise.all([...])` | all of them | rejects immediately with that error |
| `Promise.allSettled([...])` | all of them | never rejects; gives each result's `status`: `"fulfilled"` or `"rejected"` |
| `Promise.race([...])` | the first to settle | settles like the first one (useful for timeouts) |
| `Promise.any([...])` | the first to succeed | rejects only if all fail |

!!! mistake "`async` inside `forEach`"
    ```ts
    ids.forEach(async (id) => {
      await sendReminder(id);
    });
    console.log("all reminders sent");   // ✗ a lie: nothing has been sent yet
    ```
    `forEach` doesn't wait for async callbacks. Use `for (const id of ids) { await sendReminder(id); }` to go one at a time, or `await Promise.all(ids.map((id) => sendReminder(id)))` to go in parallel.

## 11.7 Errors in async code

A rejected promise that nobody handles is an **unhandled rejection**, and by default **Node crashes the whole process**:

```ts
async function failLater() {
  await sleep(10);
  throw new Error("payment provider timeout");
}
failLater();   // no await, no .catch
```

```output
Error: payment provider timeout
    at failLater (file:///.../src/demo.ts:3:9)

Node.js v24.15.0
```

On a server, that means one bad request takes the whole service down for everyone. So:

- **Always `await` promises** (or attach a `.catch`).
- **Wrap awaits in `try`/`catch`** where you can do something useful with the error.
- In Phase 3, Express 5 catches errors from `async` route handlers for you and passes them to your error handler (Chapter 15).

!!! interview "Interview corner"
    - "Node is single-threaded. How does it handle many requests at once?" *JavaScript runs on one thread, but I/O is non-blocking: Node starts the database or network operation, handles other requests while it waits, and runs the callback when the result is ready, via the event loop.*
    - "What's the difference between `Promise.all` and `Promise.allSettled`?"
    - "What happens if you do heavy computation in a request handler?" *It blocks the event loop, so every other request waits. Move it to a worker thread or a background job.*

!!! checkpoint "Checkpoint 11"
    1. In the waiter analogy, what is the waiter and what is the kitchen?
    2. Why does `setTimeout(fn, 0)` run *after* a `Promise.resolve().then(...)` callback?
    3. What does an `async` function return?
    4. Three independent queries take 100, 200 and 300 ms. Roughly how long do they take sequentially, and with `Promise.all`?
    5. What happens to a Node process when a rejected promise is never handled?

## Tasks

!!! task "Task 11.1 · Predict the output · Core"
    For each snippet, write your prediction in `ch11/answers.md` **first**, then run it and explain any surprises.

    ```ts
    // Puzzle A
    console.log("A");
    setTimeout(() => console.log("B"), 100);
    setTimeout(() => console.log("C"), 0);
    console.log("D");
    ```

    ```ts
    // Puzzle B
    async function main() {
      console.log("1");
      await sleep(0);
      console.log("2");
    }
    main();
    console.log("3");
    ```

    ```ts
    // Puzzle C
    setTimeout(() => console.log("timeout"), 0);
    Promise.resolve().then(() => console.log("promise 1")).then(() => console.log("promise 2"));
    queueMicrotask(() => console.log("microtask"));
    console.log("sync");
    ```

    ```ts
    // Puzzle D
    async function getNumber() {
      return 42;
    }
    const n = getNumber();
    console.log(n);
    n.then((v) => console.log(v));
    console.log("end");
    ```

!!! task "Task 11.2 · Sequential vs parallel · Core"
    In `ch11/src/timing.ts`, write three fake async functions with `sleep`: `getService()` (300 ms), `getStaff()` (200 ms), `getReviews()` (400 ms). Measure with `performance.now()`:

    1. Calling them sequentially.
    2. Calling them with `Promise.all`.
    3. Make `getReviews` reject with an error. What happens with `Promise.all`? With `Promise.allSettled`? Print both outcomes.

    **Done when:** your output shows roughly 900 ms vs 400 ms, and both failure behaviours. {: .done }

!!! task "Task 11.3 · A timeout helper · Core"
    Write `withTimeout<T>(promise: Promise<T>, ms: number): Promise<T>` that rejects with `new Error("Timed out after 500 ms")` if the promise takes too long. Use `Promise.race`. Test it with a fast promise and a slow one.

    This is a real backend tool: you should never wait forever for another service.

!!! task "Task 11.4 · Retry with backoff · Stretch"
    Write `retry<T>(fn: () => Promise<T>, attempts: number): Promise<T>`. It calls `fn`, and if it fails, waits and tries again: 100 ms, then 200 ms, then 400 ms (**exponential backoff**). After the last attempt, it throws the last error. Test it with a function that fails twice and then succeeds, logging each attempt.

!!! task "Task 11.5 · Block the loop · Stretch"
    Reproduce the "tick" experiment from section 11.2. Then explain in `ch11/answers.md` what a server with that loop inside a request handler would feel like to its other users.
