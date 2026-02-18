from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
database_url = "sqlite:///database.sqlite"

engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

def init_db():
    from app.models import User
    from app.models import Music_Playlists, Songs

    Base.metadata.create_all(bind=engine)
   