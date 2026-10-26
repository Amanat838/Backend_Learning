---
kind: chapter
num: 3
title: How Professionals Learn and Solve Problems
phase: Phase 0
time: about 2 hours
---
The difference between a junior and a senior engineer isn't how much they've memorised. It's how they deal with things they *don't* know yet: reading errors calmly, finding answers in documentation, and asking good questions. These habits will matter more than any framework.

!!! learn "What you'll learn"
    - How to read an error and a stack trace
    - A step-by-step debugging method
    - How to read official documentation
    - How to ask for help so you get answers fast
    - Why a learning journal is worth it
    - Learning in public to get noticed

## 3.1 Errors are messages, not insults

Beginners see red text and panic. Professionals see red text and think "good, now I know what's wrong". An error message is the computer telling you **what** went wrong and **where**.

Here's a real one. Read it from the top:

```output
file:///E:/Backend_Learning/ch03/greet.js:4
  return user.name.toUpperCase();
              ^

TypeError: Cannot read properties of undefined (reading 'name')
    at shout (file:///E:/Backend_Learning/ch03/greet.js:4:15)
    at file:///E:/Backend_Learning/ch03/greet.js:8:29
    at Array.map (<anonymous>)
    at shoutAll (file:///E:/Backend_Learning/ch03/greet.js:8:15)
    at file:///E:/Backend_Learning/ch03/greet.js:11:13
    at ModuleJob.run (node:internal/modules/esm/module_job:437:25)
    ...
```

How to read it:

| Part | What it tells you |
|---|---|
| `greet.js:4` and the `^` | **Where:** file `greet.js`, line 4. The arrow points at the exact spot. |
| `TypeError` | **What kind** of error: you used a value as the wrong type. |
| `Cannot read properties of undefined (reading 'name')` | **What exactly:** you wrote `something.name`, but `something` was `undefined`. |
| The `at ...` lines (the **stack trace**) | **How you got there**, newest first: `shout` was called by a `map` callback on line 8, inside `shoutAll`, which was called from line 11. |
| Lines with `node:internal` | Node's own code. You can usually ignore them. |

So the question becomes: *why was `user` undefined on line 4?* Follow the trace to line 8:

```js
return list.map((u, i) => shout(list[i + 1]));
```

There it is. On the last item, `list[i + 1]` goes past the end of the array and gives `undefined`. The fix is `shout(u)`.

!!! idea "Read the whole error, top to bottom, before doing anything else"
    Most errors tell you the file, the line and the reason. Many beginners read only the first word, then go and search the internet. Reading the full message takes 30 seconds, and often it's all you need.

### Errors you'll meet constantly

| Error | Usually means |
|---|---|
| `TypeError: Cannot read properties of undefined (reading 'x')` | You wrote `a.x`, and `a` is `undefined`. Find out why `a` has no value. |
| `ReferenceError: foo is not defined` | Typo in a name, or you forgot to import or declare it. |
| `TypeError: Assignment to constant variable.` | You tried to reassign a `const`. |
| `SyntaxError: Unexpected end of JSON input` | You called `JSON.parse("")` on an empty string or a cut-off file. |
| `SyntaxError: Expected property name or '}' in JSON` | Invalid JSON, e.g. keys without quotes: `{name: 1}`. |
| `Error: ENOENT: no such file or directory` | The file path is wrong, or you ran the command from a different folder. |
| `Error: listen EADDRINUSE: address already in use :::3000` | Another program (often your *previous* server) is already using port 3000. |

## 3.2 A debugging method that works

When something doesn't work, don't change random things and hope. Follow these steps:

1. **Reproduce it.** Find the exact steps that cause the problem, every time.
2. **Read the error.** All of it (section 3.1).
3. **Form a guess.** "I think `user` is undefined because the index is off by one."
4. **Test the guess.** Add a `console.log(user)` just before the failing line, or set a breakpoint (Chapter 12).
5. **Fix one thing at a time,** then run it again.
6. **Understand why it broke.** Note it in your journal so you recognise it next time.

!!! analogy "Rubber duck debugging"
    Programmers keep a rubber duck on their desk and explain their code to it, line by line. Halfway through the explanation, they often spot the bug themselves. Explaining forces you to stop assuming and look at what the code *actually* does. Your journal works the same way.

## 3.3 Reading documentation

Official documentation is the source of truth. Tutorials and videos go out of date; the docs are updated with every release.

