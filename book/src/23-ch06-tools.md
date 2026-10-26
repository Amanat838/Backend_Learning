---
kind: chapter
num: 6
title: "Your HTTP Toolkit: curl, DevTools, REST Client and a Raw Socket"
phase: Phase 1
time: about 4–5 hours
---
A backend engineer spends a lot of time sending requests and looking at responses. This chapter gives you three everyday tools, and then removes all the magic: you'll send an HTTP request by hand, as plain text, over a raw network connection.

!!! learn "What you'll learn"
    - curl: the universal HTTP client
    - Reading `curl -v` output
    - Browser DevTools and the Timing tab
    - REST Client `.http` files in VS Code
    - Node's `net` module and TCP sockets
    - Writing an HTTP client from scratch

## 6.1 curl

`curl` sends HTTP requests from the terminal. It's installed almost everywhere, including every Linux server you'll ever log into. **Use it in Git Bash.**

| Flag | Meaning | Example |
|---|---|---|
| `-i` | Include response headers in the output | `curl -i https://example.com` |
| `-v` | Verbose: show everything, including the request | `curl -v https://example.com` |
| `-s` | Silent: hide the progress bar | `curl -s ...` |
| `-X` | Choose the method | `-X POST`, `-X DELETE` |
| `-H` | Add a header | `-H "Content-Type: application/json"` |
| `-d` | Send a body | `-d '{"title":"hi"}'` |
| `-L` | Follow redirects | `curl -L http://github.com` |
| `-o` | Save the body to a file (`/dev/null` = throw it away) | `-o page.html` |
| `-w` | Print extra info after the response | `-w "%{http_code}\n"` |

```bash
# Read
curl -i https://jsonplaceholder.typicode.com/posts/1

# Create (POST with a JSON body)
curl -i -X POST https://jsonplaceholder.typicode.com/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"hello","body":"my first POST","userId":1}'

# Just the status code
curl -s -o /dev/null -w "%{http_code}\n" https://jsonplaceholder.typicode.com/posts/99999
```

