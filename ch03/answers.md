Q: Open the Node.js docs and find the page for fs.readFile in the fs/promises section. What does
it return? What happens if the file doesn't exist? That took you less time than watching a video would
have

A: The function returns a promise which later gives data of the file and if the file does not exist we will see and ENOENT("Error no entry") error.

# Checkpoint 3

Q1: In a stack trace, which line usually tells you where your code broke?
A: In a stack trace, the very first line starting with "at" that mentions the name of file.

Q2: You see Error: ENOENT: no such file or directory, open 'todos.json' . Name two possible
causes?
A: The first possible cause is that there is no such file and it does not exist, another possibility is that we are looking at the wrong place/folder.

Q3: What are the six steps of the debugging method?
A: The six steps are:

1.  Reproducing the error
2.  Read the error
3.  Form a guess
4.  Test the guess
5.  Fix 1 thing at a time
    6)Understand why it broke

Q4: Why are official docs better than a two-year-old tutorial?
A: Because docs get updated very frequently, while information in tutorials can be outdated after sometime.

# Task 3.2

Q1: Write down the error type, the file and line, and what the message means.
A: Error Type: Type Error
File: greet.js
Line: 3
Message: Means the program is trying to find name on a object and the object does not exist.

Q2: Explain the cause in your own words, and fix the bug.
A: Because of wrong indexing, users is a array and the code return list.map((u, i) => shout(list[i + 1])); is skipping 0 index. Bug is also fixed by converting i+1 to i.

Q3:
ENOENT Error Message:
SYED AMANAT ALI SHAH@DESKTOP-6LVBG0M MINGW64 /e/Backend_Learning_1/ch03 (main)
$ node enoentError.js
Error Code: ENOENT
Message: ENOENT: no such file or directory, open 'E:\Backend_Learning_1\ch03\salam.js'

       Assignment to constant variable Message:

SYED AMANAT ALI SHAH@DESKTOP-6LVBG0M MINGW64 /e/Backend_Learning_1/ch03 (main)
$ node assignToConstError.js
E:\Backend_Learning_1\ch03\assignToConstError.js:2
i = 23
^

TypeError: Assignment to constant variable.
at Object.<anonymous> (E:\Backend_Learning_1\ch03\assignToConstError.js:2:3)
at Module.\_compile (node:internal/modules/cjs/loader:1830:14)
at Object..js (node:internal/modules/cjs/loader:1961:10)
at Module.load (node:internal/modules/cjs/loader:1553:32)
at Module.\_load (node:internal/modules/cjs/loader:1355:12)
at wrapModuleLoad (node:internal/modules/cjs/loader:255:19)
at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
at node:internal/main/run_main_module:33:47

Node.js v24.15.0

      Reference Error Message:

SYED AMANAT ALI SHAH@DESKTOP-6LVBG0M MINGW64 /e/Backend_Learning_1/ch03 (main)
$ node refError.js
fakeKey
E:\Backend_Learning_1\ch03\refError.js:6
console.log(secretKey)
^

ReferenceError: secretKey is not defined
at Object.<anonymous> (E:\Backend_Learning_1\ch03\refError.js:6:13)
at Module.\_compile (node:internal/modules/cjs/loader:1830:14)
at Object..js (node:internal/modules/cjs/loader:1961:10)
at Module.load (node:internal/modules/cjs/loader:1553:32)
at Module.\_load (node:internal/modules/cjs/loader:1355:12)
at wrapModuleLoad (node:internal/modules/cjs/loader:255:19)
at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
at node:internal/main/run_main_module:33:47

Node.js v24.15.0

      Unexpected JSON message:
      SYED AMANAT ALI SHAH@DESKTOP-6LVBG0M MINGW64 /e/Backend_Learning_1/ch03 (main)

$ node jsonError.js
<anonymous_script>:1

SyntaxError: Unexpected end of JSON input
at JSON.parse (<anonymous>)
at Object.<anonymous> (E:\Backend_Learning_1\ch03\jsonError.js:2:6)
at Module.\_compile (node:internal/modules/cjs/loader:1830:14)
at Object..js (node:internal/modules/cjs/loader:1961:10)
at Module.load (node:internal/modules/cjs/loader:1553:32)
at Module.\_load (node:internal/modules/cjs/loader:1355:12)
at wrapModuleLoad (node:internal/modules/cjs/loader:255:19)
at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)
at node:internal/main/run_main_module:33:47

Node.js v24.15.0







# TASK 3.3 #

Q1: What does path.join("a", "..", "b") return? (Node docs, path module)?
A: This will return b because .. means go one folder up.

Q2: What's the difference between Array.prototype.find and Array.prototype.filter? (MDN)
A: find() returns first element of the array that satisifies provided testing function
   filter() returns a new array with elements of the calling array for which the provided filtering functions returns true

Q3: What does String.prototype.padStart do? Give an example. (MDN)?
A: It adds characters to the start of one string until it reaches the target length, it accepts 2 parameters, the first is the length of total characters in the result string, the second parameter is the string that is being padded, i.e "abc".padStart(5, "s") will be ssabc etc

Q4: Which Node.js flag loads environment variables from a .env file? (Node docs, command-line options).?
A: --env-file=file flag is used for loading env vars.