| Topic | Where |
|---|---|
| Node.js | nodejs.org/docs/latest-v24.x/api |
| JavaScript (language and web APIs) | developer.mozilla.org (MDN) |
| TypeScript | typescriptlang.org/docs |
| Express | expressjs.com |
| Zod | zod.dev |

**How to read a docs page without drowning:**

1. Read the one-paragraph description at the top.
2. Jump to the **examples**, and run one.
3. Look at the **parameters** and **return value** of the function you need.
4. Skip everything else until you need it.

!!! tryit "Try it"
    Open the Node.js docs and find the page for `fs.readFile` in the `fs/promises` section. What does it return? What happens if the file doesn't exist? That took you less time than watching a video would have.

## 3.4 Asking for help so you get answers fast

A good question gets a good answer in one reply. A vague question ("it doesn't work") takes five rounds of back-and-forth.

```text
I'm on Task 8.4 in the book.
Goal: make paginate() return the right page.
What I tried: (paste the code, or name the file in my repo)
What happened: page 3 returns [] (full output below)
What I expected: ["G"]
What I already checked: start index is 6, array has 7 items
```

Often, just writing this template makes you find the answer before you send it. That's rubber duck debugging again.

## 3.5 Your learning journal

After every session, add an entry to `JOURNAL.md` at the root of your repository:

```markdown
## 2026-10-27
- Learned: the staging area lets me split work into separate commits.
- Confused by: why PowerShell saved my file as UTF-16.
- Fixed: "address already in use" — my old server was still running.
- Next: Chapter 4, DNS and TCP.
```

Why bother?

- **It makes you think.** Writing "I learned X" forces you to check that you really did.
- **It becomes interview material.** "Tell me about a difficult bug you solved" is a classic question. Your journal will be full of answers.
- **It becomes blog posts and LinkedIn posts,** which help recruiters find you.

## 3.6 Learning in public

Recruiters can't hire you if they can't see you. From now on:

- **Commit and push every session.** A busy GitHub contribution graph is proof of consistency.
- **Post on LinkedIn once a week or two.** "This week I learned how HTTP works by sending a request over a raw TCP socket. Here's what surprised me…" Short, honest posts about real learning get noticed.
- **Write good READMEs.** Every project should explain what it does, how to run it, and what you learned.

!!! checkpoint "Checkpoint 3"
    1. In a stack trace, which line usually tells you where *your* code broke?
    2. You see `Error: ENOENT: no such file or directory, open 'todos.json'`. Name two possible causes.
    3. What are the six steps of the debugging method?
    4. Why are official docs better than a two-year-old tutorial?

## Tasks

!!! task "Task 3.1 · Start your journal · Core"
    Create `JOURNAL.md` in the root of your repository. Write entries for your last two sessions, using the format from section 3.5. Commit and push.

    **Done when:** `JOURNAL.md` is on GitHub and has at least two entries. {: .done }

!!! task "Task 3.2 · Error detective · Core"
    Create `ch03/greet.js` with exactly this buggy code, run it, and read the error:

    ```js
    const users = [{ name: "Ayesha" }, { name: "Bilal" }];

    function shout(user) {
      return user.name.toUpperCase();
    }

    function shoutAll(list) {
      return list.map((u, i) => shout(list[i + 1]));
    }

    console.log(shoutAll(users));
    ```

    Then, in `ch03/answers.md`:

    1. Write down the error type, the file and line, and what the message means.
    2. Explain the cause in your own words, and fix the bug.
    3. Cause each of these errors on purpose, in small separate files, and paste the message: `ReferenceError`, `Assignment to constant variable`, `Unexpected end of JSON input`, `ENOENT`.

    **Done when:** the fixed `greet.js` prints `[ 'AYESHA', 'BILAL' ]` and all four errors are documented. {: .done }

!!! task "Task 3.3 · Docs scavenger hunt · Core"
    Using **only** the official docs (no videos, no AI), answer in `ch03/answers.md`:

    1. What does `path.join("a", "..", "b")` return? (Node docs, `path` module)
    2. What's the difference between `Array.prototype.find` and `Array.prototype.filter`? (MDN)
    3. What does `String.prototype.padStart` do? Give an example. (MDN)
    4. Which Node.js flag loads environment variables from a `.env` file? (Node docs, command-line options)

!!! task "Task 3.4 · Learning in public · Stretch"
    Write a short LinkedIn post (5–8 sentences) about starting your backend journey and one thing you learned in Chapters 1–3. Post it, or save it in `ch03/post.md` for later.
