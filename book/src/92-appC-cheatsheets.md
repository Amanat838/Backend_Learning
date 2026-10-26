---
kind: appendix
num: C
title: Cheat Sheets
---
Print these pages, or keep them open in a second window.

## Terminal (Git Bash)

| Command | Does |
|---|---|
| `pwd` · `ls -la` · `cd dir` · `cd ..` · `cd -` | where am I · list all · enter · up · back |
| `mkdir -p a/b` · `touch f` | make folders · make an empty file |
| `cp a b` · `cp -r d e` · `mv a b` · `rm f` · `rm -r d` | copy · copy folder · move/rename · delete · delete folder |
| `cat f` · `head -n 5 f` · `tail -n 5 f` · `tail -f f` | print · first lines · last lines · follow |
| `echo "x" > f` · `echo "x" >> f` | write · append |
| `grep -rn "x" dir` · `find . -name "*.ts"` | search contents · find files |
| `a \| b` · `wc -l` · `sort -n` · `head` | pipe · count lines · sort numbers · first lines |
| <kbd>Tab</kbd> · <kbd>Ctrl</kbd>+<kbd>R</kbd> · <kbd>Ctrl</kbd>+<kbd>C</kbd> · <kbd>Ctrl</kbd>+<kbd>L</kbd> | complete · search history · stop · clear |
| `echo $?` | exit code of the last command |

## Git

| Command | Does |
|---|---|
| `git status` · `git diff` · `git diff --staged` | what changed · unstaged changes · staged changes |
| `git add <file>` · `git commit -m "Add ..."` · `git push` | stage · snapshot · upload |
| `git log --oneline --graph` | compact history |
| `git switch -c name` · `git switch main` · `git merge name` · `git branch -d name` | new branch · go back · merge · delete branch |
| `git pull` | download and merge others' commits |
| `git restore f` · `git restore --staged f` | discard changes · unstage |
| `git commit --amend -m "..."` | fix the last commit (only if not pushed) |
| `git revert <id>` | undo a pushed commit safely |

**Commit messages:** imperative ("Add", "Fix", "Remove"), say what and why, one logical change per commit.

## HTTP status codes

| Code | When |
|---|---|
| `200 OK` | success with a body |
| `201 Created` | created; add a `Location` header |
| `204 No Content` | success, no body (e.g. delete) |
| `301` / `302` | moved permanently / temporarily (redirects) |
| `400 Bad Request` | invalid input or malformed JSON |
| `401 Unauthorized` | not logged in |
| `403 Forbidden` | logged in, not allowed |
| `404 Not Found` | it doesn't exist |
| `409 Conflict` | clashes with current state (duplicate, slot taken) |
| `410 Gone` | existed, but permanently removed or expired |
| `413` / `415` | body too large / unsupported content type |
| `422 Unprocessable Content` | valid format, breaks a business rule |
| `429 Too Many Requests` | rate limit exceeded |
| `500 Internal Server Error` | unexpected bug |
| `503 Service Unavailable` | deliberately unavailable (maintenance, overload) |

## REST endpoints

| Operation | Request | Success |
|---|---|---|
| List | `GET /v1/things?page=1&pageSize=20&sort=-createdAt` | `200` `{ items, page, pageSize, total, totalPages }` |
| Get | `GET /v1/things/:id` | `200` |
| Create | `POST /v1/things` | `201` + `Location` |
| Update | `PATCH /v1/things/:id` | `200` updated object |
| Replace | `PUT /v1/things/:id` | `200` |
| Delete | `DELETE /v1/things/:id` | `204` |
| Action | `POST /v1/things/:id/cancel` | `200` |

## TypeScript

```ts
type Status = "pending" | "confirmed";                    // union of literals
type Item = { readonly id: string; name: string; note?: string };
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

function first<T>(xs: T[]): T | undefined { return xs[0]; }          // generic
function byId<T extends { id: string }>(xs: T[], id: string) { /*...*/ } // constraint

type Create = Omit<Item, "id">;      type Update = Partial<Create>;
type Summary = Pick<Item, "id" | "name">;   type Counts = Record<string, number>;

const ROLES = ["a", "b"] as const;   type Role = (typeof ROLES)[number];
function isRole(v: unknown): v is Role { return ROLES.some((r) => r === v); }

// exhaustive switch
default: { const unreachable: never = value; throw new Error(`Unhandled ${unreachable}`); }
```

**Narrowing:** `typeof x === "string"` · `x === undefined` · `if (x)` · `"field" in obj` · `Array.isArray(x)` · `x instanceof Error`

## Node.js

```ts
import { readFile, writeFile, mkdir, rename } from "node:fs/promises";
import path from "node:path";
import { parseArgs } from "node:util";
import { randomUUID, randomInt } from "node:crypto";

const file = path.join(import.meta.dirname, "..", "data", "x.json");
const text = await readFile(file, "utf8");
await writeFile(tmp, JSON.stringify(data, null, 2)); await rename(tmp, file);
process.exitCode = 1;  console.error("message");
const [a, b] = await Promise.all([taskA(), taskB()]);
```

```bash
node --watch src/server.ts             # restart on save
node --env-file=.env src/server.ts     # load environment variables
npx tsc --noEmit                       # type-check
```

## Express and Zod

```ts
const app = express();
app.use(requestLogger);
app.use(express.json());
app.use("/v1/books", bookRouter);
app.use(notFoundHandler);
app.use(errorHandler);                 // (err, req, res, next): four parameters

router.post("/", validateBody(createSchema), controller.create);
res.status(201).location(`/v1/books/${id}`).json(book);
res.status(204).end();
res.redirect(302, url);

const schema = z.object({
  name: z.string().trim().min(1).max(100),
  count: z.number().int().min(0),
  kind: z.enum(["a", "b"]),
  email: z.email().optional(),
  startsAt: z.iso.datetime(),
});
const query = z.object({ page: z.coerce.number().int().min(1).default(1) });
type Input = z.infer<typeof schema>;
const result = schema.safeParse(data);   // result.success ? result.data : result.error.issues
```
