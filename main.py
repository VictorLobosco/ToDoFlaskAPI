import datetime
from flask import app, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request
from models import User, ToDo
from app import ToDoSchema, app, UserSchema, EditSchema, EditToDoSchema, LoginSchema, jwt

#this route takes care of the registred users, it does the registration if the request type is POST, allows info to be change to current user if the request type is PUT, and changes the Active boolean in the database to False if the request method is DELETE
@app.route('/user/', methods = ['POST', 'PUT', 'DELETE'])
def register_user():
    if request.method == 'POST':
        #check if there is a acess token in the request if there is one, it dosent allow a user to be created until either the token is expired or revoked using the /logout/ route
        if not verify_jwt_in_request(locations= ['cookies'], optional = True):
            #A variable that holds the data sent through json
            data = request.json
            #marshmallow code that handles the verification of the request, if the request is deemed invalid its returns the mensage sent by marshmallow
            userschema = UserSchema()
            validation_error = userschema.validate(request.json)
            if validation_error:
                return jsonify(validation_error), 400
            # checks if the login or email is already used by someone in the database
            if (User.query.filter_by(email=data['email']).first() is None) and (User.query.filter_by(login=data['login']).first() is None):
                # a simple try except to catch any erros
                try:
                    #set the right values to the right variables
                    user = User(login =data['login'], email=data['email'] ,password= data['password'], active = True)
                    #uses the save method from the model to save the info in the database
                    user.save()
                    response = {
                            'Status': 'User {} created, to login send a post to login with the login and password'.format(user.login)
                        }, 201
                except AttributeError:
                    response = {
                        'Status':'Failed to create User'
                    }, 500 
            else:
                response = {"status":"either the username or email is already being used by an existing account"}, 400
                return response
        else:
            response = {"Status": "You already have an account"}

    if request.method == 'PUT':
        #check if the user is logged in, if it is it uses that id as the identifier if it dosent it will tell the user to log-in
        if verify_jwt_in_request(locations= ['cookies'], optional = True):
            #A variable that holds the data sent through json
            data = request.json
            #marshmallow code that handles the verification of the request, if the request is deemed invalid its returns the mensage sent by marshmallow
            editschema = EditSchema()
            validation_error = editschema.validate(request.json)
            if validation_error:
                return jsonify(validation_error), 400
            #Checks if the request is empty
            if data:
                user = User.query.filter_by(id=get_jwt_identity()).first()
                #check if there is an login field in the request
                if 'login' in data:
                        #check if the username is the same as the one that is already being used and if its not being used by anyone else if either of thoses condition is true it sets the username to be saved, if it is already being used by someone else it returns a message explaning it to the user
                        if (user.login == data['login']) or (User.query.filter_by(login = data['login']).first() is None):
                            print(User.query.filter_by(login = data['login']).first())
                            user.login = data['login']
                        else:
                            response = {"status":"username already being used by someone else"}, 400
                            return response
                #check if there is an email field in the request
                if 'email' in data:
                    #check if the email is the same as the one that is already being used and if its not being used by anyone else if either condition is true it sets the email to be saved, if it is already being used by someone else it returns a message explaning it to the user
                    if (user.email == data['email']) or (User.query.filter_by(email = data['email']).first() is None):
                        user.email = data['email']
                    else:
                        response = {"status":"email already being used by someone else"}, 400
                        return response
                #check if there is a passowrd field in the request
                if 'password' in data:
                        #calls the set_password method from the model, it hashes the password and then i set the hashed password as the new password
                        newpass = user.set_password(data['password'])
                        user.password = newpass
                user.save()
                response = {
                        "Status":"Changes applied sucessufuly"
                    }, 200
            else:
                response = {"Status":"Empty Request"}, 400
        else:
            response = {"Status":"you need to be loged in to performe this operation, if you dont have an account yet, you can create on by sending a POST to the same adress"}, 401
        return response

    if request.method == 'DELETE':
        #checks if the user is logged in and if it is it then querys the user with the same id as the logged one and then its change its active status to false
        if verify_jwt_in_request(locations= ['cookies'], optional = True):
            user = User.query.filter_by(id=get_jwt_identity()).first()
            user.deactive_user()
            user.save()
            response = {"Status":"User deleted"}, 200
            unset_jwt_cookies(response)
        else:
            response = {"Status":"you need to be loged in to performe this operation, if you dont have an account yet, you can create on by sending a POST to the same adress"}, 401
    return response

