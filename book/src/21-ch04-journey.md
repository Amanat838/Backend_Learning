---
kind: chapter
num: 4
title: "The Journey of a Request: IP, DNS, TCP and TLS"
phase: Phase 1
time: about 2–3 hours
---
You type `https://slotify.app/services` and press Enter. Half a second later, a page appears. In between, at least four separate conversations happen between computers. This chapter walks through each one.

!!! learn "What you'll learn"
    - Clients, servers, IP addresses and ports
    - How DNS turns names into addresses
    - How TCP makes a reliable connection
    - What TLS (the "S" in HTTPS) protects
    - The full journey, step by step
    - The classic interview question

## 4.1 Clients and servers

A **server** is just a program that **waits** for messages on a network port. A **client** is a program that **starts** a conversation by sending a request. Browsers, mobile apps, `curl` and even other servers can all be clients.

Your job as a backend engineer is to write the server side: receive a request, do the work (check the data, talk to the database, apply business rules), and send back a response.

## 4.2 IP addresses and ports

Every device on a network has an **IP address**, like a postal address for computers.

- **IPv4** looks like `20.207.73.82`: four numbers from 0 to 255.
- **IPv6** looks like `2606:4700::6810:84e5`. It's longer, because the world ran out of IPv4 addresses.

Some addresses are special:

| Address | Meaning |
|---|---|
| `127.0.0.1` or `localhost` | "This computer." Used when your browser talks to the server you're running locally. |
| `192.168.x.x`, `10.x.x.x` | **Private** addresses inside a home or office network. Usually your router or devices behind it. Never a public website. |

!!! mistake "Lesson 01 flashback"
    When you ran `nslookup github.com`, you got two addresses: `192.168.100.1` and `20.207.73.82`. The first one is **your router**, the DNS server that answered your question (the `Server:` line). GitHub's address is the second one.

One computer runs many programs, so an IP address isn't enough. A **port** is a number from 0 to 65535 that says *which program* should receive the message.

!!! analogy "Analogy: an apartment building"
    The IP address is the building's street address. The port is the apartment number. The postman (the network) delivers to the building; the port decides which apartment gets the letter.

