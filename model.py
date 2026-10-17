from database import Base
from sqlalchemy import Column,Integer,String,Float,Date,ForeignKey
from datetime import date

class Users(Base):
    __tablename__='users'

    id=Column(Integer,primary_key=True,index=True)
    username=Column(String,unique=True)
    email=Column(String,unique=True)
    hash_password=Column(String)

class Transactions(Base):
    __tablename__='transactions'
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String)
    amount=Column(Float)
    type=Column(String)
    category = Column(String)
    date = Column(Date, default=date.today)
    owner_id = Column(Integer, ForeignKey("users.id"))
    

