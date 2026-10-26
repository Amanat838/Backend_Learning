---
kind: chapter
num: 1
title: The Terminal, VS Code and Node.js
phase: Phase 0
time: about 2–3 hours
---
Servers don't have a mouse or windows. They have a terminal. This chapter makes the terminal feel normal, sets up your editor, and explains what Node.js actually is.

!!! learn "What you'll learn"
    - Why backend engineers live in the terminal
    - The 15 commands you'll use every day
    - Why Git Bash beats PowerShell for this course
    - What text encoding is, and why it bites
    - How to set up VS Code properly
    - What Node.js and npm really are

## 1.1 Why the terminal?

When you deploy Slotify, it will run on a Linux server in a data centre. To check logs, restart the app or fix a problem at 2 a.m., you'll connect to that server and type commands. There is no File Explorer there.

!!! analogy "Analogy"
    A graphical interface is like ordering from a menu with pictures: easy, but you can only order what's on the menu. The terminal is like talking directly to the chef. It takes some learning, but you can ask for anything, and you can write the order down (a script) and repeat it a thousand times.

## 1.2 Choose the right shell: Git Bash

A **shell** is the program inside the terminal that reads your commands. Windows has two you care about:

| Shell | What it is | Use it for |
|---|---|---|
| **PowerShell** | Windows' own shell | Windows administration |
| **Git Bash** | A Linux-style shell that came with Git | **This course.** The same commands work on Linux servers and Macs. |

