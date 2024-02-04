import sqlalchemy.orm as orm
import sqlalchemy
import sqlalchemy_utils
import os


def db_exists(file):
    return sqlalchemy_utils.database_exists(f"sqlite:///{file}")


def make_db(file):
    if not db_exists(file):
        engine = sqlalchemy.create_engine(f"sqlite:///{file}")
        sqlalchemy_utils.create_database(engine.url)
        Base.metadata.create_all(engine)
        with orm.Session(engine) as session:
            session.commit()
        return True
    return False


def reset_db(file):
    if db_exists(file):
        os.remove(file)
        engine = sqlalchemy.create_engine(f"sqlite:///{file}")
        sqlalchemy_utils.create_database(engine.url)
        Base.metadata.create_all(engine)
        with orm.Session(engine) as session:
            session.commit()
        return True
    return False


class Base(orm.DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: orm.Mapped[int] = orm.mapped_column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    permissions: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String, nullable=False)
    password: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String, nullable=False)
    username: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String, unique=True, nullable=False)


class Token(Base):
    __tablename__ = "tokens"
    id: orm.Mapped[int] = orm.mapped_column(sqlalchemy.ForeignKey("users.id"), primary_key=True)
    token: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String, unique=True, nullable=False, primary_key=True)
    expires: orm.Mapped[int] = orm.mapped_column(sqlalchemy.Integer, nullable=False)


class MOTHException(Exception):
    pass


class NoUserError(MOTHException):
    pass


class InvalidPasswordError(MOTHException):
    pass


class InvalidTokenError(MOTHException):
    pass


class TokenExpiredError(MOTHException):
    pass


class UserExistsError(MOTHException):
    pass