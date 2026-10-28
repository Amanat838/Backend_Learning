# Checkpoint 2 #

Q1: What does git commit do that git push doesn't?
A: git commit add changes to local repository in local machine and history is stored in hidden .git folder, while git push add a copy of that history on a server i.e a backup and timeline of project.

Q2: You edited 3 files for 2 different reasons. How do you make two clean commits?
A: We make clean commits by adressing 1 reason at a time and making a commit for them individually.

Q3: Why is Added stuff a poor commit message? Rewrite it for a commit that adds input validation to the signup form.?
A: It can be rewritten as "Add input validations to the signup form in form.ts file"

Q4: You committed a database password and pushed it. What must you do?
A: I must revoke the password and create a new one because it's already in history and can be attacked by a automated bot.

Q5: When is git commit --amend safe, and when is it not?
A: --amend rewrites history and is safe when commits are only on my machine but if someone else is already using the commit then it's not safe.



    # TASKS #
# Task 2.1 #

.I'm skipping part A
.First 2 points of part B are done and I don't know the answer to third part but here's it's result:
$ git check-ignore -v .env ch02/debug.log
.gitignore:2:.env       .env
.gitignore:4:*.log      ch02/debug.log

For part C when I do the mention things at the end I see this error message:
error: the branch 'temp-idea' is not fully merged
hint: If you are sure you want to delete it, run 'git branch -D temp-idea'
hint: Disable this message with "git config advice.forceDeleteBranch false"

I think this means that the temp-idea branch has a change and it's committed but you cannot delete the branch until the change is merged with another branchn because currently it's committed and if I try to delete the branch then what will happen to the change I already committed.

I merged temp-idea with main and then deleted this branch using git branch -d temp-idea, it did not show any error this time.