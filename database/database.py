from sqlalchemy.orm import sessionmaker
from .models import Base
from sqlalchemy import create_engine


class Database:
    def __init__(self):
        self.engine = create_engine("sqlite:///database.db", echo=True, future=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def session(self):
        return self.SessionLocal()