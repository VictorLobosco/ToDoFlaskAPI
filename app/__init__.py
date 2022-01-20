from flask import Flask
from marshmallow import Schema, fields
from marshmallow.validate import Length
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_CSRF_IN_COOKIES"] = True
#this is set to false as to not requeire the token to be sent in the header.
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
jwt = JWTManager(app)



#Schemas used by marshmallow to validate the requests

class UserSchema(Schema):
    login = fields.Str(required=True, validate=Length(max=20))
    password = fields.Str(required=True, validate=Length(max=128))
    email = fields.Str(required=True, validate=Length(max=128))


class EditSchema(Schema):
    login = fields.Str(validate=Length(max=20))
    password = fields.Str(validate=Length(max=128))
    email = fields.Str(validate=Length(max=128))


class ToDoSchema(Schema):
    name = fields.Str(required=True, validate=Length(max=80))
    details = fields.Str(validate=Length(max=250))
    status = fields.Str(validate=Length(max=250))

class EditToDoSchema(Schema):
    name = fields.Str(validate=Length(max=80))
    details = fields.Str(validate=Length(max=250))
    status = fields.Str(validate=Length(max=250))

class LoginSchema(Schema):
    login = fields.Str(required=True, validate=Length(max=20))
    password = fields.Str(required=True, validate=Length(max=128))