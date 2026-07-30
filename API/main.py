from fastapi import FastAPI, Depends
# import TestClient
from fastapi.testclient import TestClient

from database.database import Database
from database.models import Users

app = FastAPI()
database = Database()

def get_db():
    session = database.session()
    try:
        yield session
    finally:
        session.close()
client = TestClient(app)

@app.get("/login")
def password_validation(user_email: str, user_password: str, db=Depends(get_db)):
    user = db.query(Users).filter(Users.email == user_email, Users.password == user_password).first()

    if user:
        return {"user_id": user.id}
    else:
        return False