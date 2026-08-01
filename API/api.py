from fastapi import FastAPI, Depends, HTTPException, status
# import TestClient
from fastapi.testclient import TestClient
from database.database import Database
from database.models import Users, Projects, ServiceProjects
from sqlalchemy.orm import defer
from API.pydantic_models  import ServiceProjectSchema
from sqlalchemy.orm import Session

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
def password_validation(
    user_email: str, user_password: str, db: Session = Depends(get_db)
):
    user = (
        db.query(Users)
        .filter(Users.email == user_email, Users.password == user_password)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return {"user_id": user.id}
@app.get("/projects")
def get_projects(db=Depends(get_db)):
    return db.query(Projects).all()
@app.get("/project/{project_id}")
def get_project(project_id: int, db=Depends(get_db)):
    return db.get(Projects, project_id)
@app.get("/service_projects", response_model=list[ServiceProjectSchema])
def get_service_projects(db=Depends(get_db)):
    service_projects = db.query(ServiceProjects).options(defer(ServiceProjects.pdf_form)).all()
    return service_projects
@app.get("/user/{user_id}")
def get_user(user_id: int, db=Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    return user
@app.get("/service_project/{service_project_id}")
def get_service_project(service_project_id: int, db=Depends(get_db)):
    return db.get(ServiceProjects, service_project_id)

@app.post("/new_service_project")
def create_service_project(
    number: str,
    owner: str,
    start_date: str,
    phone_number: str = None,
    email: str = None,
    manufacturer: str = None,
    model: str = None,
    code: str = None,
    serial_number: str = None,
    description: str = "",
    db=Depends(get_db)
):
    from datetime import datetime
    dt_start = datetime.strptime(start_date, "%Y-%m-%d")
    new_project = ServiceProjects(
        number=number,
        owner=owner,
        start_date=dt_start,
        phone_number=phone_number,
        email=email,
        manufacturer=manufacturer,
        model=model,
        code=code,
        serial_number=serial_number,
        description=description
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project.id

@app.patch("/service_project/{service_project_id}")
def update_service_project(service_project_id: int, data: dict, db=Depends(get_db)):
    project = db.get(ServiceProjects, service_project_id)
    if not project:
        return False
    for key, value in data.items():
        if hasattr(project, key):
            if key in ['start_date', 'end_date'] and value:
                from datetime import datetime
                value = datetime.fromisoformat(value)
            if key == "pdf_form" and value:
                import base64
                value = base64.b64decode(value)
            setattr(project, key, value)
    db.commit()
    return True
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
def create_project(name: str, number: int, description: str, project_owner: int, db=Depends(get_db)):
    from datetime import datetime
    project = Projects(
        name=name,
        number=number,
        description=description,
        is_active=True,
        project_owner=str(project_owner),
        beginning=datetime.now()
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project.id

@app.delete("/project/{project_id}")
def delete_project(project_id: int, db=Depends(get_db)):
    project = db.get(Projects, project_id)
    if project:
        db.delete(project)
        db.commit()
        return True
    return False

@app.delete("/service_project/{service_project_id}")
def delete_service_project(service_project_id: int, db=Depends(get_db)):
    service_project = db.get(ServiceProjects, service_project_id)
    if service_project:
        db.delete(service_project)
        db.commit()
        return True
    return False