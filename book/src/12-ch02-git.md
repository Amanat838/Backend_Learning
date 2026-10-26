---
kind: chapter
num: 2
title: Git and GitHub, the Professional Way
phase: Phase 0
time: about 3 hours
---
Every company uses Git. In your first week on a job you'll be expected to create a branch, commit cleanly and open a pull request. This chapter builds the right mental model, so Git stops feeling like magic spells.

!!! learn "What you'll learn"
    - What Git really is (a timeline of snapshots)
    - The four places your code lives
    - What the staging area is *for*
    - How to write commits a reviewer will love
    - Branches and merging
    - How to undo mistakes safely

## 2.1 What Git is

Git is not "saving to the cloud". Git is a **time machine for your project**. Every commit is a snapshot of all your files at one moment. You can look at any snapshot, compare two snapshots, or go back.

!!! analogy "Analogy: a photo album"
    Imagine taking a photo of your desk every time you finish a piece of work. Each photo has a caption ("Add login form"). Later you can flip back through the album and see exactly what the desk looked like on any day. A commit is one photo, the message is its caption, and the repository is the album.

## 2.2 The four places your code lives

<figure>
<svg viewBox="0 0 720 190" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, sans-serif">
  <defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#3b5bdb"/></marker></defs>
  <g font-size="13" text-anchor="middle">
    <rect x="10" y="40" width="140" height="70" rx="8" fill="#f0f4ff" stroke="#3b5bdb"/>
    <text x="80" y="70" font-weight="700" fill="#1d2433">Working folder</text>
    <text x="80" y="90" fill="#4a5468" font-size="11">the files you edit</text>
    <rect x="195" y="40" width="140" height="70" rx="8" fill="#fff8eb" stroke="#c77700"/>
    <text x="265" y="70" font-weight="700" fill="#1d2433">Staging area</text>
    <text x="265" y="90" fill="#4a5468" font-size="11">the next snapshot</text>
    <rect x="380" y="40" width="140" height="70" rx="8" fill="#effaf1" stroke="#2b8a3e"/>
    <text x="450" y="70" font-weight="700" fill="#1d2433">Local repository</text>
    <text x="450" y="90" fill="#4a5468" font-size="11">history on your PC</text>
    <rect x="565" y="40" width="145" height="70" rx="8" fill="#f5f2ff" stroke="#7048e8"/>
    <text x="637" y="70" font-weight="700" fill="#1d2433">GitHub (remote)</text>
    <text x="637" y="90" fill="#4a5468" font-size="11">backup + portfolio</text>
  </g>
  <g stroke="#3b5bdb" stroke-width="2" fill="none" marker-end="url(#ar)">
    <line x1="152" y1="62" x2="191" y2="62"/><line x1="337" y1="62" x2="376" y2="62"/><line x1="522" y1="62" x2="561" y2="62"/>
  </g>
  <g font-family="Cascadia Mono, Consolas, monospace" font-size="11.5" fill="#22348c" text-anchor="middle">
    <text x="172" y="30">git add</text><text x="357" y="30">git commit</text><text x="542" y="30">git push</text>
  </g>
  <g stroke="#9aa3b5" stroke-width="1.6" fill="none" stroke-dasharray="4 3" marker-end="url(#ar)">
    <path d="M637,112 C637,165 80,165 80,114"/>
  </g>
  <text x="360" y="178" font-family="Cascadia Mono, Consolas, monospace" font-size="11.5" fill="#5c677d" text-anchor="middle">git pull  (bring others' commits down to you)</text>
</svg>
<figcaption>Your changes travel left to right. Nothing reaches GitHub until you push.</figcaption>
</figure>

1. **Working folder.** The files you see and edit in VS Code.
2. **Staging area.** A waiting room where you put the changes that will go into the *next* commit.
3. **Local repository.** The history of commits, stored in the hidden `.git` folder on your computer.
4. **Remote (GitHub).** A copy of the history on a server: a backup, a way to collaborate, and your public portfolio.

## 2.3 The staging area: what it's really for

The staging area lets you **choose exactly which changes go into the next commit.**

Imagine you spent an evening doing two unrelated things: you fixed a bug in `format.ts` *and* added a new `paginate.ts`. Without staging, you'd have to commit both together under one confusing message. With staging, you make two clean commits:

```bash
git add src/format.ts
git commit -m "Fix price formatting for amounts in cents"

git add src/paginate.ts
git commit -m "Add generic paginate helper"
```

!!! mistake "Common mistake"
    "The staging area is for testing changes before production." No. Testing and production have nothing to do with it. Staging is about **grouping changes into meaningful commits**.

## 2.4 The daily workflow

```bash
git status                 # what changed? (run it ALL the time)
git diff                   # show changes not yet staged, line by line
git add src/app.ts         # stage one file
git add .                  # stage everything in this folder (check git status first!)
git diff --staged          # show what you're about to commit
git commit -m "Add health check endpoint"
git push                   # send your commits to GitHub
git log --oneline --graph  # see history as a compact tree
```

!!! idea "The golden habit"
    Before you close VS Code, run `git status`. You want to see:

    `nothing to commit, working tree clean` and `Your branch is up to date with 'origin/main'`.

    If you don't see both, you have work that isn't safe on GitHub yet.

## 2.5 Writing good commit messages

Reviewers and future you will read your history. A good message completes the sentence **"If applied, this commit will..."**

| Bad | Good | Why |
|---|---|---|
| `update` | `Add pagination to GET /books` | Says what changed |
| `Added a date line` | `Add date line to sysinfo output` | Imperative mood: "Add", not "Added" |
| `fix` | `Fix 100x price bug: convert cents before formatting` | Says what and why |
| `Lesson 01 exercises 1.1 to 1.6` (but 1.4 and 1.6 aren't there) | `Add Lesson 01 answers for 1.1–1.3 and 1.5` | **The message must match the contents** |

### Atomic commits

An **atomic commit** contains **one logical change**, complete and working. If a commit's message needs the word "and", it should probably be two commits.

## 2.6 .gitignore: things Git must never track

Create `.gitignore` at the root of a repository:

```text
node_modules/
dist/
.env
*.log
.DS_Store
```

!!! warning "Never commit secrets"
    API keys, passwords and database URLs go in a `.env` file, and `.env` goes in `.gitignore`. Automated bots scan GitHub for leaked keys and can abuse them within minutes. If you ever commit a secret, deleting the file isn't enough, because it's still in the history. You must **revoke the key** and create a new one.

Also: `.gitignore` itself **must be committed**. An untracked `.gitignore` protects only your machine.

## 2.7 Branches

A branch is a **parallel timeline**. You can experiment on a branch without touching `main`. If the experiment works, you merge it back. If not, you delete it.

```bash
git switch -c add-search      # create a branch and move onto it
# ...edit, add, commit...
git switch main               # go back to main (your branch's changes disappear from view)
git merge add-search          # bring the branch's commits into main
git branch -d add-search      # delete the branch (its commits are now in main)
git push
```

At a job you'll rarely merge into `main` yourself. Instead you push your branch and open a **pull request (PR)** on GitHub. A teammate reviews it, and then it gets merged. You'll practise this with Slotify.

## 2.8 Undoing things (the safe way)

| Situation | Command |
|---|---|
| I changed a file and want to throw the changes away | `git restore file.ts` |
| I staged a file by mistake | `git restore --staged file.ts` |
| My last commit message has a typo (not pushed yet) | `git commit --amend -m "Better message"` |
| I want to undo a commit that's already pushed | `git revert <commit-id>` (creates a new "undo" commit) |
| I want to see what a file looked like 3 commits ago | `git show HEAD~3:path/to/file.ts` |

!!! warning "Never rewrite pushed history on shared branches"
    `--amend`, `rebase` and `reset --hard` rewrite history. That's fine for commits that only exist on your machine, and dangerous for commits others may already have. When in doubt, use `git revert`.

!!! interview "Interview corner"
    "What's the difference between `git merge` and `git rebase`?" At this level, a solid answer is: *both bring changes from one branch into another. Merge keeps the history exactly as it happened and adds a merge commit. Rebase replays your commits on top of the other branch, giving a straight, tidy history, but it rewrites commits, so you shouldn't rebase commits others are already using.*

!!! checkpoint "Checkpoint 2"
    1. What does `git commit` do that `git push` doesn't?
    2. You edited 3 files for 2 different reasons. How do you make two clean commits?
    3. Why is `Added stuff` a poor commit message? Rewrite it for a commit that adds input validation to the signup form.
    4. You committed a database password and pushed it. What must you do?
    5. When is `git commit --amend` safe, and when is it not?

## Tasks

!!! task "Task 2.1 · Clean up your repository · Core"
    Your repository still has loose ends from Lessons 00–02. Fix them, **one commit per logical change**:

    1. Commit the untracked files: `00-setup/solutions/answers.md`, the drills folder, `01-how-the-web-works/solutions/raw-http.mjs`, `02-typescript/`.
    2. Delete the old `experiment` branch.
    3. Push.

    **Done when:** `git status` says the working tree is clean and up to date, and `git branch` shows only `main`. {: .done }

!!! task "Task 2.2 · Branch, commit, merge · Core"
    1. Create a branch `improve-sysinfo`.
    2. On it, make **two separate commits** in `ch01/sysinfo.js`: one adding the date and time, one showing the hostname (`os.hostname()`).
    3. Switch to `main` and notice the changes are gone. Merge the branch, push, then delete the branch.

    **Done when:** `git log --oneline` shows both commits with clear imperative messages. {: .done }

!!! task "Task 2.3 · Practise undoing · Core"
    In `ch02/`, create `undo.txt` with one line and commit it. Then:

    1. Change the file, and throw the change away with `git restore`.
    2. Change it again, stage it, then unstage it with `git restore --staged`.
    3. Commit with a deliberate typo in the message, then fix it with `--amend` (before pushing).
    4. Write in `ch02/answers.md` what each command did, in your own words.

!!! task "Task 2.4 · Your first pull request · Stretch"
    Create a branch, make a small change (e.g. improve your README), push the branch (`git push -u origin branch-name`), and open a pull request on GitHub. Read your own PR's "Files changed" tab like a reviewer would, then merge it on GitHub and `git pull` locally.
