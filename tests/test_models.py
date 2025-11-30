import pytest
from src.models import Task, Student

# Requirement #9 from prof: Automated Testing
# Run this by typing 'pytest' in terminal

def test_create_task():
    """checks if tasks init correctly"""
    task = Task(1, "Lab 4", "2025-11-30", 20.0)
    assert task.title == "Lab 4"
    assert task.weight_percent == 20.0
    assert task.status == "To Do" # default should be To Do

def test_student_password_hashing():
    """checks if bcrypt is actually hashing the password"""
    student = Student("test@dal.ca", password_plain="secure123")
    
    # password should NOT be stored as plain text
    assert student.password_hash != "secure123"
    
    # check if the verify function works
    assert student.check_password("secure123") is True
    assert student.check_password("wrongpass") is False
