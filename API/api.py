from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy import desc
from fastapi.responses import FileResponse

from database.database import Database
from database.models import Users, Projects, ServiceProjects, ProjectItems, ProjectActivities, ProjectTodos, AppMetadata
from sqlalchemy.orm import defer
from API.pydantic_models import ServiceProjectSchema, ProjectSchema, ProjectItemSchema, \
    ProjectActivitySchema, ProjectTodoSchema
from sqlalchemy.orm import Session
from datetime import datetime
import base64

app = FastAPI()
database = Database()

DOWNLOAD_DIR = "C:/server/downloads/app"

def get_db():
    session = database.session()
    try:
        yield session
    finally:
        session.close()

API_CLIENT = TestClient(app)

# Login and Register Routes
@app.get("/login")
def password_validation(
    user_email: str, user_password: str, db: Session = Depends(get_db)):
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
@app.post("/register")
def sign_up(email: str, password: str, db=Depends(get_db)):
    existing_user = db.query(Users).filter(Users.email == email).first()
    if existing_user:
        return False
    user = Users(email=email, password=password)
    db.add(user)
    db.commit()
    return True

# APP VERSION
@app.get("/app_metadata/latest_version")
def get_app_metadata(db = Depends(get_db)):
    return db.query(AppMetadata).order_by(desc(AppMetadata.version)).first()
@app.get("/app_metadata/{current_version}")
def get_app_metadata(current_version: str, db = Depends(get_db)):
    return db.query(AppMetadata).filter(AppMetadata.version == current_version).first()
@app.get("/app_metadata/download/latest")
def download_latest_version(db = Depends(get_db)):
    latest_version = db.query(AppMetadata).order_by(desc(AppMetadata.id)).first()
    if latest_version is None:
        raise HTTPException(
            status_code=404,
            detail="No application version found"
        )
    path = latest_version.download_url
    filename = latest_version.filename
    return FileResponse(path=path, media_type="application/octet-stream", filename=filename)
@app.get("/app_metadata/download/{version}")

# Projects Page routes
@app.get("/projects", response_model=list[ProjectSchema])
def get_projects(db=Depends(get_db), ):
    return db.query(Projects).all()
@app.get("/projects/last_project_number")
def get_last_project_number(db=Depends(get_db)):
    last_project = db.query(Projects).order_by(Projects.number.desc()).first()
    if last_project:
        return last_project.number + 1
    else:
        return 1
@app.get("/projects/{project_id}")
def get_project_by_id(project_id: int, db=Depends(get_db)):
    return db.get(Projects, project_id)
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

# Project Items Routes
@app.get("/projects/{project_id}/items/", response_model=list[ProjectItemSchema])
def get_project_items(project_id: int, db=Depends(get_db)):
    project_items = db.query(ProjectItems).filter(ProjectItems.project_id == project_id).all()
    return project_items
@app.get("/projects/project/items/{item_id}", response_model=ProjectItemSchema)
def get_item_by_id(item_id: int, db=Depends(get_db)):
    item = db.get(ProjectItems, item_id)
    if item:
        return item
    else:
        raise HTTPException(status_code=404, detail="Item not found")
@app.patch("/projects/project/items/{item_id}/update/",status_code=status.HTTP_202_ACCEPTED)
def update_project_item(item_id: int, data: dict, db=Depends(get_db)):
    item = db.get(ProjectItems, item_id)
    if item:
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        db.commit()
        return True
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
@app.post("/projects/project/items/new", status_code=status.HTTP_201_CREATED)
def create_project_item(new_item:ProjectItemSchema, db=Depends(get_db)):
    new_project_item = ProjectItems(**new_item.model_dump(exclude={"id"}))
    db.add(new_project_item)
    db.commit()
    db.refresh(new_project_item)
    return new_project_item
