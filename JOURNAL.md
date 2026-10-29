## 2026-10-28
- Learned: reading docs, reading + understanding errors, debugging methods.
- Confused by: no confusion.
- Fixed: deleted new branch
- Next: Chapter 3, Task 3.2.

## 2026-10-28 · Task 3.3 (docs scavenger hunt)
- Learned: `path.join("a", "..", "b")` returns `b`, not `a/b`. `..` cancels the folder before it, like `cd a`, `cd ..`, `cd b`. The same trick (`../../.env`) is how path traversal attacks escape an uploads folder.
- Learned: `find` returns the first match (or `undefined`); `filter` returns every match (or `[]`).
- Learned: `String(9).padStart(2, "0")` gives `"09"`, handy for clock times like 09:05.
- Learned: `node --env-file=.env app.js` loads environment variables; `--env-file-if-exists` skips a missing file quietly.
- Confused by: I ignored what `..` does and guessed `a/b`.
- Confused by: I described `padStart` as "padding 2 strings". It pads the start of one string until it reaches the target length.
- Fixed: nothing broke this session.
- Next: Task 3.4 (LinkedIn post), then Chapter 4.

## 2026-10-29 · Checkpoint 4 (journey of a request)
- Learned: IP address = which computer (the building), port = which program on it (the apartment). They are two separate numbers written together, like `142.250.181.46:443`.
- Learned: `localhost` is `127.0.0.1`, my own machine. If nothing listens on the port, I get "connection refused".
- Learned: DNS answers are cached for their TTL in the browser, the OS and the ISP, so a change takes time to reach everyone.
- Learned: TCP guarantees everything arrives, in order, or I get an error. Lost packets are sent again.
- Learned: keep-alive reuses the connection, so DNS, TCP and TLS don't repeat on the second page.
- Confused by: I thought the port was part of the IP address.
- Confused by: I listed the three-way handshake as a TCP guarantee. It's only how the connection starts.
- Fixed: my commit `cd00805` said it added ch02 and JOURNAL.md, but only ch03 was staged. Check `git status` before every commit.
- Next: Chapter 4 tasks (4.1 DNS explorer).

## 2026-10-29 · Task 4.1 (DNS explorer)
- Learned: my resolver is my home router, `192.168.100.1` (192.168.x.x is a private address). GitHub resolved to `20.207.73.82`.
- Learned: google.com returns several addresses (load balancing, redundancy, nearby servers), and the list changes depending on when and where you ask. `2a00:...` is IPv6; `192.179.x.x` is IPv4.
- Learned: "Non-authoritative answer" means the answer came from a cache, not from the domain's own DNS servers.
- Learned: MX records list the servers that receive email for a domain. Lower preference = tried first (5, then 10, 20…); the rest are backups. nslookup prints them out of order.
- Learned: DNS has record types: A (IPv4), AAAA (IPv6), MX (mail).
- Confused by: what MX results mean.
- Confused by: the `Server:`/`Address:` block at the top of nslookup. It's just which DNS server answered, printed every time. I thought the localhost lookup had failed, but it found `::1` and `127.0.0.1`.
- Fixed: nothing broke. (Task 4.1 answers should move from interview.md to answers.md.)
- Next: Task 4.2 (explain it like an interview).

## 2026-10-29 · Task 4.2 (first draft, "what happens when you press Enter?")
- Learned: the DNS lookup order is browser cache → OS cache → resolver. Mentioning the caches is a strong detail in interviews.
- Learned: the full answer has 7 steps: parse URL → DNS → TCP → TLS → HTTP request → server builds the response → browser renders and fetches extra files.
- Confused by: I stopped after TLS. At that point the browser has a connection but hasn't asked for anything yet.
- Fixed: nothing yet. My draft needs steps 1, 5, 6 and 7, especially step 6 (the server, i.e. the backend part), in 8–12 sentences.
- Next: finish Task 4.2 and practise saying it out loud in under 2 minutes.

## 2026-10-29 · Task 4.2 (missing steps answered)
- Learned: the browser splits a URL into scheme (`https` → port 443 + TLS), host (for DNS) and path (sent to the server).
- Learned: an HTTP request starts with the method + path line (`GET /cart HTTP/1.1`), then headers, plus a body for things like POST. The query (`?page=2`) is just an optional part of the path.
- Learned: a response has three parts: status code, headers, body.
- Learned: the browser finds the extra files by reading `<link>`, `<script>` and `<img>` tags, then fetches them over the same connection (keep-alive).
- Confused by: I named "query" as the third part of a request instead of the path, and I forgot headers in the response.
- Fixed: nothing broke.
- Next: merge everything into one 8–12 sentence answer in interview.md and say it out loud without notes.
