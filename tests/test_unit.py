import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date, timedelta
from app import _build_postgres_uri
from models import Task, User

def test_build_postgres_uri(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "doria")
    monkeypatch.setenv("POSTGRES_PASSWORD", "MotDePasse123")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.setenv("POSTGRES_DB", "taskmanager")

    uri = _build_postgres_uri()
    assert uri == "postgresql+psycopg://doria:MotDePasse123@localhost:5433/taskmanager"

def test_user_password():
    user = User(username="testuser")
    user.set_password("mypassword")
    
    assert user.check_password("mypassword")
    assert not user.check_password("wrongpassword")

def test_task_is_overdue():
    task1 = Task(title="Overdue task", due_date=date.today() - timedelta(days=1))
    assert task1.is_overdue() is True

    task2 = Task(title="Future task", due_date=date.today() + timedelta(days=1))
    assert task2.is_overdue() is False

    task3 = Task(title="No due date task", due_date=None)
    assert task3.is_overdue() is False