@app.delete("/projects/project/items/{item_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_by_id(item_id: int, db=Depends(get_db)):
    item = db.get(ProjectItems, item_id)
    if item:
        db.delete(item)
        db.commit()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

# Project Activities Routes
@app.get("/projects/{project_id}/activities/", response_model=list[ProjectActivitySchema])
def get_project_activities(project_id: int, db=Depends(get_db)):
    project_activities = db.query(ProjectActivities).filter(ProjectActivities.project_id == project_id).all()
    return project_activities
@app.get("/projects/project/activities/{activity_id}", response_model=ProjectActivitySchema)
def get_activity_by_id(activity_id: int, db=Depends(get_db)):
    activity = db.get(ProjectActivities, activity_id)
    if activity:
        return activity
    else:
        raise HTTPException(status_code=404, detail="Activity not found")
@app.post("/projects/project/activities/new", status_code=status.HTTP_201_CREATED)
def create_project_activity(new_activity:ProjectActivitySchema, db=Depends(get_db)):
    new_project_activity = ProjectActivities(**new_activity.model_dump(exclude={"id"}))
    db.add(new_project_activity)
    db.commit()
    db.refresh(new_project_activity)
    return new_project_activity
@app.patch("/projects/project/activities/{activity_id}/update/", status_code=status.HTTP_202_ACCEPTED)
def update_project_activity(activity_id: int, data: dict, db=Depends(get_db)):
    activity = db.get(ProjectActivities, activity_id)
    if activity:
        for key, value in data.items():
            if hasattr(activity, key):
                setattr(activity, key, value)
        db.commit()
        db.refresh(activity)
        return True
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
@app.delete("/projects/project/activities/{activity_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity_by_id(activity_id: int, db=Depends(get_db)):
    activity = db.get(ProjectActivities, activity_id)
    if activity:
        db.delete(activity)
        db.commit()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

# Project Todos Routes
@app.get("/projects/{project_id}/todos/", response_model=list[ProjectTodoSchema])
def get_project_todos(project_id: int, db=Depends(get_db)):
    project_todos = db.query(ProjectTodos).filter(ProjectTodos.project_id == project_id).all()
    return project_todos
@app.get("/projects/project/todos/{todo_id}", status_code=status.HTTP_200_OK, response_model=ProjectTodoSchema)
def get_todo_by_id(todo_id: int, db=Depends(get_db)):
    todo = db.get(ProjectTodos, todo_id)
    if todo:
        return todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
@app.post("/projects/project/todos/new", status_code=status.HTTP_201_CREATED)
def create_project_todo(new_todo:ProjectTodoSchema, db=Depends(get_db)):
    new_project_todo = ProjectTodos(**new_todo.model_dump(exclude={'id'}))
    db.add(new_project_todo)
    db.commit()
    db.refresh(new_project_todo)
    return new_project_todo
@app.patch("/projects/project/todos/{todo_id}/update/", status_code=status.HTTP_202_ACCEPTED)
def update_project_todo(todo_id: int, data: dict, db=Depends(get_db)):
    todo = db.get(ProjectTodos, todo_id)
    if todo:
        for key, value in data.items():
            if hasattr(todo, key):
                setattr(todo, key, value)
        db.commit()
        return True
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
@app.delete("/projects/project/todos/{todo_id}/delete", status_code=status.HTTP_200_OK, response_model=ProjectTodoSchema)
def delete_todo_by_id(todo_id: int, db = Depends(get_db)):
    todo = db.get(ProjectTodos, todo_id)
    if todo:
        db.delete(todo)
        db.commit()
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")


# Users Routes
@app.get("/users")
def get_employees(db = Depends(get_db)):
    users = db.query(Users).all()
    return users
@app.get("/users/{user_id}")
def get_user_by_id(user_id: int, db: Session =Depends(get_db)):
    user = db.get(Users, user_id)
    return user
@app.patch("/users/{user_id}")
def update_user(user_id: int, data: dict, db: Session = Depends(get_db)):
    user = db.get(Users, user_id)
    if not user:
        return False
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return None

# Service Projects routes
@app.get("/service_projects", response_model=list[ServiceProjectSchema])
def get_service_projects(db=Depends(get_db)):
    service_projects = db.query(ServiceProjects).options(defer(ServiceProjects.pdf_form)).all()
    return service_projects
@app.get("/service_projects/{service_project_id}")
def get_service_project(service_project_id: int, db=Depends(get_db)):
    project = db.get(ServiceProjects, service_project_id)
    project_dictionary = project.to_dict()
    if project.pdf_form:
        project_dictionary["pdf_form"] = base64.b64encode(project.pdf_form).decode("utf-8")
    return project_dictionary
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
@app.delete("/service_project/{service_project_id}")
def delete_service_project(service_project_id: int, db=Depends(get_db)):
    service_project = db.get(ServiceProjects, service_project_id)
    if service_project:
        db.delete(service_project)
        db.commit()
        return True
    return False
@app.patch("/service_projects/{service_project_id}")
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








