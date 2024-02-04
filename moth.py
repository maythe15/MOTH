# a couple imports
import time
import sqlalchemy
import sqlalchemy.orm as orm
import bcrypt
import sqlalchemy.exc
import moth.utils as utils

#app class
class Moth:
    def __init__(self, path):
        self.path=path
        self.engine=sqlalchemy.create_engine(f"sqlite:///{self.path}")

    def login(self, username, password):
        with orm.Session(self.engine) as session:
            state=sqlalchemy.select(utils.User).where(utils.User.username==username)
            result=session.scalars(state).all()
            if not result:
                raise utils.NoUserError(f"User {username} does not exist")
            result=result[0]
            password_good=bcrypt.checkpw(bytes(password,'utf8'),bytes(result.password,'utf8'))
            if not password_good:
                raise utils.InvalidPasswordError(f"Password for user {username} does not match")
            #make a token
            token_str=bcrypt.gensalt()
            token = utils.Token(id=result.id, token=token_str.decode('utf8'), expires=round(time.time())+259200)
            session.add(token)
            session.commit()
            return {'token':token_str.decode('utf8'), 'userid':result.id, 'username':result.username, 'permissions':result.permissions, 'expires':token.expires}

    def validate(self, token):
        with orm.Session(self.engine) as session:
            state=sqlalchemy.select(utils.Token).where(utils.Token.token==token)
            result=session.scalars(state).all()
            if not result:
                raise utils.InvalidTokenError(f"Token does not exist")
            result = result[0]
            if result.expires<time.time():
                #token expired, delete it
                session.delete(result)
                session.commit()
                raise utils.TokenExpiredError(f"Token expired")
            #fetch the user and give some info
            state = sqlalchemy.select(utils.User).where(utils.User.id == result.id)
            user=session.scalars(state).one()
            return {'valid':True, 'userid':user.id, 'username':user.username, 'permissions':user.permissions, 'expires':result.expires}

    def logout(self, token):
        with orm.Session(self.engine) as session:
            state=sqlalchemy.select(utils.Token).where(utils.Token.token==token)
            result=session.scalars(state).all()
            if not result:
                raise utils.InvalidTokenError(f"Token does not exist")
            result=result[0]
            session.delete(result)
            session.commit()
            return {'deleted':True}

    def passwordValid(self, username, password):
        with orm.Session(self.engine) as session:
            state=sqlalchemy.select(utils.User).where(utils.User.username==username)
            result=session.scalars(state).all()
            if not result:
                raise utils.NoUserError(f"User {username} does not exist")
            result=result[0]
            return {'valid':bcrypt.checkpw(bytes(password,'utf8'),bytes(result.password,'utf8'))}

    def newuser(self, username, passw, permissions):
        with orm.Session(self.engine) as session:
            password = bcrypt.hashpw(bytes(passw, 'utf8'), bcrypt.gensalt())
            user = utils.User(username=username, permissions=permissions, password=password.decode('utf8'))
            session.add(user)
            try:
                session.commit()
            except sqlalchemy.exc.IntegrityError:
                raise utils.UserExistsError(f'User {username} already exists')
            return {'userid':user.id, 'username':user.username, 'permissions':user.permissions}

    def deluser(self, id):
        with orm.Session(self.engine) as session:
            state = sqlalchemy.select(utils.User).where(utils.User.id == id)
            result = session.scalars(state).all()
            if not result:
                raise utils.NoUserError(f"User does not exist")
            result = result[0]
            session.delete(result)
            state = sqlalchemy.select(utils.Token).where(utils.Token.id == id)
            result = session.scalars(state).all()
            for i in result:
                session.delete(i)
            session.commit()
            return {'deleted': True}

    def newpass(self, id, password):
        with orm.Session(self.engine) as session:
            state = sqlalchemy.select(utils.User).where(utils.User.id == id)
            result = session.scalars(state).all()
            if not result:
                raise utils.NoUserError(f"User does not exist")
            user=result[0]
            password = bcrypt.hashpw(bytes(password, 'utf8'), bcrypt.gensalt())
            user.password=password.decode('utf8')
            session.commit()
            return {'updated': True}

    def newperms(self, id, permissions):
        with orm.Session(self.engine) as session:
            state = sqlalchemy.select(utils.User).where(utils.User.id == id)
            result = session.scalars(state).all()
            if not result:
                raise utils.NoUserError(f"User does not exist")
            user=result[0]
            user.password=permissions
            session.commit()
            return {'updated': True}

    def gettokens(self, id):
        with orm.Session(self.engine) as session:
            state = sqlalchemy.select(utils.Token).where(utils.Token.id == id)
            result = len(session.scalars(state).all())
            {'count': result}

    def getusers(self):
            with orm.Session(self.engine) as session:
                state = sqlalchemy.select(utils.User)
                result=[]
                for i in session.scalars(state).all():
                    result.append({'id':i.id, 'username':i.username, 'permissions':i.permissions})
                return result

    def getuser(self, id):
        with orm.Session(self.engine) as session:
            state = sqlalchemy.select(utils.User).where(utils.User.id == id)
            i = session.scalars(state).all()
            if i:
                i=i[0]
            else:
                raise utils.NoUserError(f"User does not exist")
            return {'id':i.id, 'username':i.username, 'permissions':i.permissions}

    def deltokens(self, id):
        with orm.Session(self.engine) as session:
            state = sqlalchemy.select(utils.Token).where(utils.Token.id == id)
            result = session.scalars(state).all()
            count=0
            for i in result:
                session.delete(i)
                count+=1
            session.commit()
            return {'deleted': (count>0), 'count': count}