#this route takes care of both creating a todo and showing all todos that belong to the user
@app.route('/todo/', methods = ['POST', 'GET'])
@jwt_required()
def add_todo():
    if request.method == "POST":
        data = request.json
        #marshmallow code that handles the verification of the request, if the request is deemed invalid its returns the mensage sent by marshmallow
        todoschema = ToDoSchema()
        validation_error = todoschema.validate(request.json)
        if validation_error:
            return jsonify(validation_error), 400
        #gets the id of the currently logged user this will be use as to get the info of that user. 
        current_id = int(get_jwt_identity())
        try:
            #checks if the id that owns the todo is the same as the currently logged in one
            user = User.query.filter_by(id=current_id).first()
            #Checks if the request is empty, and if it has any fields missing in the request it sets a default value to them
            if data:
                if 'details' not in data:
                    data['details'] = "none"
                if 'status' not in data:
                    data['status'] = "pending"
            #sets all the info into an variable and then uses the save() method of the todo class to save it to the database
            todo = ToDo(name = data['name'], details = data['details'], status = data['status'], user = user)
            todo.save()
            response = {
                            'name':todo.name,
                            'details':todo.details,
                            'status':todo.status,
                            'id':todo.id
                }, 201
        except AttributeError:
            response = {'status': 'There is something wrong with the sended request, please check if all the fields are correct before trying again'}, 400
        return response

    if request.method == "GET":
        #gets the id of the currently logged user
        current_id = int(get_jwt_identity())
        #query all the todos belonging to the currently logged in user
        todo = ToDo.query.filter_by(user_id=current_id)
        #a simple for loop stores all the todos in the response variable
        response = [{'name':i.name, 'details':i.details, 'status':i.status, 'id':i.id} for i in todo]
        #check to see if there is any todo assing to the user, if there is none it will send a message explaining that to the user, if there is any it is sent to the user
        if not (todo.first() is None):
            response = jsonify(response), 200
        else:
            response = {"Status":"The current user dosent have any todos"}, 204
        return response

#this method takes care of editing, deleting and showing a specific todo to the user by using and id as a identifier
@app.route('/todo/<int:id>/', methods = ['PUT', 'DELETE', 'GET'])
@jwt_required()
def modify_todo(id):
    if request.method == "PUT":
        data = request.json
        #marshmallow code that handles the verification of the request, if the request is deemed invalid its returns the mensage sent by marshmallow
        todoschema = EditToDoSchema()
        validation_error = todoschema.validate(request.json)
        if validation_error:
            return jsonify(validation_error), 400
        #Checks if the request is empty, if not it adds any fields present in the request to the database
        if data:
            try:
                todo = ToDo.query.filter_by(id=id).first()
                #checks if the selected todo belongs to the currently logged user if it does it will apply the changes if it dosent then its display a message explaning the current situation
                if todo.user_id == int(get_jwt_identity()):
                    if 'name' in data:
                        todo.name = data['name']
                    if 'details' in data:
                        todo.details = data['details']
                    if 'status' in data:
                        todo.status = data['status']
                    todo.save()
                    response = {
                            'name':todo.name,
                            'details':todo.details,
                            'status':todo.status
                        }, 200
                else:
                    response = {'Error': 'The todo with the given id dosent belong to the currently logged user'}, 403
            except AttributeError:
                response = {'status': 'There is something wrong with the sended request, please check if all the fields are correct before trying again'}, 400
        return response

    if request.method == "DELETE":
        try:
            #checks if the selected todo belongs to the currently logged user if it does it will delete the entry, if it dosent then its display a message explaning the current situation
            todo = ToDo.query.filter_by(id=id).first()
            if todo.user_id == int(get_jwt_identity()):
                todo.delete()
                response = {'status':'Taks deleted.'}, 200
            else:
                response = {'Error': 'The todo with the given id dosent belong to the currently logged user'}, 403
        except AttributeError:
            response = {'Error': 'Either a todo with the given id dosent exist or the database could not be reached'}, 400
        return response
    
    if request.method == "GET":
        #Checks if the required entry is owned by the id that is currentrly logged in, if it is the info in the entry is returned if not then returns a messagens explaining that
        try:
            todo = ToDo.query.filter_by(id=id).first()
            if todo.user_id == int(get_jwt_identity()):
                response = {
                    'name':todo.name,
                    'details':todo.details,
                    'status':todo.status,
                }
            else:
                response = {
                    "error":"The todo you are trying to return dosent belong to the logged user"
                }, 403
        except AttributeError:
            response = {
                "mensage": "entry not found"
            }, 404
        
        return response


@app.route('/login/', methods=['POST'])
def login():
    if not verify_jwt_in_request(locations= ['cookies'], optional = True):

        if request.method == 'POST':
            data = request.json
            loginschema = LoginSchema()
            validation_error = loginschema.validate(request.json)
            if validation_error:
                return jsonify(validation_error)
            user = User.query.filter_by(login=data['login']).first()
            if not user or not user.check_password(data['password']):
                response = {"Status":"Either the user name or the password is incorrect"}, 400
            else:
                access_token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(hours=1))
                response = jsonify({'Status':'sucess'})
                set_access_cookies(response ,access_token)
        return response
    else:
        return jsonify({"Status":"You are already logged in"}), 405

@app.route('/logout/', methods=['POST'])
def logout():
    response = jsonify({'logout': True})
    unset_jwt_cookies(response)
    return response

@jwt.unauthorized_loader
def verification_fail_loader(callback):
    return ({"status": "you need to be loged in to performe this operation, if you dont have an account yet, you can create on by sending a POST to /user/"}), 401

if __name__ == '__main__':
    app.run()