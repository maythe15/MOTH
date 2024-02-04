# a couple imports
import json
import multiprocessing
import time
from flask import Flask
from flask import request
import sqlalchemy
import sqlalchemy.orm as orm
import bcrypt
from flask import Response
import sqlalchemy.exc
import moth.utils as utils

#app class
class App:
    def __init__(self, path):
        self.path=path
        self.engine=sqlalchemy.create_engine(f"sqlite:///{self.path}")
    
    def run(self, port):
        app=Flask(__name__)
    
        @app.route("/login", methods=['GET'])
        def login():
            if request.method=='GET':
                try:
                    username=request.json['username']
                    passw=request.json['password']
                except:
                    return Response('Missing request parameters',400)
                with orm.Session(self.engine) as session:
                    state=sqlalchemy.select(utils.User).where(utils.User.username==username)
                    result=session.scalars(state).one()
                    if not result:
                        return Response("User does not exist", 401)
                    password_good=bcrypt.checkpw(bytes(passw,'utf8'),bytes(result.password,'utf8'))
                    if not password_good:
                        return Response("Invalid password", 401)
                    #make a token
                    token_str=bcrypt.gensalt()
                    token = utils.Token(id=result.id, token=token_str.decode('utf8'), expires=round(time.time())+259200)
                    session.add(token)
                    session.commit()
                    return Response(json.dumps({'token':token_str.decode('utf8'), 'userid':result.id, 'username':result.username, 'permissions':result.permissions, 'expires':token.expires}), 200)
    
        @app.route("/validate", methods=['GET'])
        def validate():
            if request.method=='GET':
                try:
                    token=request.json['token']
                except Exception:
                    return Response('Missing request parameters',400)
                with orm.Session(self.engine) as session:
                    state=sqlalchemy.select(utils.Token).where(utils.Token.token==token)
                    result=session.scalars(state).all()
                    if not result:
                        return Response("Token does not exist", 401)
                    result = result[0]
                    if result.expires<time.time():
                        #token expired, delete it
                        session.delete(result)
                        session.commit()
                        return Response("Token expired", 401)
                    #fetch the user and give some info
                    state = sqlalchemy.select(utils.User).where(utils.User.id == result.id)
                    user=session.scalars(state).one()
                    returncode=json.dumps({'valid':True, 'userid':user.id, 'username':user.username, 'permissions':user.permissions, 'expires':result.expires})
                    return Response(returncode, 200, content_type='JSON')

        @app.route('/passvalid', methods=['GET'])
        def passwordValid(self, username, password):
            if request.method=='GET':
                try:
                    username = request.json['username']
                    password = request.json['password']
                except Exception:
                    return Response('Missing request parameters',400)
                with orm.Session(self.engine) as session:
                    state = sqlalchemy.select(utils.User).where(utils.User.username == username)
                    result = session.scalars(state).all()
                    if not result:
                        return Response("User does not exist", 401)
                    result = result[0]
                    return Response(
                        json.dumps({'valid': bcrypt.checkpw(bytes(password, 'utf8'), bytes(result.password, 'utf8'))}),
                        200, content_type='JSON')

        @app.route('/logout', methods=['DELETE'])
        def logout():
            if request.method=='DELETE':
                try:
                    token=request.json['token']
                except Exception:
                    return Response('Missing request parameters',400)
                with orm.Session(self.engine) as session:
                    state=sqlalchemy.select(utils.Token).where(utils.Token.token==token)
                    result=session.scalars(state).all()
                    if not result:
                        return Response("Token does not exist", 401)
                    result=result[0]
                    session.delete(result)
                    session.commit()
                    return Response(json.dumps({'deleted':True}), 200, content_type='JSON')
    
        @app.route('/new', methods=['PUT'])
        def newuser():
            if request.method=='PUT':
                try:
                    username = request.json['username']
                    passw = request.json['password']
                    permissions=request.json['permissions']
                except Exception:
                    return Response('Missing request parameters',400)
                with orm.Session(self.engine) as session:
                    password = bcrypt.hashpw(bytes(passw, 'utf8'), bcrypt.gensalt())
                    user = utils.User(username=username, permissions=permissions, password=password.decode('utf8'))
                    session.add(user)
                    try:
                        session.commit()
                    except sqlalchemy.exc.IntegrityError:
                        return Response("User already exists", 409)
                    return Response(json.dumps({'userid':user.id, 'username':user.username, 'permissions':user.permissions}), 200, content_type='JSON')
    
        @app.route('/del', methods=['DELETE'])
        def deluser():
            if request.method=='DELETE':
                try:
                    id = request.json['id']
                except Exception:
                    return Response('Missing request parameters',400)
                with orm.Session(self.engine) as session:
                    state = sqlalchemy.select(utils.User).where(utils.User.id == id)
                    result = session.scalars(state).all()
                    if not result:
                        return Response("User does not exist", 401)
                    result = result[0]
                    session.delete(result)
                    state = sqlalchemy.select(utils.Token).where(utils.Token.id == id)
                    result = session.scalars(state).all()
                    for i in result:
                        session.delete(i)
                    session.commit()
                    return Response(json.dumps({'deleted': True}), 200, content_type='JSON')
    
        @app.route('/setpass', methods=['PATCH'])
        def newpass():
            if request.method=='PATCH':
                try:
                    id = request.json['id']
                    password = request.json['password']
                except Exception:
                    return Response('Missing request parameters',400)
                with orm.Session(self.engine) as session:
                    state = sqlalchemy.select(utils.User).where(utils.User.id == id)
                    result = session.scalars(state).all()
                    if not result:
                        return Response("User does not exist", 401)
                    user=result[0]
                    password = bcrypt.hashpw(bytes(password, 'utf8'), bcrypt.gensalt())
                    user.password=password.decode('utf8')
                    session.commit()
                    return Response(json.dumps({'updated': True}), 200, content_type='JSON')
    
        @app.route('/setperms', methods=['PATCH'])
        def newperms():
            if request.method=='PATCH':
                try:
                    id = request.json['id']
                    permissions = request.json['permissions']
                except Exception:
                    return Response('Missing request parameters',400)
                with orm.Session(self.engine) as session:
                    state = sqlalchemy.select(utils.User).where(utils.User.id == id)
                    result = session.scalars(state).all()
                    if not result:
                        return Response("User does not exist", 401)
                    user=result[0]
                    user.password=permissions
                    session.commit()
                    return Response(json.dumps({'updated': True}), 200, content_type='JSON')
    
        @app.route('/gettokens', methods=['GET'])
        def gettokens():
            if request.method=='GET':
                try:
                    id = request.json['id']
                except Exception:
                    return Response('Missing request parameters',400)
                with orm.Session(self.engine) as session:
                    state = sqlalchemy.select(utils.Token).where(utils.Token.id == id)
                    result = len(session.scalars(state).all())
                    return Response(json.dumps({'count': result}), 200, content_type='JSON')
    
        @app.route('/getusers', methods=['GET'])
        def getusers():
            if request.method=='GET':
                with orm.Session(self.engine) as session:
                    state = sqlalchemy.select(utils.User)
                    result=[]
                    for i in session.scalars(state).all():
                        result.append({'id':i.id, 'username':i.username, 'permissions':i.permissions})
                    return Response(json.dumps(result), 200, content_type='JSON')
    
        @app.route('/getuser', methods=['GET'])
        def getuser():
            if request.method=='GET':
                try:
                    id = request.json['id']
                except Exception:
                    return Response('Missing request parameters',400)
                with orm.Session(self.engine) as session:
                    state = sqlalchemy.select(utils.User).where(utils.User.id == id)
                    i = session.scalars(state).all()
                    if i:
                        i=i[0]
                    else:
                        return Response("User does not exist", 401)
                    return Response(json.dumps({'id':i.id, 'username':i.username, 'permissions':i.permissions}), 200, content_type='JSON')
    
        @app.route('/deltokens', methods=['DELETE'])
        def deltokens():
            if request.method=='DELETE':
                try:
                    id = request.json['id']
                except Exception:
                    return Response('Missing request parameters',400)
                with orm.Session(self.engine) as session:
                    state = sqlalchemy.select(utils.Token).where(utils.Token.id == id)
                    result = session.scalars(state).all()
                    count=0
                    for i in result:
                        session.delete(i)
                        count+=1
                    session.commit()
                    return Response(json.dumps({'deleted': (count>0), 'count': count}), 200, content_type='JSON')
        app.run(host='localhost', port=port)

def run(file, port):
    app = App(file)
    app.run(port)

def run_threaded(file, port):
    thread=multiprocessing.Process(target=run,args=(file, port))
    thread.start()
