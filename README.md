# MOTH
Basic token based authentication server

## Components

### CLI
The MOTH CLI is very limited and only contains two commands.

The first command is `moth create`. This takes a file path and creates an empty MOTH database file.<br>
The second command is `moth run`. This takes the path to a MOTH database and a server port, and starts the server.

### Moth
Accessed through `moth.moth`, this class connects directly to the database without the use of an intermediary server.

### Server
Accessed through `moth.server`, this class can runs a server mirroring the methods, inputs, and responses of `moth.moth`.<br>
Parameters can be sent to `moth.server` via JSON. For example, the call `logout(token="TOKEN")` is equivalent to an API call to `/logout` with the JSON data `{token="TOKEN"}`.<br>
Return codes, and what exceptions they represent, are noted in the call documentation.<br>
Can be started without blocking through `moth.server.start_threaded`.

### Client
Accessed through `moth.client`, this class connects to an instance of `moth.server` but behaves like `moth.moth`, including exceptions.<br>
This may also return `moth.utils.ServerError` when the server responds in an unexpected way.

### Utils
This is a collection of MOTH utilities, exceptions, and other internal classes accessible through `moth.utils`.<br>
There are 3 primary functions included:
+ `db_exists` takes a path to a database file and returns whether it exists or not.
+ `make_db` takes a path and creates a new database file at it if a database is not already present there. It will return if a new databse was created or not.
+ `reset_db` takes a path to an existing database file and resets if it is present. It will not create a new database. It will return if it reset the database.

### Terms
+ `username`: The name of the user account
+ `password`: The password of the user account
+ `token`: An access token associated with an account
+ `userid` or `id`: An internal unique incremental ID associated with each account
+ `expires`: A unix timestamp at which the associated token expires.
+ `valid`: A boolean stating if the requested resource is valid or not.
+ `deleted`: A boolean stating if the requested resource has been successfuly deleted.
+ `updated`: A boolean stating if the requested resource has been successfuly updated.
+ `count`: An integer representing the amount of matching resources present.

### login
Create and return a user token.<br>
Equivalent server call: `/login [GET]`<br>
Takes: `username, password`<br>
Returns: `token, userid, username, expires`<br>
Error codes:<br>
+ `401 User does not exist` or `moth.utils.NoUserError`: User does not exist.
+ `401 Invalid password` or `moth.utils.InvalidPasswordError`: User is valid but the provided password does not match.

### validate
Validate that a token exists.<br>
Equivalent server call: `/validate [GET]`<br>
Takes: `token`<br>
Returns `valid, userid, username, expires`<br>
Error codes:
+ `401 Token does not exist` or `moth.utils.InvalidTokenError`: Token does not exist.
+ `401 Token expired` or `moth.utils.TokenExpiredError`: Token has expired.

### passwordValid
Check if a password is valid without logging in.<br>
Equivalent server call: `/passvalid [GET]`<br>
Takes: `username, password`<br>
Returns: `valid`<br>
Error codes:<br>
+ `401 Unknown username` or `moth.utils.NoUserError`: User does not exist.

### logout
Delete an access token.<br>
Equivalent server call: `/logout [DELETE]`<br>
Takes: `token`<br>
Returns `deleted`<br>
Error codes:
+ `401 Token does not exist` or `moth.utils.InvalidTokenError`: Token does not exist.

### newuser
Create a new user.<br>
Equivalent server call: `/new [PUT]`<br>
Takes: `username, password`<br>
Returns: `userid, username`<br>
Error codes:<br>
+ `409 User already exists` or `moth.utils.UserExistsError`: User already exists.

### deluser
Delete an existing user.<br>
Equivalent server call: `/del [DELETE]`<br>
Takes: `id`<br>
Returns: `deleted`<br>
Error codes:<br>
+ `401 User does not exist` or `moth.utils.NoUserError`: User does not exist.

### newpass
Give a user a new password.<br>
Equivalent server call: `/setpass [PATCH]`<br>
Takes: `id, password`<br>
Returns: `updated`<br>
Error codes:<br>
+ `401 User does not exist` or `moth.utils.NoUserError`: User does not exist.

### gettokens
Check how many tokens a user has.<br>
Equivalent server call: `/gettokens [GET]`<br>
Takes: `id`<br>
Returns: `count`<br>
Error codes:

### getusers
Retrieve a list of users.<br>
Equivalent server call: `/getusers [GET]`<br>
Takes: <br>
Returns: `[id, username]`<br>
Error codes:

### getuser
Retrieve information about a specific user.<br>
Equivalent server call: `/getuser [GET]`<br>
Takes: `id`<br>
Returns: `id, username`<br>
Error codes:
+ `401 User does not exist` or `moth.utils.NoUserError`: User does not exist.

### deltokens
Clear all tokens associated with a user.<br>
Equivalent server call: `/deltokens [DELETE]`<br>
Takes: `id`<br>
Returns: `deleted, count`<br>
Error codes:

# Important note about intended server usage
This server is intended to be entirely backend, and does not do any credential validation before performing actions. It should *never* be accessible to untrusted programs, and programs intending to use MOTH should perform their own checks before passing the operation over to MOTH.
