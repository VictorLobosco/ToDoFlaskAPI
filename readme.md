# ToDoFlaskAPI

An api project that i made to learn Flask and the concepts of Rest

## What you will need to run this code

- Python
- Flask
- Flask-JWT-Extended
- marshmallow
- psycopg2
- SQLAlchemy

## How it works

this project is composed of 3 python files 

- models.py: who has all the Database related code
- main.py: has all the code related to handling requests and taking care of the JWT token
- __init__.py: its stored inside of the app folder, it contains both the schemas used for validation of requests and some configurations of the app

The api itself is divided in 5 main routes:

- /user/

  Parameters: login, password and email [All obligatory for a POST request]

  This route does the registration of an user using POST, it uses PUT to change info to a registered user and uses DELETE to disable access of a user by changing the account to inactive in the database

- /todo/

  Parameters: name [Obligatory for POST], details and status

  This route takes care of both creating a todo by sending a request with POST and displaying all the ToDos owned by the currently logged user by sending a GET request

- /todo/<"id of the todo">/

  Parameters: name, details and status

  This route's GET method displays an specific ToDo by using its id as an identifier, it allows to modify an ToDo by using the passed id by sending an PUT request and lastly it allows to Delete an ToDo by sending an DELETE request, as long as the ToDo with the sent ID belongs to the currently logged-in user

- /login/

  Parameters: login and password

  This route is used to get an token to access the database, the token has an 1 hour lifetime.

- /logout/

  Parameters: none

  This route is used to revoke the access token

  ## How To Run

  To run this app you will need to either change the dbstring variable inside of the models.py file to a existing Postgres Database or create an database with the same name as the one in the file, then run models.py to create the fields in the database and after that just run main.py and it should work just fine

  

  







