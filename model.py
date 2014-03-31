import config
import bcrypt
import requests

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric

from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

from flask.ext.login import UserMixin

engine = create_engine(config.DB_URL, echo=True) 
session = scoped_session(sessionmaker(bind=engine,
                                        autocommit = False,
                                        autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

class User(Base, UserMixin):
    __tablename__ = "users" 
    id = Column(Integer, primary_key=True)
    email = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    salt =  Column(String(64), nullable=False)
    firstname = Column(String(64), nullable=False)
    surname = Column(String(64), nullable=False)

    def set_password(self, password):
        self.salt = bcrypt.gensalt()
        password = password.encode("utf-8")
        self.password = bcrypt.hashpw(password, self.salt)

    def authenticate(self, password):
        password = password.encode("utf-8")
        return bcrypt.hashpw(password, self.salt.encode("utf-8")) == self.password

class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email = Column(String(64), nullable=False)
    address1 = Column(Text, nullable=False)
    address2 = Column(Text, nullable=True)
    city = Column(String(64), nullable=False)
    state = Column(String(2), nullable=False)
    zipcode = Column(Integer, nullable=False)
    country = Column(Text, nullable=False)
    phone = Column(Integer, nullable=True)
    lat = Column(Numeric(10, 7), nullable=True)
    lng = Column(Numeric(10, 7), nullable=True)

    user = relationship("User", backref="addresses")

    def geocode(self):
        if self.lat == None:

            self.address12=self.address1.replace(" ","+")
            self.city2=self.city.replace(" ","+")
            address = "%s+%s+%s" % (self.address12, self.city2, self.state)

            url="https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyCeMBBKrZKuJdpfnmzj7roq5XO2Q1740aY&address=%s&sensor=false" % address

            r = requests.get(url)
           # print "response: %r" % r.json()
            jsongeocode = r.json()

            latlng = jsongeocode["results"][0]["geometry"]["location"]
            self.lat = latlng["lat"]
            self.lng = latlng["lng"]

            #print "lat: %s, lng: %s" % (self.lat, self.lng)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", backref="orders")
    
class Duck(Base):
    __tablename__ = "ducks"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    pic = Column(String(50), nullable=False) 
    price = Column(String(10), nullable=False)
    bio = Column(Text, nullable=False)

class DuckOrder(Base):
    __tablename__ = "duckorders"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    duck_id = Column(Integer, ForeignKey("ducks.id"))
    qty = Column(Integer, nullable=False)

    order = relationship("Order", backref="duckorders")
    duck = relationship("Duck", backref="duckorders")
    
def create_tables():
    #Base.metadata.drop_all(engine) #this is for droping all tables for a fresh start.
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    create_tables()
    
