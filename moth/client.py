# a couple imports
import requests
import time

import json

import moth.utils as utils

#app class
class MothClient:
    def __init__(self, url):
        self.url=url

    def login(self, username, password):
        req = requests.get(f'{self.url}/login', json=json.dumps({
            'username':username,
            'password':password
        }))

        if req.status_code==401:
            if req.text=='Invalid password':
                raise utils.InvalidPasswordError(f"Password for user {username} does not match")
            elif req.text=='User does not exists':
                raise utils.NoUserError(f"User {username} does not exist")
            else:
                raise utils.ServerError(f"Unknown response for 401: {req.text}")
        elif req.status_code==400:
            raise utils.ServerError(f"Server responded with 400: {req.text}")
        elif req.status_code==200:
            return req.json()
        else:
            raise utils.ServerError(f"Server responded with unknown code {req.status_code}")

    def validate(self, token):
        req = requests.get(f'{self.url}/validate', json={'token':token})
        if req.status_code==401:
            if req.text=='Token does not exist':
                raise utils.InvalidTokenError(f"Token does not exist")
            elif req.text=='Token expired':
                raise utils.TokenExpiredError(f"Token expired")
            else:
                raise utils.ServerError(f"Unknown response for 401: {req.text}")
        elif req.status_code==400:
            raise utils.ServerError(f"Server responded with 400: {req.text}")
        elif req.status_code==200:
            return req.json()
        else:
            raise utils.ServerError(f"Server responded with unknown code {req.status_code}")

    def logout(self, token):
        req = requests.delete(f'{self.url}/logout', json={'token': token})
        if req.status_code == 401:
            if req.text == 'Token does not exist':
                raise utils.InvalidTokenError(f"Token does not exist")
            else:
                raise utils.ServerError(f"Unknown response for 401: {req.text}")
        elif req.status_code == 400:
            raise utils.ServerError(f"Server responded with 400: {req.text}")
        elif req.status_code == 200:
            return req.json()
        else:
            raise utils.ServerError(f"Server responded with unknown code {req.status_code}")

    def passwordValid(self, username, password):
        req = requests.get(f'{self.url}/passvalid', json={'username':username, 'password':password})
        if req.status_code == 401:
            if req.text == 'Token does not exist':
                raise utils.NoUserError(f"User does not exist")
            else:
                raise utils.ServerError(f"Unknown response for 401: {req.text}")
        elif req.status_code == 400:
            raise utils.ServerError(f"Server responded with 400: {req.text}")
        elif req.status_code == 200:
            return req.json()
        else:
            raise utils.ServerError(f"Server responded with unknown code {req.status_code}")

    def newuser(self, username, passw):
        req = requests.put(f'{self.url}/new', json=json.dumps({
            'username': username,
            'password': passw
        }))

        if req.status_code == 409:
            if req.text == 'User already exists':
                raise utils.UserExistsError(f'User {username} already exists')
            else:
                raise utils.ServerError(f"Unknown response for 409: {req.text}")
        elif req.status_code == 400:
            raise utils.ServerError(f"Server responded with 400: {req.text}")
        elif req.status_code == 200:
            return req.json()
        else:
            raise utils.ServerError(f"Server responded with unknown code {req.status_code}")

    def deluser(self, id):
        req = requests.delete(f'{self.url}/del', json=json.dumps({
            'id': id
        }))

        if req.status_code == 401:
            if req.text == 'User does not exist':
                raise utils.NoUserError(f"User does not exist")
            else:
                raise utils.ServerError(f"Unknown response for 401: {req.text}")
        elif req.status_code == 400:
            raise utils.ServerError(f"Server responded with 400: {req.text}")
        elif req.status_code == 200:
            return req.json()
        else:
            raise utils.ServerError(f"Server responded with unknown code {req.status_code}")

    def newpass(self, id, password):
        req = requests.patch(f'{self.url}/setpass', json=json.dumps({
            'id': id,
            'password':password
        }))

        if req.status_code == 401:
            if req.text == 'User does not exist':
                raise utils.NoUserError(f"User does not exist")
            else:
                raise utils.ServerError(f"Unknown response for 401: {req.text}")
        elif req.status_code == 400:
            raise utils.ServerError(f"Server responded with 400: {req.text}")
        elif req.status_code == 200:
            return req.json()
        else:
            raise utils.ServerError(f"Server responded with unknown code {req.status_code}")

    def gettokens(self, id):
        req = requests.get(f'{self.url}/gettokens', json=json.dumps({
            'id': id
        }))

        if req.status_code == 400:
            raise utils.ServerError(f"Server responded with 400: {req.text}")
        elif req.status_code == 200:
            return req.json()
        else:
            raise utils.ServerError(f"Server responded with unknown code {req.status_code}")


    def getusers(self):
        req = requests.get(f'{self.url}/getusers')
        if req.status_code == 200:
            return req.json()
        else:
            raise utils.ServerError(f"Server responded with unknown code {req.status_code}")

    def getuser(self, id):
        req = requests.get(f'{self.url}/getuser', json=json.dumps({
            'id':id
        }))

        if req.status_code == 401:
            if req.text == 'User does not exists':
                raise utils.NoUserError(f"User does not exist")
            else:
                raise utils.ServerError(f"Unknown response for 401: {req.text}")
        elif req.status_code == 400:
            raise utils.ServerError(f"Server responded with 400: {req.text}")
        elif req.status_code == 200:
            return req.json()
        else:
            raise utils.ServerError(f"Server responded with unknown code {req.status_code}")

    def deltokens(self, id):
        req = requests.delete(f'{self.url}/deltokens', json=json.dumps({
            'id': id
        }))

        if req.status_code == 400:
            raise utils.ServerError(f"Server responded with 400: {req.text}")
        elif req.status_code == 200:
            return req.json()
        else:
            raise utils.ServerError(f"Server responded with unknown code {req.status_code}")