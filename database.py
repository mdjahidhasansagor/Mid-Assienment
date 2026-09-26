from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:12345678@127.0.0.1:3306/transactiontable'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()