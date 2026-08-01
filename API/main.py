from fastapi import FastAPI, Depends
# import TestClient
from fastapi.testclient import TestClient

from database.database import Database
from database.models import Users, Projects, ServiceProjects

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
@app.get("/projects")
def get_projects(db=Depends(get_db)):
    return db.query(Projects).all()
@app.get("/project/{project_id}")
def get_project(project_id: int, db=Depends(get_db)):
    return db.get(Projects, project_id)
@app.get("/service_projects")
def get_service_projects(db=Depends(get_db)):
    return db.query(ServiceProjects).all()
@app.get("/service_project/{service_project_id}")
def get_service_project(service_project_id: int, db=Depends(get_db)):
    return db.get(ServiceProjects, service_project_id)
@app.get("/last_project_number")
def get_last_project_number(db=Depends(get_db)):
    last_project = db.query(Projects).order_by(Projects.number.desc()).first()
    if last_project:
        return last_project.number
    else:
        return 1
@app.post("/register")
def sign_up(email: str, password: str, db=Depends(get_db)):
    existing_user = db.query(Users).filter(Users.email == email).first()
    if existing_user:
        return False
    user = Users(email=email, password=password)
    db.add(user)
    db.commit()
    return True
@app.post("/new_project")
def create_project(project_name: str, db=Depends(get_db)):
    pass