The backslash `\` at the end of a line means "the command continues on the next line".

### Reading `curl -v`

```output
* Host example.com:443 was resolved.
* IPv6: (none)
* IPv4: 104.20.23.154, 172.66.147.243
*   Trying 104.20.23.154:443...
* Connected to example.com (104.20.23.154) port 443
> GET / HTTP/1.1
> Host: example.com
> User-Agent: curl/8.9.0
> Accept: */*
>
< HTTP/1.1 200 OK
< Content-Type: text/html; charset=utf-8
< Transfer-Encoding: chunked
< Server: cloudflare
<
```

| Line prefix | Meaning |
|---|---|
| `*` | curl telling you what it's doing: DNS results, connecting, TLS |
| `>` | What **you** sent: the request |
| `<` | What the **server** sent back: the response |

Look: DNS returned two IPv4 addresses, curl tried the first, and then the request is exactly the text format from Chapter 5.

!!! note "Where are the TLS lines?"
    On Linux and Mac, `curl -v` prints lines like `* TLSv1.3 (OUT), TLS handshake, Client hello`. On Windows, curl uses Windows' own TLS library (Schannel), which prints very little. So lines like `IPv6: (none)` or `Request completely sent off` are *not* TLS handshake lines; they're just curl's progress notes.

## 6.2 Browser DevTools

Press <kbd>F12</kbd> in Chrome and open the **Network** tab, then reload the page. Every request the page makes appears in the list.

Useful controls:

- **Fetch/XHR** filter: show only API calls (requests made by JavaScript), hiding images and CSS.
- **Preserve log**: keep requests when the page navigates.
- **Disable cache**: see what a first-time visitor experiences.
- **Throttling** ("No throttling" dropdown): simulate a slow mobile connection.

Click any request to see its details:

| Tab | Shows |
|---|---|
| **Headers** | URL, method, status code, request and response headers |
| **Payload** | The body or query parameters you sent |
| **Preview** | The response, nicely formatted (great for JSON) |
| **Response** | The raw response body |
| **Timing** | Where the time went |

### The Timing tab: where did the time go?

| Phase | What's happening | If it's big... |
|---|---|---|
| Queueing / Stalled | Waiting for the browser to start the request | Too many requests at once |
| DNS Lookup | Finding the IP address | First visit, or slow DNS |
| Initial connection | TCP handshake | Far-away server |
| SSL | TLS handshake | Far-away server, first connection |
| Request sent | Uploading the request | Large uploads |
| **Waiting for server response (TTFB)** | The server thinking: **your code, your database** | **Slow backend. That's your job to fix.** |
| Content Download | Receiving the body | Large response, slow network |

**TTFB** stands for *Time To First Byte*. When a page feels slow, this column tells you whether to blame the network or the backend.

!!! tryit "Try it"
    Open your favourite website, reload with DevTools open, and sort by the **Time** column. Click the slowest request and open **Timing**. Which phase is biggest?

## 6.3 REST Client: requests saved as files

The **REST Client** extension for VS Code lets you write requests in a `.http` file and send them with one click. Unlike curl commands in your history, these files live in your project, get committed, and act as **living documentation** of your API.

```http
@baseUrl = https://jsonplaceholder.typicode.com

### Get one post
GET {{baseUrl}}/posts/1
Accept: application/json

### Create a post
POST {{baseUrl}}/posts
Content-Type: application/json

{
  "title": "hello",
  "body": "sent from VS Code",
  "userId": 1
}

### Delete a post
DELETE {{baseUrl}}/posts/1
```

- `###` separates requests (and the text after it is a label).
- `@name = value` defines a variable; `{{name}}` uses it.
- Headers go right under the request line. **A blank line, then the body**, exactly like real HTTP.
- A **Send Request** link appears above each request. The response opens on the right.

From Chapter 13 on, every API you build gets a `requests.http` file.

## 6.4 Talking TCP with Node's `net` module

curl, the browser and REST Client all do the same thing underneath: open a TCP connection and write HTTP text into it. Node's built-in `net` module lets you do that yourself.

The pieces you need:

```js
import net from "node:net";

// 1. Open a TCP connection. The callback runs once it's connected.
const socket = net.connect({ host: "example.com", port: 80 }, () => {
  console.log("Connected!");
  // socket.write("some text") sends text to the server
});

// 2. Data can arrive in several pieces ("chunks")
socket.on("data", (chunk) => {
  // chunk is a Buffer (raw bytes); chunk.toString() turns it into text
});

// 3. The server closed the connection: everything has arrived
socket.on("end", () => {
  console.log("Server closed the connection");
});

// 4. Something went wrong (no internet, wrong host...)
socket.on("error", (err) => {
  console.error("Socket error:", err.message);
});
```

!!! idea "Events"
    Node is built around **events**: "when X happens, run this function". `socket.on("data", fn)` means "every time data arrives, call `fn`". You'll see this pattern everywhere in Node, including in HTTP servers.

!!! analogy "Analogy: a walkie-talkie channel"
    `net.connect` opens the channel. `socket.write` is you speaking. The `data` event fires each time the other side says something. The `end` event is "over and out".

Why port **80**, not 443? Port 80 is plain HTTP: no encryption, so you can write readable text directly. Port 443 would need a TLS handshake first (that's a stretch task).

!!! checkpoint "Checkpoint 6"
    1. In `curl -v` output, what do lines starting with `>` and `<` mean?
    2. A page is slow, and the Timing tab shows 1.8 s of "Waiting for server response". Whose problem is it, the network's or the backend's?
    3. Why are `.http` files better than curl commands for a project?
    4. In Node's `net` module, why might the `data` event fire more than once for one response?

## Tasks

!!! task "Task 6.1 · curl explorer · Core"
    Run each command in Git Bash and write the answers in `ch06/answers.md`:

    1. `curl -v https://example.com -o /dev/null`. Which lines did you send? Which did the server send? What's the status and `Content-Type`?
    2. `curl -i https://jsonplaceholder.typicode.com/posts/1`. List **at least six** response headers and what each is for.
    3. `curl -i https://jsonplaceholder.typicode.com/posts/99999`. What status? Why is that the right answer, rather than `200` with an empty body?
    4. The `POST` example from section 6.1. Which status, and why that one?
    5. `curl -i http://github.com`, then the same with `-L`. What changed, and why does GitHub do this?

!!! task "Task 6.2 · DevTools detective · Core"
    On any website you use, with the Network tab open:

    1. How many requests did one page load make?
    2. Filter by Fetch/XHR. Pick one JSON request: what's its URL and method? What data is in its **Preview** tab?
    3. Find a `Set-Cookie` header. What do you think that cookie is for?
    4. Find the slowest request. In its **Timing** tab, which phase took the longest, and what does that tell you?

!!! task "Task 6.3 · Your first .http file · Core"
    Create `ch06/requests.http` for `jsonplaceholder.typicode.com` with a `@baseUrl` variable and these requests: list posts, get post 1, get a post that doesn't exist, create a post, change a post's title with `PATCH`, delete a post. Send each one and note the status codes in comments.

    **Done when:** all six requests work from VS Code with one click each. {: .done }

!!! task "Task 6.4 · Speak HTTP by hand · Core"
    Write `ch06/raw-http.mjs`, an HTTP client using **only** `node:net`: no `fetch`, no `http` module, no packages. Build it in small steps, and get each step working before the next:

    1. **Connect.** Print `Connected!` when the connection to `example.com:80` opens, then close it with `socket.end()`.
    2. **Build the request.** Create a string with the request line `GET / HTTP/1.1`, a `Host: example.com` header, a `Connection: close` header, and the blank line. Print it with `console.log(JSON.stringify(request))` so you can *see* every `\r\n`.
    3. **Send it, and print the raw reply.** Write the request inside the connect callback (and remove the `socket.end()`). Print each chunk as it arrives. **You just spoke HTTP.**
    4. **Collect everything.** Add each chunk to a `raw` string. Do the work in the `end` handler.
    5. **Split head from body** at the first `\r\n\r\n`.
    6. **Parse the head.** The first line is the status line. Turn the remaining lines into an object like `{ "content-type": "text/html; charset=utf-8", ... }`. Then print the status line, the headers object and the first 200 characters of the body.

    **Done when:** `node raw-http.mjs` prints the status line, a headers object and the start of the HTML. {: .done }

!!! warning "A surprise you'll probably see"
    The body may start with a strange number, like `241`, before the HTML. That's not a bug in your code. The response has `Transfer-Encoding: chunked`: the server sends the body in pieces, and each piece starts with its size **in hexadecimal** (`241` in hex = 577 bytes), followed by `\r\n`. The body ends with a `0` chunk. Your browser and curl quietly remove these numbers for you. Now you know they're there.

!!! task "Task 6.5 · Break it on purpose · Stretch"
    Change one thing at a time in your raw client, and record what the server does:

    1. Remove the `Host` header.
    2. Use `\n` instead of `\r\n`.
    3. Change `HTTP/1.1` to `HTTP/1.0`. What happens to the chunk numbers?
    4. Accept a host and path from the command line: `node raw-http.mjs example.com /`.
    5. Switch to `node:tls` and port 443. How little do you have to change? Why?