| Port | Usually used by |
|---|---|
| 80 | HTTP (plain, unencrypted web) |
| 443 | HTTPS (encrypted web) |
| 22 | SSH (remote terminal access to servers) |
| 5432 | PostgreSQL (you'll meet it in Book 2) |
| 6379 | Redis |
| 3000, 8080 | Popular choices for local development servers |

So `http://localhost:3000` means: "connect to *this* computer, to the program listening on port 3000, and speak HTTP."

## 4.3 DNS: the internet's phone book

People remember names like `github.com`. Computers need IP addresses. **DNS (Domain Name System)** translates one into the other.

!!! analogy "Analogy: your phone's contacts"
    You tap "Ammi" and your phone dials `0300-1234567`. You never type the number. DNS does the same for websites: you type the name, and DNS finds the number.

What happens when you look up `github.com`:

1. **Browser cache.** Has the browser looked this up recently? If yes, done.
2. **Operating system cache.** Has Windows looked it up recently?
3. **Resolver.** Ask the DNS resolver, usually your router, your internet provider, or a public one like `1.1.1.1` or `8.8.8.8`.
4. If the resolver doesn't know, it asks a **root server** ("who handles `.com`?"), then a **`.com` server** ("who handles `github.com`?"), then GitHub's own **authoritative server** ("what's the address of `github.com`?").
5. The answer travels back and **is cached at every step** for a while.

That "while" is the **TTL (time to live)**. Every DNS record says how many seconds it may be cached. This is why, when a company changes its server address, some users still reach the old server for a few minutes or hours.

### Common record types

| Record | Maps | Example |
|---|---|---|
| `A` | name → IPv4 address | `github.com → 20.207.73.82` |
| `AAAA` | name → IPv6 address | |
| `CNAME` | name → another name (an alias) | `www.slotify.app → slotify.app` |
| `MX` | domain → mail server | Where to deliver email for `@slotify.app` |
| `TXT` | domain → any text | Used to prove you own a domain |

!!! idea "Why big sites return several IP addresses"
    `nslookup google.com` often returns several addresses. This gives **load balancing** (spreading users across many servers), **redundancy** (if one server is down, try the next) and **speed** (users get a server near them).

## 4.4 TCP: a reliable conversation

Now the browser knows the IP address. Next it opens a **TCP connection** to that address and port.

The internet itself is unreliable. Data travels in small **packets**, and packets can get lost, duplicated or arrive in the wrong order. **TCP (Transmission Control Protocol)** sits on top and guarantees that what you send arrives **complete and in order**, or you get an error. It does this by numbering packets, and resending any that aren't acknowledged.

Before sending data, TCP does a **three-way handshake**:

1. Client → server: **SYN** ("Hello, can we talk?")
2. Server → client: **SYN-ACK** ("Yes, I hear you. Can you hear me?")
3. Client → server: **ACK** ("Yes. Let's talk.")

!!! analogy "Analogy: a phone call"
    "Hello?" "Hi, it's me, can you hear me?" "Yes, I can hear you." Only then does the real conversation start. If a word gets lost on a bad line, you say "sorry, can you repeat that?" That's TCP.

There's also **UDP**, which skips the handshake and the guarantees. It's faster but unreliable, so it suits things where speed matters more than perfection: video calls, online games, and DNS lookups. (HTTP/3 also runs over UDP, with its own reliability on top.)

## 4.5 TLS: the "S" in HTTPS

Plain HTTP travels as readable text. Anyone between you and the server (the café Wi-Fi, a compromised router) could read your password or change the page.

**TLS (Transport Layer Security)** fixes this. After the TCP handshake, client and server do a **TLS handshake**:

1. The server shows its **certificate**: a digital ID card saying "I am `github.com`", signed by a trusted **Certificate Authority**.
2. The browser checks the signature, the name and the expiry date.
3. Both sides agree on secret keys, and from then on **everything is encrypted**.

!!! analogy "Analogy: a sealed envelope with an ID check"
    Before you hand over a sealed envelope, you check the courier's official ID. TLS checks the server's ID (the certificate), then seals everything (encryption) so nobody on the way can read or change it.

TLS protects against **reading** (privacy), **tampering** (integrity) and **impersonation** (authenticity). That's why `http://github.com` answers with **`301 Moved Permanently`** and a `Location: https://github.com/` header. GitHub refuses to talk unencrypted and sends you to the secure version.

## 4.6 The whole journey

<figure>
<svg viewBox="0 0 700 470" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, sans-serif" font-size="12">
  <defs>
    <marker id="a1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#3b5bdb"/></marker>
    <marker id="a2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#2b8a3e"/></marker>
  </defs>
  <g text-anchor="middle" font-weight="700" font-size="13" fill="#1d2433">
    <rect x="40" y="10" width="140" height="36" rx="6" fill="#f0f4ff" stroke="#3b5bdb"/><text x="110" y="33">Your browser</text>
    <rect x="280" y="10" width="140" height="36" rx="6" fill="#fff8eb" stroke="#c77700"/><text x="350" y="33">DNS resolver</text>
    <rect x="520" y="10" width="140" height="36" rx="6" fill="#effaf1" stroke="#2b8a3e"/><text x="590" y="33">Server :443</text>
  </g>
  <g stroke="#c3cad8" stroke-width="1.5" stroke-dasharray="3 4"><line x1="110" y1="46" x2="110" y2="460"/><line x1="350" y1="46" x2="350" y2="460"/><line x1="590" y1="46" x2="590" y2="460"/></g>
  <g fill="#7b8496" font-size="10.5" font-weight="700" letter-spacing="1"><text x="8" y="82">1 DNS</text><text x="8" y="158">2 TCP</text><text x="8" y="262">3 TLS</text><text x="8" y="352">4 HTTP</text></g>
  <g stroke-width="1.8" fill="none">
    <line x1="112" y1="75" x2="346" y2="75" stroke="#3b5bdb" marker-end="url(#a1)"/>
    <line x1="348" y1="105" x2="114" y2="105" stroke="#2b8a3e" marker-end="url(#a2)"/>
    <line x1="112" y1="145" x2="586" y2="145" stroke="#3b5bdb" marker-end="url(#a1)"/>
    <line x1="588" y1="172" x2="114" y2="172" stroke="#2b8a3e" marker-end="url(#a2)"/>
    <line x1="112" y1="199" x2="586" y2="199" stroke="#3b5bdb" marker-end="url(#a1)"/>
    <line x1="112" y1="245" x2="586" y2="245" stroke="#3b5bdb" marker-end="url(#a1)"/>
    <line x1="588" y1="275" x2="114" y2="275" stroke="#2b8a3e" marker-end="url(#a2)"/>
    <line x1="112" y1="340" x2="586" y2="340" stroke="#3b5bdb" marker-end="url(#a1)"/>
    <line x1="588" y1="430" x2="114" y2="430" stroke="#2b8a3e" marker-end="url(#a2)"/>
  </g>
  <g fill="#1d2433" text-anchor="middle" style="paint-order:stroke;stroke:#ffffff;stroke-width:5px;stroke-linejoin:round">
    <text x="230" y="69">"What is the IP of slotify.app?"</text>
    <text x="230" y="99">"104.21.48.10" (cached for its TTL)</text>
    <text x="350" y="139">SYN</text><text x="350" y="166">SYN-ACK</text><text x="350" y="193">ACK  (connection open)</text>
    <text x="350" y="239">"Hello! Here's what encryption I support"</text>
    <text x="350" y="269">certificate "I am slotify.app" + key exchange</text>
    <text x="350" y="300" fill="#7b8496" font-style="italic">from here on, everything is encrypted</text>
    <text x="350" y="334" font-family="Cascadia Mono, Consolas, monospace">GET /services HTTP/1.1</text>
    <text x="350" y="424" font-family="Cascadia Mono, Consolas, monospace">HTTP/1.1 200 OK  + JSON body</text>
  </g>
  <rect x="525" y="355" width="130" height="55" rx="6" fill="#ffffff" stroke="#2b8a3e"/>
  <g text-anchor="middle" font-size="11" fill="#1d2433"><text x="590" y="375" font-weight="700">YOUR CODE RUNS</text><text x="590" y="392">routing, validation,</text><text x="590" y="405">database, response</text></g>
</svg>
<figcaption>Four conversations: DNS finds the address, TCP opens a reliable line, TLS secures it, HTTP carries the actual request.</figcaption>
</figure>

After the response, the browser keeps the connection open for a while (**keep-alive**), so the next requests to the same server skip the DNS, TCP and TLS steps. That's a big part of why the *second* page on a website loads faster.

### HTTP versions in one paragraph

**HTTP/1.1** (1997) sends readable text, one request at a time per connection. **HTTP/2** (2015) sends the same information as binary frames and allows many requests at once over one connection. **HTTP/3** (2022) runs over a UDP-based protocol called QUIC to connect faster and cope better with bad networks. The concepts (methods, status codes, headers) are identical in all three, so you learn them once. In Chapter 6 you'll speak HTTP/1.1 by hand.

!!! interview "Interview corner: “What happens when you type a URL and press Enter?”"
    This is one of the most common junior interview questions. A strong answer walks through the layers in order, with one or two sentences each:

    1. The browser **parses the URL** (scheme, host, path).
    2. **DNS** resolves the host name to an IP address, using caches first.
    3. The browser opens a **TCP connection** to that IP on port 443 (three-way handshake).
    4. A **TLS handshake** verifies the certificate and sets up encryption.
    5. The browser sends an **HTTP request** (method, path, headers).
    6. The **server** routes the request to the right code, which may query a database, and builds a **response** (status code, headers, body).
    7. The browser **renders** the response, and fetches extra files (CSS, JavaScript, images), often reusing the same connection.

    Bonus points: mention caching (DNS TTL, browser cache), load balancers, and keep-alive.

!!! checkpoint "Checkpoint 4"
    1. What's the difference between an IP address and a port?
    2. You open `http://localhost:3000`. Which computer and which program are you talking to?
    3. Why can a DNS change take a while to reach everyone?
    4. What does TCP guarantee that the raw internet doesn't?
    5. Name the three things TLS protects against.
    6. Why does the second page on a site usually load faster than the first?

## Tasks

!!! task "Task 4.1 · DNS explorer · Core"
    In `ch04/answers.md`, record and explain:

    1. `nslookup github.com`: which line is the resolver, and which is GitHub's address?
    2. `nslookup google.com`: how many addresses? Why might there be several?
    3. `nslookup -type=MX gmail.com`: what do the results tell you?
    4. `nslookup localhost`: what comes back, and why?

!!! task "Task 4.2 · Explain it like an interview · Core"
    Write your answer to **"What happens when you type a URL and press Enter?"** in `ch04/interview.md`, in your own words, in 8–12 sentences. Use the interview corner as a guide, but don't copy it.

    Then say it **out loud** in under 2 minutes (record yourself on your phone if you can). Saying it is a different skill from writing it, and interviews need the spoken version.

    **Done when:** you can explain all seven steps without looking at your notes. {: .done }

!!! task "Task 4.3 · Watch the connection · Stretch"
    1. Run `curl -v https://example.com -o /dev/null` in Git Bash. In the `*` lines, find the IP addresses DNS returned and the one curl actually connected to. (On Windows, curl uses the built-in Windows TLS library, called Schannel, which prints very few TLS details. That's normal.)
    2. Open `https://example.com` in Chrome, click the icon left of the address, then **Connection is secure → Certificate is valid**. Write down who the certificate was issued to, who issued it, and when it expires.
    3. Explain in one sentence each what the browser checks before trusting that certificate.
