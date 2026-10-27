# Checkpoint 1 #

Q1: What's the difference between cp a.txt b.txt and mv a.txt b.txt ?
A: cp a.txt b.txt copies the file while preserving original while mv a.txt b.txt move the file permanently removing the original.

Q2: cat app.log | grep 404 | wc -l tell you?
A: wc -l is used for counting lines, grep is used for search a text, cat is used to print the file, so this case is trying to find how many lines contain 404 in app.log file.

Q3: Why might a file written by Windows PowerShell look like garbage on a Linux server?
A: Because linux uses UTF-8 which uses 1 byte for English characters and can use upto 2-4 for urdr, emoji or any other language and windows powershell uses UTF-16 which uses 2 bytes for every character.

Q4: Node.js and Chrome use the same engine. Name two things Node can do that a web page can't.
A: Web page cannot read or write files in the disk and web page cannot listen on a port and act as a server.

Q5: Which of these do you commit: package.json , package-lock.json , node_modules/ ?
A: We leave node modules out and commit the other two.


# Task 1.3 #
The number after running ls -la /c/Windows/System32 | wc -l is 4477, and it means total number of lines in System32, 
The command used for this after reaching System 32 folder using cd is "ls -la | sort -k5 -r | head -n 5"
ls -la is used to print list of all files, sort -k5 is used for sorting in ascending order then -r reverses ascending to descending order and finally head -n 5 is used for top 5 files.