import pytest # to run the test do 'python -m pytest' in terminal
from src.models import Task, Student, Status
from datetime import datetime

# Requirement #9 from prof: Automated Testing
# Run this by typing 'pytest' in terminal

def test_create_task():
    """checks if tasks initialize correctly with all fields"""
    task = Task(
        task_id = 1,
        title = "Lab 4",
        date_assigned = datetime.now(),
        due_date = datetime(2025, 12, 31),
        weighted_percent = 20.0,
        points_earned = 0.0,
        task_status = Status.TODO,
        total_work_time = 0.0
    )

    assert task.title == "Lab 4"
    assert task.weighted_percent == 20.0
    assert task.task_status == Status.TODO # check against the enum not string

def test_student_password_hashing():
    """Checks if bcrypt is actually hashing the password"""
    student = Student(
        email = "test@dal.ca",
        student_id = 123456,
        password_hash = ""
    )

    student.set_password("secure123")

    # password should not be stored in plain text
    assert student.password_hash != "secure123"
    assert student.password_hash != ""

    # check that the password verifies correctly
    assert student.check_password("secure123") is True
    assert student.check_password("wrongpassword") is False