**Make Git Bash your default in VS Code:** press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>, type **Terminal: Select Default Profile**, choose **Git Bash**. Open a new terminal with <kbd>Ctrl</kbd>+<kbd>`</kbd>.

!!! warning "Two PowerShell traps"
    1. In Windows PowerShell, `curl` is **not** the real curl. It's a different command with a different output. Use Git Bash, or type `curl.exe`.
    2. In Windows PowerShell, `echo "hi" > file.txt` saves the file as **UTF-16**, not UTF-8. Other tools then show garbage like `��h i`. That's exactly what happened in your Lesson 00 drills. More on this in section 1.4.

## 1.3 The everyday commands

In Git Bash, your drives live under `/c/`, `/e/` and so on. `E:\Backend_Learning` is `/e/Backend_Learning`.

### Moving around

```bash
pwd                      # Print Working Directory: where am I?
ls                       # list files
ls -la                   # list ALL files (including hidden ones like .git) with details
cd /e/Backend_Learning   # change directory
cd ch01                  # go into a folder (relative path)
cd ..                    # go up one level
cd ~                     # go to your home folder
cd -                     # go back to where you just were
```

### Creating, copying, moving, deleting

```bash
mkdir notes              # make a folder
mkdir -p a/b/c           # make nested folders in one go (-p = "parents")
touch todo.txt           # create an empty file
cp todo.txt backup.txt   # copy a file (the original stays)
cp -r a a-copy           # copy a whole folder (-r = recursive)
mv backup.txt old.txt    # rename (or move) a file (the original is gone)
mv old.txt a/b/          # move into a folder
rm old.txt               # delete a file — there is NO recycle bin
rm -r a-copy             # delete a folder and everything inside
```

!!! mistake "cp vs mv"
    `cp` makes a copy and keeps the original. `mv` moves it, so the original disappears. In your Lesson 00 drills, `notes.txt` vanished from folder `c/` because a move happened where a copy was intended.

### Reading and writing files

```bash
echo "hello" > notes.txt     # write (replaces the whole file!)
echo "world" >> notes.txt    # append a new line at the end
cat notes.txt                # print the whole file
head -n 5 big.log            # first 5 lines
tail -n 5 big.log            # last 5 lines
tail -f app.log              # keep watching the file as it grows (Ctrl+C to stop)
wc -l big.log                # count lines
```

### Searching

```bash
grep "error" app.log          # lines containing "error"
grep -i "error" app.log       # ignore upper/lower case
grep -r "TODO" src/           # search every file in a folder
grep -rn "TODO" src/          # ... and show line numbers
find . -name "*.ts"           # find files by name
```

### Combining commands with pipes

The pipe `|` sends the output of one command into the next. This is one of the most powerful ideas in computing:

```bash
cat app.log | grep "500" | wc -l      # how many lines contain "500"?
history | grep "git commit"           # which commits did I type recently?
ls -la | sort -k5 -n                  # sort files by size
```

### Keyboard shortcuts that save hours

| Keys | What they do |
|---|---|
| <kbd>Tab</kbd> | Autocomplete file and folder names. **Use it constantly.** |
| <kbd>↑</kbd> / <kbd>↓</kbd> | Scroll through previous commands |
| <kbd>Ctrl</kbd>+<kbd>R</kbd> | Search your command history |
| <kbd>Ctrl</kbd>+<kbd>C</kbd> | Stop the running program (e.g. a server) |
| <kbd>Ctrl</kbd>+<kbd>L</kbd> | Clear the screen |

!!! tryit "Try it"
    Open Git Bash and run: `cd /e/Backend_Learning && ls -la`. Can you see the hidden `.git` folder? That folder is your entire project history.

## 1.4 Text encoding: why files turn into garbage

Computers only store numbers. An **encoding** is the agreement about which numbers mean which characters.

- **UTF-8** is the standard for the web, Linux, JSON, databases, almost everything. The letter `A` is one byte; Urdu or emoji characters take 2–4 bytes.
- **UTF-16** uses at least two bytes for every character. Windows uses it internally, and old PowerShell writes files in it by default.

When a UTF-8 program reads a UTF-16 file, every second byte is a zero, and you see `t e r m i n a l` with gaps, or `��` symbols.

!!! idea "Rule"
    Everything you create in this course should be **UTF-8**. VS Code shows the encoding in the bottom-right status bar. Click it to change it.

## 1.5 Set up VS Code

Install these extensions (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>X</kbd>):

| Extension | Why |
|---|---|
| **ESLint** | Warns about likely bugs as you type |
| **Prettier** | Formats your code automatically |
| **Error Lens** | Shows errors right on the line, in red |
| **REST Client** (Huachao Mao) | Send HTTP requests from `.http` files. You'll use it from Chapter 6 on. |
| **GitLens** (optional) | Shows who changed each line and when |

Then turn on **Format On Save**: <kbd>Ctrl</kbd>+<kbd>,</kbd>, search "format on save", tick it.

Shortcuts worth learning now:

| Keys | Action |
|---|---|
| <kbd>Ctrl</kbd>+<kbd>P</kbd> | Open any file by typing its name |
| <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> | Command palette: every VS Code command |
| <kbd>F12</kbd> | Go to the definition of a function or type |
| <kbd>F2</kbd> | Rename a variable everywhere |
| <kbd>Ctrl</kbd>+<kbd>D</kbd> | Select the next match (multi-cursor editing) |
| <kbd>Alt</kbd>+<kbd>↑</kbd>/<kbd>↓</kbd> | Move a line up or down |
| <kbd>Ctrl</kbd>+<kbd>/</kbd> | Comment or uncomment lines |

## 1.6 What is Node.js?

JavaScript was born inside web browsers. In 2009, Node.js took Chrome's JavaScript engine (called **V8**) out of the browser and gave it new powers: reading files, opening network connections, starting processes. Suddenly JavaScript could run servers.

| | JavaScript in the browser | JavaScript in Node.js |
|---|---|---|
| Engine | V8 (in Chrome) | V8 (the same one) |
| Can touch the page (`document`, `window`) | Yes | No, there is no page |
| Can read and write files | No (it's sandboxed for safety) | Yes, `node:fs` |
| Can open network ports | No | Yes, `node:http`, `node:net` |
| Can see the operating system | Very little | Yes, `process`, `node:os` |

!!! idea "Same language, different environment"
    The language is identical. What changes are the **APIs** around it. The browser gives you the page; Node gives you the operating system.

## 1.7 npm: the package manager

**npm** installs code other people wrote (packages) and manages your project's settings.

```bash
npm init -y               # create package.json (your project's ID card)
npm install express       # add a dependency (code your app needs to run)
npm install -D typescript # add a dev dependency (only needed while developing)
npm run check             # run a script defined in package.json
npx tsc --version         # run a tool from node_modules without installing it globally
```

- `package.json` lists your dependencies and scripts. **Commit it.**
- `package-lock.json` records the exact versions installed. **Commit it.**
- `node_modules/` holds the downloaded code. It's huge and can always be rebuilt with `npm install`. **Never commit it.**

## 1.8 Your first Node program

```js
// hello.js
const name = process.argv[2] ?? "stranger";
console.log(`Hello, ${name}!`);
console.log("Node version:", process.version);
```

```bash
node hello.js Amanat
```

```output
Hello, Amanat!
Node version: v24.15.0
```

`process.argv` is an array of the command-line words. Try `console.log(process.argv)` to see what's in it. The `??` operator means "use the right side if the left side is `null` or `undefined`".

!!! checkpoint "Checkpoint 1"
    1. What's the difference between `cp a.txt b.txt` and `mv a.txt b.txt`?
    2. What does `cat app.log | grep 404 | wc -l` tell you?
    3. Why might a file written by Windows PowerShell look like garbage on a Linux server?
    4. Node.js and Chrome use the same engine. Name two things Node can do that a web page can't.
    5. Which of these do you commit: `package.json`, `package-lock.json`, `node_modules/`?

## Tasks

!!! task "Task 1.1 · Terminal drills · Core"
    Using **only Git Bash** (no File Explorer, no VS Code sidebar), inside `ch01/`:

    1. Create the folders `drills/a/b/c` in one command.
    2. Create `drills/a/b/c/notes.txt` containing `terminal is fine actually`.
    3. Append a second line, `pipes are cool`, with `>>`.
    4. **Copy** it to `drills/a/copy.txt`, then **rename** that copy to `renamed.txt`.
    5. Use `grep -r` to find every file under `drills/` that contains `actually`.
    6. Count the lines in `notes.txt` with `wc -l`.
    7. Save your commands: `history | tail -n 20 > drills.md`, then tidy the file.

    **Done when:** `notes.txt` *and* `renamed.txt` both exist, `cat` shows clean text (no `��`), and `drills.md` lists your commands. {: .done }

!!! task "Task 1.2 · System info script · Core"
    Create `ch01/sysinfo.js` that prints:

    ```output
    Hello, Amanat!
    Node version: v24.15.0
    Platform: win32
    CPU cores: 8
    Memory: 4.5 GB free of 15.8 GB
    Uptime of this process: 0.03 s
    ```

    - The name comes from the command line: `node sysinfo.js Amanat`. With no name, print `Hello, stranger!`.
    - Memory must show **one decimal place**.
    - Write a small function `toGB(bytes)` instead of repeating the maths.
    - Use the Node docs to find `os.cpus()`, `os.freemem()`, `os.totalmem()` and `process.uptime()`.

    **Done when:** `node sysinfo.js` and `node sysinfo.js "Syed Amanat"` both print correctly formatted output. {: .done }

!!! task "Task 1.3 · Pipe detective · Stretch"
    Run `ls -la /c/Windows/System32 | wc -l`. What does the number mean? Then find the 5 largest files in that folder with one pipeline (hint: `sort` and `head`). Write your commands and an explanation in `ch01/answers.md`.
