from sqlalchemy import Integer, String, Column, DateTime, func, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

Base = declarative_base()

load_dotenv()

class URL(Base):
    __tablename__ = 'urls'
    
    id = Column(Integer, primary_key= True)
    short_code = Column(String, unique= True, nullable= False)
    long_url = Column(String, nullable= False)
    click_count = Column(Integer, default= 0)
    created_at = Column(DateTime, server_default= func.now())

Username = os.environ['DB_Username']
Password = os.environ['DB_Password']
Host = os.environ['DB_Host']
Port = os.environ['DB_Port']
DB_Name = os.environ['DB_Name']
    
DATABASE_URL = f"postgresql://{Username}:{Password}@{Host}:{Port}/{DB_Name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()