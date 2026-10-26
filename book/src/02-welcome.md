---
kind: front
label: Start here
title: Welcome. How to Use This Book
---
This book takes you from "I've built a few small projects" to "I can design, build and explain a real backend API". It's written for you specifically: TypeScript and Node.js, about 5–10 hours a week, with one goal, **getting hired as a backend engineer**.

## What you'll be able to do by the end of this book

- Use the terminal and Git like a professional, every day, without thinking.
- Explain exactly what happens when someone types a URL and presses Enter (a classic interview question).
- Write clean, strict TypeScript and understand *why* the compiler complains.
- Work with files, environment variables, async code and streams in Node.js.
- Build an HTTP server **from scratch**, then build the same thing properly with Express.
- Validate input, handle errors consistently, and design REST APIs that other developers enjoy using.
- Structure a project into clear layers, the way real companies do.
- Ship four projects: a **Todo CLI**, a **Log Analyzer**, a **URL Shortener**, and **Slotify v0.1**, the first version of your portfolio project.

## Where this book fits

The whole journey has 11 phases. This book covers the first four. Book 2 starts with databases.

<div class="roadmap">
<div class="step here"><b>Phase 0 · This book</b><span>Tools, Git, professional habits</span></div>
<div class="step here"><b>Phase 1 · This book</b><span>How the web works: DNS, TCP, HTTP</span></div>
<div class="step here"><b>Phase 2 · This book</b><span>TypeScript and Node.js fundamentals</span></div>
<div class="step here"><b>Phase 3 · This book</b><span>HTTP servers, Express, REST APIs</span></div>
<div class="step"><b>Phase 4 · Book 2</b><span>SQL, PostgreSQL, data modelling</span></div>
<div class="step"><b>Phase 5 · Book 2</b><span>Authentication, authorization, security</span></div>
<div class="step"><b>Phase 6 · Book 3</b><span>Automated testing</span></div>
<div class="step"><b>Phase 7 · Book 3</b><span>Docker, CI/CD, deployment</span></div>
<div class="step"><b>Phase 8 · Book 4</b><span>Redis, queues, webhooks, AI features</span></div>
<div class="step"><b>Phase 9–10 · Book 4</b><span>System design, interviews, getting hired</span></div>
</div>

## Meet Slotify, your portfolio project

Many small businesses (salons, clinics, tutors, gyms) still take bookings on WhatsApp and paper. **Slotify** is a booking API that lets a business list its services and staff, and lets customers book, cancel and reschedule appointments.

It's a great portfolio project because it forces you to solve problems that real backend jobs are full of:

| Real problem | What you learn |
|---|---|
| Two customers try to book the same slot | Overlap checks, conflicts (`409`), later database transactions |
| A business in Dubai, a customer in Lahore | Time and time zones |
| "Send a reminder 24 hours before" | Background jobs and queues |
| Owner, staff and customer see different things | Authentication and authorization |
| The page gets slow with 10,000 bookings | Indexes, caching, pagination |

In this book you build **Slotify v0.1**: businesses, services, staff, and bookings with conflict detection, stored in memory. Later books add a real database, security, tests and deployment.

## How every chapter works

1. **The idea.** Each concept is explained in plain words first, often with an everyday analogy.
2. **Examples.** Small, runnable code examples. Type them in and run them.
3. **Common mistakes.** The traps beginners (and AI tools) fall into.
4. **Checkpoint.** A few quick questions to test yourself. Answers are in Appendix B.
5. **Tasks.** Hands-on work with clear "done when" criteria.

### Callout boxes

<div class="legend" markdown="1">

!!! idea "Idea"
    The key concept. If you remember one thing, remember this.

!!! analogy "Analogy"
    An everyday comparison that makes an idea click.

!!! warning "Watch out"
    Something that often causes bugs or confusion.

!!! mistake "Common mistake"
    Wrong code or thinking you'll see in the wild.

!!! tryit "Try it"
    A quick experiment. Do it now; it takes a minute.

!!! interview "Interview corner"
    How this topic shows up in real interviews.

</div>

### Tasks: core and stretch

Every task is marked **Core** or **Stretch**.

- **Core** tasks are required. They build the skills the next chapters depend on.
- **Stretch** tasks are optional. Do them when you have energy, or come back later.

Stuck on a task? **Hints are in Appendix A**, in three levels: a nudge, the concept you need, then pseudo-code. Open only the level you need.

## Your workspace

Keep everything in your `Backend_Learning` repository, one folder per chapter:

```text
Backend_Learning/
├── ch01/  ch02/  ch03/ ...        ← your code for each chapter
├── projects/
│   ├── todo-cli/
│   ├── log-analyzer/
│   └── url-shortener/
├── JOURNAL.md                     ← your learning log
└── (book, roadmap, progress files)

slotify/                           ← its OWN repository (your portfolio piece)
```

Slotify gets its own GitHub repository because recruiters should be able to look at it on its own.

!!! note "You've already started"
    Chapters 1–9 cover the same ground as Lessons 00–02 you worked on. Don't skip them: they explain things more simply and fill gaps from the earlier lessons (the staging area, phone numbers as strings, money in cents, the raw HTTP exercise). If you already finished a task, check your solution against the "done when" list and move on.

## A realistic schedule

At 5–10 hours a week, plan for about **14–16 weeks** for this book. A rhythm that works:

| Session | Length | What to do |
|---|---|---|
| Weekday 1 | 1–1.5 h | Read a section, type out the examples |
| Weekday 2 | 1–1.5 h | Read, then do the checkpoint |
| Weekend | 3–5 h | Tasks and projects |

Consistency beats intensity. Three steady sessions a week will get you much further than one 10-hour weekend followed by two weeks off.

## The rules

| Rule | Why it matters |
|---|---|
| **Type the code yourself.** Don't copy and paste from the book, from AI or from tutorials. | Your fingers learn what your eyes skip. And in interviews you won't have copy-paste. |
| **Run everything.** Reading code isn't the same as running it. | Surprises happen when you run code, and surprises are where learning happens. |
| **Read the whole error message before asking for help.** | Most errors tell you exactly what's wrong. Reading them is about half of the job. |
| **Commit after every session.** | Your GitHub history is visible proof that you put in the work. |
| **Write in your journal after every session.** | Your notes turn into interview stories and blog posts later. |
| **Done is better than perfect.** | Ship a simple version first, then improve it. That's how real teams work. |

## How to get unstuck

Use the **20-minute rule**: struggle on your own for 20 minutes (that struggle is where learning happens), then ask for help.

1. Re-read the error message, slowly, from the top.
2. Check the hints in Appendix A, one level at a time.
3. Ask Claude. Paste this template so you get a useful answer quickly:

```text
I'm on Task 14.3 in the book.
Goal: what I'm trying to do
What I tried: my code (or the file path in my repo)
What happened: the full error message or output
What I expected: ...
```

!!! idea "AI is your tutor, not your typist"
    Asking "why does this fail?" or "review my code" makes you stronger. Asking "write this for me" makes you weaker, because you skip exactly the thinking that interviews test. Once you can judge whether code is correct, AI tools will make you much faster. This book builds that judgement.

Let's begin.
