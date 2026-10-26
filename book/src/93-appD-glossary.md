---
kind: appendix
num: D
title: Glossary
---
| Term | Meaning |
|---|---|
| **API** | Application Programming Interface: a defined way for programs to talk to each other. For us, usually a set of HTTP endpoints. |
| **Atomic write** | Writing to a temporary file and then renaming it, so a crash never leaves a half-written file. |
| **Backpressure** | When a stream's destination is full, the source pauses until it catches up. |
| **Body** | The data part of an HTTP message, after the headers and the blank line. |
| **Breakpoint** | A marker that pauses your program at a line so you can inspect it in a debugger. |
| **Buffer** | Node's type for raw bytes. |
| **Callback** | A function you pass to another function, to be called later. |
| **Certificate** | A digital ID card a server shows during the TLS handshake to prove its identity. |
| **Client** | The program that starts a request (browser, app, curl, another server). |
| **Controller** | The layer that translates between HTTP (`req`/`res`) and the service layer. |
| **CRUD** | Create, Read, Update, Delete: the four basic operations on data. |
| **Discriminated union** | A union of object types that share a tag field with a different literal value in each. |
| **DNS** | Domain Name System: translates names like `github.com` into IP addresses. |
| **Endpoint** | One method and path combination your API responds to, like `POST /v1/bookings`. |
| **Environment variable** | A setting passed to a program from outside, like `PORT=3000`. |
| **Event loop** | Node's mechanism for running callbacks when the call stack is empty. |
| **Exit code** | The number a program returns when it ends: `0` for success, anything else for failure. |
| **Generic** | A type or function with a type parameter (`<T>`), so it works with many types. |
| **Header** | A `Name: value` line in an HTTP message that carries metadata. |
| **Idempotent** | Doing it once or many times leaves the same final state. `PUT` and `DELETE` are; `POST` isn't. |
| **IP address** | A device's address on a network, like `20.207.73.82`. |
| **ISO 8601** | The standard date format: `2026-11-03T09:30:00Z`. |
| **JSON** | JavaScript Object Notation: the standard text format for API data. |
| **Keep-alive** | Reusing a TCP connection for several HTTP requests. |
| **Latency** | How long something takes, usually measured in milliseconds. |
| **Mass assignment** | A security hole where a client sets fields it shouldn't (like `isAdmin`) because all input is copied blindly. |
| **Microtask** | A queued callback (promise callbacks, code after `await`) that runs before the next timer or I/O task. |
| **Middleware** | A function in the request pipeline that either passes the request on (`next()`) or responds. |
| **Narrowing** | TypeScript working out a more specific type inside an `if` or `switch`. |
| **Non-blocking I/O** | Starting slow input/output work and carrying on with other work until it's done. |
| **p95 / percentile** | The value that 95% of measurements fall below. A better measure of "slow" than the average. |
| **Pagination** | Returning a big list in pages, with `page` and `pageSize`. |
| **Port** | A number that identifies a program on a computer, like `443` or `3000`. |
| **Promise** | An object representing a result that will arrive later: pending, fulfilled or rejected. |
| **Pure function** | A function whose result depends only on its inputs and which has no side effects. |
| **Query string** | The part of a URL after `?`: `?page=2&sort=-createdAt`. |
| **Repository** | The layer that stores and loads data. |
| **Resource** | A thing your API exposes, named by a URL: a booking, a service. |
| **REST** | An API style where URLs name resources and HTTP methods say what to do with them. |
| **Route** | A mapping from a method and path to the code that handles it. |
| **Schema** | A description of what valid data looks like (here, with Zod). |
| **Semantic versioning** | `MAJOR.MINOR.PATCH`: the first number changes for breaking changes. |
| **Server** | A program that waits for requests and sends responses. |
| **Service (layer)** | The layer that holds business rules and knows nothing about HTTP. |
| **Stack trace** | The list of function calls that led to an error, newest first. |
| **Stateless** | Each request stands alone; the server doesn't remember earlier requests. |
| **Status code** | The three-digit number summarising an HTTP response, like `404`. |
| **Stream** | Data processed piece by piece as it arrives, instead of all at once. |
| **TCP** | The protocol that provides reliable, ordered connections. |
| **TLS** | The encryption layer behind HTTPS. |
| **TTFB** | Time To First Byte: how long the server took before it started responding. |
| **TTL** | Time To Live: how long a cached value (like a DNS answer) stays valid. |
| **Type guard** | A function returning `value is Type`, which narrows a value when it returns `true`. |
| **UTC** | Coordinated Universal Time: the time zone servers use for storing times. |
| **UTF-8** | The standard text encoding for the web, Linux and JSON. |
| **Validation** | Checking at runtime that incoming data has the right shape and values. |
