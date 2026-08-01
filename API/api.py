from fastapi import FastAPI, Depends, HTTPException, status
# import TestClient
from fastapi.testclient import TestClient
from database.database import Database
from database.models import Users, Projects, ServiceProjects
from sqlalchemy.orm import defer
from API.pydantic_models  import ServiceProjectSchema
from sqlalchemy.orm import Session
from datetime import datetime
import base64

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

@app.get("/projects/{project_id}")
def get_project_by_id(project_id: int, db=Depends(get_db)):
    return db.get(Projects, project_id)

@app.get("/employees")
def get_employees(db = Depends(get_db)):
    users = db.query(Users).all()
    return users

@app.get("/employees/{user_id}")
def get_user_by_id(user_id: int, db: Session =Depends(get_db)):
    user = db.get(Users, user_id)
    return user

@app.patch("/employees/{user_id}")
def update_user_role(user_id: int, new_role: str, db: Session = Depends(get_db)):
    user = db.get(Users, user_id)
    if user:
        user.role = new_role
        db.commit()
        db.refresh(user)
    return user

@app.get("/service_projects", response_model=list[ServiceProjectSchema])
def get_service_projects(db=Depends(get_db)):
    service_projects = db.query(ServiceProjects).options(defer(ServiceProjects.pdf_form)).all()
    return service_projects

@app.get("/service_project/{service_project_id}")
def get_service_project(service_project_id: int, db=Depends(get_db)):
    project = db.get(ServiceProjects, service_project_id)
    project_dictionary = project.to_dict()
    if project.pdf_form:
        project_dictionary["pdf_form"] = base64.b64encode(project.pdf_form).decode("utf-8")
    return project_dictionary
@app.get("/user/{user_id}")
def get_user(user_id: int, db=Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    return user


@app.post("/service_projects/new")
def create_service_project(new_project:ServiceProjectSchema
                           , db=Depends(get_db)):
    last_project = (
        db.query(ServiceProjects)
        .order_by(ServiceProjects.id.desc())  # or ServiceProjects.number.desc()
        .first()
    )
    if last_project:
        last_number = int(last_project.number[-3:])
        actual_number = last_number + 1
        formatted_actual_number = f"{actual_number:03d}"
        actual_number = str(datetime.now().year) + "/" + str(formatted_actual_number)
    else:
        actual_number = str(datetime.now().year) + "/001"


    new_project = ServiceProjects(
        number=actual_number,
        owner=new_project.owner,
        start_date=new_project.start_date,
        phone_number=new_project.phone_number,
        email=new_project.email,
        manufacturer=new_project.manufacturer,
        model=new_project.model,
        code=new_project.code,
        serial_number=new_project.serial_number,
        description=new_project.description,
        repair_time=new_project.repair_time,
        active=new_project.active,
        tasks=new_project.tasks,
        service_parts=new_project.service_parts,
        pdf_form=new_project.pdf_form
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
    db.refresh(project)
    return None
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