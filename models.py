from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, engine, desc
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash


dbstring = 'postgres:admin@localhost:5432/ToDo'

engine = create_engine('postgresql+psycopg2://' + dbstring, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                            bind= engine))

Base = declarative_base()
Base.query = db_session.query_property()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String(20), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    active = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return '<Users {}>'.format(self.login)
    
    def __init__(self, login, password, email, active):
        self.login = login
        self.password = generate_password_hash(password)
        self.email = email
        self.active = active
    
    def set_password(self, password):
        return generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def deactive_user(self):
        self.active = 0
    
    def get_id(self):
        return self.id

    def save(self):
        db_session.add(self)
        db_session.commit()
    
    def delete(self):
        db_session.delete(self)
        db_session.commit()

class ToDo(Base):
    __tablename__ = 'todo'
    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    details = Column(String(250))
    status = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User')

    def __repr__(self):
        return '<name= {}, details {}, status= {}, >'.format(self.name, self.details, self.status)
    
    def save(self):
        db_session.add(self)
        db_session.commit()
    
    def delete(self):
        db_session.delete(self)
        db_session.commit()

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()