# MediaFetch
Hello there! Welcome to my API of Google News! 

To get this up and running, install all dependancies with pip, and run it with a python version of 3 or later (preferably the most recent)

You need a few environment variables. 
  1. `EMAIL_ADDRESS`, an email address that works with flask_mail
  2. `MFS`, a long, secure, secret for MediaFetch to use. Never change this.
  3. `MAIL_APP_PWORD`, the password to your email address, if it is a gmail, you need to generate an app password and use it here.
Any environment variables can be renamed.
To set up the database, here are the steps
  1. `touch database.db`
  2. `python3`
  3. `from app import db`
  4. `db.create_all()`

Make sure to change stuff like the shebang line to something that works for you, or, even better, remove it. Do the same and change the `sqlite://///` path to whatever the path of the database.db file is for you. 
If there are any errors, I know this should work so it is an issue with your system and/or you didn't change everything you needed to. 
If you find something you need to change that I didnt mention, make a PR to this readme.md.
Make sure your localhost:5050 is open, and if it isn't, change the port. 
