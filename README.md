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
There are 3 primary functions included:
+ `db_exists` takes a path to a database file and returns whether it exists or not.
+ `make_db` takes a path and creates a new database file at it if a database is not already present there. It will return if a new databse was created or not.
+ `reset_db` takes a path to an existing database file and resets if it is present. It will not create a new database. It will return if it reset the database.

# API
Note that while these docs cover the server API, the `moth.moth.Moth` class functions take the same names and parameters. For example, sending `{"token"="TOKEN"}` to `/logout` is equivalent to running `logout(token="TOKEN")`.<br>
The largest difference is that non-200 return codes are replaced with exceptions. The only return code that does not have an exception analogue is `400 Missing request parameters`. All server end points are capable of responding with it.<br>
Many methods return either `401 Token expired` or `moth.utils.TokenExpiredError`. This indicates that a token *did* exist, but has expired. This also means that the token has been cleaned up, and subsequent identical calls will return `401 Token does not exist` or `moth.utils.InvalidTokenError`.

### Terms
+ `username`: The name of the user account
+ `password`: The password of the user account
+ `token`: An access token associated with an account
+ `userid` or `id`: An internal unique incremental ID associated with each account
+ `permissions`: A miscellaneous convenience string. This is not used within MOTH itself.
+ `expires`: A unix timestamp at which the associated token expires.
+ `valid`: A boolean stating if the requested resource is valid or not.
+ `deleted`: A boolean stating if the requested resource has been successfuly deleted.
+ `updated`: A boolean stating if the requested resource has been successfuly updated.
+ `count`: An integer representing the amount of matching resources present.

### /login [GET]
Create and return a user token.<br>
Equivalent method: `login`<br>
Takes: `username, password`<br>
Returns: `token, userid, username, permissions, expires`<br>
Error codes:<br>
+ `401 User does not exist` or `moth.utils.NoUserError`: User does not exist.
+ `401 Invalid password` or `moth.utils.InvalidPasswordError`: User is valid but the provided password does not match.

### /validate [GET]
Validate that a token exists.<br>
Equivalent method: `validate`<br>
Takes: `token`<br>
Returns `valid, userid, username, permissions, expires`<br>
Error codes:
+ `401 Token does not exist` or `moth.utils.InvalidTokenError`: Token does not exist.
+ `401 Token expired` or `moth.utils.TokenExpiredError`: Token has expired.

### /passvalid [GET]
Check if a password is valid without logging in.<br>
Equivalent method: `passwordValid`<br>
Takes: `username, password`<br>
Returns: `valid`<br>
Error codes:<br>
+ `401 Unknown username` or `moth.utils.NoUserError`: User does not exist.

### /logout [DELETE]
Delete an access token.<br>
Equivalent method: `logout`<br>
Takes: `token`<br>
Returns `deleted`<br>
Error codes:
+ `401 Token does not exist` or `moth.utils.InvalidTokenError`: Token does not exist.

### /new [PUT]
Create a new user.<br>
Equivalent method: `newuser`<br>
Takes: `username, password, permissions`<br>
Returns: `userid, username, permissions`<br>
Error codes:<br>
+ `409 User already exists` or `moth.utils.UserExistsError`: User already exists.

### /del [DELETE]
Delete an existing user.<br>
Equivalent method: `deluser`<br>
Takes: `id`<br>
Returns: `deleted`<br>
Error codes:<br>
+ `401 User does not exist` or `moth.utils.NoUserError`: User does not exist.

### /setpass [PATCH]
Give a user a new password.<br>
Equivalent method: `newpass`<br>
Takes: `id, password`<br>
Returns: `updated`<br>
Error codes:<br>
+ `401 User does not exist` or `moth.utils.NoUserError`: User does not exist.

### /setperms [PATCH]
Update a users permission string.<br>
Equivalent method: `newperms`<br>
Takes: `id, permissions`<br>
Returns: `updated`<br>
Error codes:<br>
+ `401 User does not exist` or `moth.utils.NoUserError`: User does not exist.

### /gettokens [GET]
Check how many tokens a user has.<br>
Equivalent method: `gettokens`<br>
Takes: `id`<br>
Returns: `count`<br>
Error codes:

### /getusers [GET]
Retrieve a list of users.<br>
Equivalent method: `getusers`<br>
Takes: <br>
Returns: `[id, username, permissions]`<br>
Error codes:

### /getuser [GET]
Retrieve information about a specific user.<br>
Equivalent method: `getuser`<br>
Takes: `id`<br>
Returns: `id, username, permissions`<br>
Error codes:
+ `401 User does not exist` or `moth.utils.NoUserError`: User does not exist.

### /deltokens [DELETE]
Clear all tokens associated with a user.<br>
Equivalent method: `deltokens`<br>
Takes: `id`<br>
Returns: `deleted, count`<br>
Error codes:

# Important note about intended server usage
This server is intended to be entirely backend, and does not do any credential validation before performing actions. It should *never* be accessible to untrusted programs, and programs intending to use MOTH should perform their own checks before passing the operation over to MOTH.
