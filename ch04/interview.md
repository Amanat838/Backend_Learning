


Q: What happens when you type a URL and press Enter?

A: First, the browser splits the URL into its parts: the scheme (https), the host (shop.pk) and the path (/cart). Then it needs the host’s IP address, so it checks its own cache, then the operating system’s cache, and finally asks a DNS resolver, which returns the IP address.

Next, the browser opens a TCP connection to that IP on port 443 using a three-way handshake. TCP guarantees that the data arrives completely and in order. Because the scheme is HTTPS, a TLS handshake follows: the browser checks the server’s certificate to make sure it’s really shop.pk, and both sides agree on encryption keys.

Once the connection is secure, the browser sends an HTTP request containing the method and path, like GET /cart, plus headers such as cookies.

On the server, the router matches the request to the right code. That code runs the business logic and may query a database, for example “which items are in this user’s cart?” The server then sends back a response with a status code like 200 OK, headers like Content-Type, and a body containing the HTML.

Finally, the browser renders the HTML. While reading it, it finds links to CSS, JavaScript and images, and fetches them over the same connection, so DNS, TCP and TLS don’t have to happen again. That reuse is called keep-alive, and together with caching, it’s why the second page loads faster than the first.
