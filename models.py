from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Date


class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    amount = Column(Float)
    type = Column(String)
    category = Column(String)
    Transaction_date = Column(Date)
    owner_id = Column(Integer, ForeignKey("users.id"))



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)

