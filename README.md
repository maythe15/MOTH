# MOTH
Basic token based authentication server

# Module components

### CLI
The MOTH CLI is very limited and only contains two commands.

The first command is `moth create`. This takes a file path and creates an empty MOTH database file.<br>
The second command is `moth run`. This takes the path to a MOTH database and a server port, and starts the server.

### Server
This can be accessed through `moth.server`. It has two main methods: `run` and `run_threaded`.<br>
Both take a database path and a server port, with the difference being that `run_threaded` starts the server without blocking.

### Moth
This is an alternate method of accessing MOTH without the use of the server accessible through the `moth.moth.Moth` class.<br>
The functions in this class mirror the API endpoints of `moth.server`.

### Utils
This is a collection of MOTH utilities, exceptions, and other internal classes accessible through `moth.utils`.<br>
There are 3 primary functions included:<br>
  `db_exists` takes a path to a database file and returns whether it exists or not.<br>
  `make_db` takes a path and creates a new database file at it if a database is not already present there. It will return if a new databse was created or not.<br>
  `reset_db` takes a path to an existing database file and resets if it is present. It will not create a new database. It will return if it reset the database.

# API
Note that while these docs cover the server API, the `moth.moth.Moth` class functions take the same names and parameters. For example, sending `{"token"="TOKEN"}` to `/logout` is equivalent to running `logout(token="TOKEN")`.<br>
The largest difference is that non-200 return codes are replaced with exceptions. The only return code that does not have an exception analogue is `400 Missing request parameters`. All server end points are capable of responsind with it.

### Terms
+ `username`: The name of the user account<br>
+ `password`: The password of the user account<br>
+ `token`: An access token associated with an account<br>
+ `userid`: An internal unique incremental ID associated with each account<br>
+ `permissions`: A miscellaneous convenience string. This is not used within MOTH itself.<br>
+ `expires`: A unix timestamp at which the associated token expires.

### /login [GET]
Takes: `username, password`<br>
Returns: `token, userid, username, permissions, expires`<br>
Error codes:<br>
+ `401 Unknown username` or `moth.utils.NoUserError`: Username does not exist<br>
+ `401 Invalid password` or `moth.utils.InvalidPasswordError`: Username is valid but the provided password does not match.<br>

###
  
# Warning about server usage
This server is intended to be entirely backend, and does not do any credential validation before performing actions. It should *never* be accessible to untrusted programs, and programs intending to use MOTH should perform their own checks before passing the operation over to MOTH.
