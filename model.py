import config
import bcrypt
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Text

from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

engine = create_engine(config.DB_URI, echo=False) 
session = scoped_session(sessionmaker(bind=engine,
                         autocommit = False,
                         autoflush = False))

Base = declarative_base()
Base.query = session.query_property

class User(Base):
    __tablename__ = "users" 
    id = Column(Integer, primary_key=True)
    email = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    salt = Column(String(64), nullable=False)

    posts = relationship("Post", uselist=True)

    def set_password(self, password):
        self.salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(password, self.salt)

    def authenticate(self, password):
        return bcrypt.hashpw(password, self.salt) == self.password

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(64), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    posted_at = Column(DateTime, nullable=True, default=None)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")


def create_tables():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    create_tables()
