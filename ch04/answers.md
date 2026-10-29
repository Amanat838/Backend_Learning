# Checkpoint 4 #

Q1: What's the difference between an IP address and a port?
A: Every device on a network has an IP address and port is a separate number which specifically tells what to serve, IP is like a buildin and port is a apartment in that building.

Q2: You open http://localhost:3000 . Which computer and which program are you talking to?
A: I'm talking to my local machine because that is what localhost is and I'm talking to a program that is currently live on port 3000.

Q3: Why can a DNS change take a while to reach everyone?
A: Every DNS record is cached for sometime so time that's why when a company change it's server address some user's still see old site.

Q4: What does TCP guarantee that the raw internet doesn't?
A: TCP gaurantees a reliable connection with three way handshake at the start of the connection, also TCP numbers the data packets and make sure they recieve in the same order as they were sent. The other guarantee is completeness: if a packet gets lost, TCP notices and sends it again.

Q5: Name the three things TLS protects against.?
A: Reading, Tampering, Impersonation. In technical terms, that’s privacy, integrity and authenticity.

Q6: Why does the second page on a site usually load faster than the first?
A: Because after recieving data the browser keeps the connection open for some time to make sure that DNS, TCP and TLS steps are not repeated if request is going to the same server.


# Task 4.1

Q1: nslookup github.com : which line is the resolver, and which is GitHub's address?
A: Resolver: 192.168.100.1
Github Address: 20.207.73.82

Q2: nslookup google.com : how many addresses? Why might there be several?
A: Total 10 addresses, the reasons for serveral address are follwing:
1)Load balancing, traffic is spread on different servers. 2) Redundency, if one server is down move to the next one. 3) Speed, every user get's the server closest to him.

Q3: nslookup -type=MX gmail.com : what do the results tell you?
A: $ nslookup -type=MX gmail.com
Non-authoritative answer:
Server: UnKnown
Address: 192.168.100.1

gmail.com MX preference = 5, mail exchanger = gmail-smtp-in.l.google.com
gmail.com MX preference = 40, mail exchanger = alt4.gmail-smtp-in.l.google.com
gmail.com MX preference = 30, mail exchanger = alt3.gmail-smtp-in.l.google.com
gmail.com MX preference = 10, mail exchanger = alt1.gmail-smtp-in.l.google.com
gmail.com MX preference = 20, mail exchanger = alt2.gmail-smtp-in.l.google.com
This is the result but I don't know what it means.

Q4: nslookup localhost : what comes back, and why?
A: $ nslookup localhost
Server: UnKnown
Address: 192.168.100.1

Name: localhost
Addresses: ::1
127.0.0.1
This came back and second is information about the localhost and it's IP address, first one I don't understand. I think it tried to check on internet or in DNS and did not found localhost.