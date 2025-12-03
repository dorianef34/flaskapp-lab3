import pytest
from app import create_app, db
from models import User, Task

@pytest.fixture
def app():
    app = create_app(testing=True)
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", 
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_and_login(client):
    response = client.post(
        "/register",
        data={"username": "testuser", "password": "pass", "confirm": "pass"},
        follow_redirects=True
    )
    assert b"Registration successful" in response.data

    response = client.post(
        "/login",
        data={"username": "testuser", "password": "pass"},
        follow_redirects=True
    )
    assert b"Logged in successfully" in response.data

def test_create_task(client, app):
    with app.app_context():
        user = User(username="taskuser")
        user.set_password("pass")
        db.session.add(user)
        db.session.commit()

    client.post("/login", data={"username": "taskuser", "password": "pass"}, follow_redirects=True)

    response = client.post(
        "/tasks/new",
        data={"title": "My Task", "description": "Test Task", "due_date": ""},
        follow_redirects=True
    )
    assert b"Task created" in response.data

def test_edit_and_toggle_task(client, app):
    with app.app_context():
        user = User(username="edituser")
        user.set_password("pass")
        db.session.add(user)
        db.session.commit()

        task = Task(title="Initial Task", user_id=user.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    client.post("/login", data={"username": "edituser", "password": "pass"}, follow_redirects=True)

    response = client.post(
        f"/tasks/{task_id}/edit",
        data={"title": "Updated Task", "description": "Updated", "due_date": "", "is_completed": "y"},
        follow_redirects=True
    )
    assert b"Task updated" in response.data

    response = client.post(f"/tasks/{task_id}/toggle", follow_redirects=True)
    assert b"Task status updated" in response.data
