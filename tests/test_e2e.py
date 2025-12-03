import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import create_app
from extensions import db


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_e2e_register_login(client):
    # REGISTER
    resp = client.post("/register", data={
        "username": "john",
        "password": "secret123",
        "confirm": "secret123",
    }, follow_redirects=True)

    assert b"Registration successful" in resp.data

    resp = client.post("/login", data={
        "username": "john",
        "password": "secret123",
    }, follow_redirects=True)

    assert b"Logged in successfully" in resp.data

    assert b"Tasks" in resp.data or b"task" in resp.data.lower()


def test_e2e_create_task(client):
    client.post("/register", data={
        "username": "alice",
        "password": "pass123",
        "confirm": "pass123",
    }, follow_redirects=True)

    client.post("/login", data={
        "username": "alice",
        "password": "pass123",
    }, follow_redirects=True)

    resp = client.post("/tasks/new", data={
        "title": "Faire les courses",
        "description": "Acheter du lait",
        "due_date": "2025-01-10"
    }, follow_redirects=True)

    assert b"Task created" in resp.data
    assert b"Faire les courses" in resp.data

def test_e2e_toggle_task(client):
    client.post("/register", data={
        "username": "bob",
        "password": "pass123",
        "confirm": "pass123",
    }, follow_redirects=True)
    client.post("/login", data={
        "username": "bob",
        "password": "pass123",
    }, follow_redirects=True)

    client.post("/tasks/new", data={
        "title": "Réviser",
        "description": "",
        "due_date": ""
    }, follow_redirects=True)

    from models import Task
    task = Task.query.first()
    task_id = task.id

    resp = client.post(f"/tasks/{task_id}/toggle", follow_redirects=True)

    assert b"Task status updated" in resp.data

    task = Task.query.get(task_id)
    assert task.is_completed is True
