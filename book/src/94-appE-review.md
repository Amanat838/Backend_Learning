---
kind: appendix
num: E
title: Before You Ask for a Review
---
Before you tell Claude "Chapter 14 done, review it", go through this checklist. Fixing these yourself first means the review can focus on the interesting parts, which is how real code reviews work at a job.

## The basics

<ul class="checklist">
<li>Every <strong>Core</strong> task is done, and each "done when" condition is true. (Check them one by one; don't assume.)</li>
<li>It runs: no crash on start, and each example from the task gives the expected output.</li>
<li><code>npm run check</code> passes with zero errors.</li>
<li>No <code>any</code>, and no <code>as</code> or <code>!</code> without a comment explaining why.</li>
<li><code>git status</code> is clean, and everything is pushed.</li>
<li>The commits are small, with imperative messages that match their contents.</li>
<li>Your journal has an entry for this chapter.</li>
</ul>

## Code quality

<ul class="checklist">
<li>Names say what things are: <code>activeBookings</code>, not <code>data2</code> or <code>x</code>.</li>
<li>No duplicated logic. Repeated code is moved into a function.</li>
<li>Functions return values instead of printing (except at the very edges of the program).</li>
<li>Money is in integer cents; phone numbers and IDs are strings; times are ISO strings in UTC.</li>
<li>No magic numbers: <code>const MAX_PAGE_SIZE = 50</code>, not a bare <code>50</code> in three places.</li>
<li>Errors aren't swallowed. Every <code>catch</code> does something useful.</li>
<li>No commented-out code or leftover debugging <code>console.log</code>s.</li>
</ul>

## For APIs (Phase 3)

<ul class="checklist">
<li>Every input is validated with a schema, including query strings and path parameters.</li>
<li>Every status code matches the tables in Chapters 5 and 16.</li>
<li>Every error uses the same JSON format; nothing ever returns HTML or a stack trace.</li>
<li><code>requests.http</code> covers each success case <em>and</em> each error case.</li>
<li>Services don't import <code>express</code>; only repositories touch the data store.</li>
<li>The README has run instructions, an endpoint table and your design decisions.</li>
</ul>

## How to ask

```text
Chapter 14 done, review it.
Code: ch14/  (or the GitHub link)
Skipped: Task 14.5 (stretch)
Unsure about: whether requireApiKey should also protect GET routes
Hardest part: understanding why the logger has to come before express.json()
```

Telling the reviewer what you're unsure about, and what was hard, gets you a much more useful review. It's also exactly how good engineers write pull request descriptions.
