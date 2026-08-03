from sqlalchemy import Integer, String, Column, DateTime, func, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class URL(Base):
    __tablename__ = 'urls'
    
    id = Column(Integer, primary_key= True)
    short_code = Column(String, unique= True, nullable= False)
    long_url = Column(String, nullable= False)
    click_count = Column(Integer, default= 0)
    created_at = Column(DateTime, server_default= func.now())
    
DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/urlshortener"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(engine)