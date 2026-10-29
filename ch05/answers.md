# CHECKPOINT 5

Q1: What separates the headers from the body in an HTTP message?
A: A empty line (\r\n\r\n)

Q2: Is the #fragment part of a URL sent to the server?
A: No, fragment is only read by browser.

Q3: Why must a GET handler never change data?
A: magine Slotify had a cancel link like this:

GET /bookings/7/cancel

Now a customer pastes that link into WhatsApp to ask a friend about it. WhatsApp sends a GET request to show a link preview, and the booking is cancelled. Nobody clicked anything.

The rule exists because the whole web assumes GET is safe to call at any time: link previews, search engine crawlers, browsers prefetching links you might click, caches retrying requests. They all send GET freely, because “GET just looks, it never touches”.

Q4: Which status code: (a) booking created, (b) slot already taken, (c) not logged in, (d) logged in but
it's someone else's booking, (e) booking deleted, nothing returned?
A: (a) 201
(b) 409
(c) 401
(d) 403
(e) 204

Q5: A request arrives with ?page=3 . What JavaScript type is 3 when it reaches your server?
A: string

Q6: How does a server "remember" a logged-in user if HTTP is stateless?
A: Using cookeies or authentication headers.
