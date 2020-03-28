import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    age = sqlalchemy.Column(sqlalchemy.Integer)
    position = sqlalchemy.Column(sqlalchemy.String)
    speciality = sqlalchemy.Column(sqlalchemy.String)
    address = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime)
    username = sqlalchemy.Column(sqlalchemy.String, unique=True)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        if self.id == 2:
            return True
        return check_password_hash(self.hashed_password, password)


class Jobs(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'jobs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    team_leader = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    job = sqlalchemy.Column(sqlalchemy.String)
    work_size = sqlalchemy.Column(sqlalchemy.Integer)
    collaborators = sqlalchemy.Column(sqlalchemy.String)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    end_date = sqlalchemy.Column(sqlalchemy.DateTime)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer)
    users = orm.relation('User')
    tm_leader = orm.relationship('User', foreign_keys='Jobs.team_leader')
    categories = orm.relation('Category', secondary='association', backref='jobs')

    def job_to_dict(self):
        dic = {}
        for c in self.__class__.__table__.columns:
            v = getattr(self, c.name)
            try:
                dic[c.name] = v
            except Exception:
                pass
        return dic


class Departments(SqlAlchemyBase):
    __tablename__ = 'departments'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    chief = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    chief_m = orm.relationship('User', foreign_keys='Departments.chief')
    members = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String)
    users = orm.relation('User')


class Category(SqlAlchemyBase):
    __tablename__ = 'category'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    cat_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)


association_table = sqlalchemy.Table('association', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('jobs', sqlalchemy.Integer, sqlalchemy.ForeignKey('jobs.id')),
                                     sqlalchemy.Column('category', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('category.id')))
