from typing import List, Optional # 'List' is a type hint that says "this variable holds a list of things".
from dataclasses import dataclass, field
from enum import IntEnum
import datetime
import bcrypt

class Type(IntEnum):
    LECTURE = 1
    STUDY = 2
    CLASSWORK = 3

class Status(IntEnum):
    TODO = 1
    IN_PROGRESS = 2
    DONE = 3

@dataclass
class Student:
    """
    The Student class stores all information related to one user of the system.

    This class does NOT handle:
        - timing study sessions
        - saving/loading files
        - analytics calculations

    Those responsibilities are handled by other components
    (SessionController, DatabaseHandler, AnalyticsEngine).

    Student is simply a data container.
    """

    email: str # student's login email (must be unique)
    password_hash: str # encrypted password (bcrypt will be used for hashing)
    student_id: int # internal student number (must be unique)
    
    # Lists of objects connected to this student
    # These default to empty lists using field(default_factory=list)
    # This will ensure each Student instance has its own separate lists

    courses: List["Course"] = field(default_factory=list)
    tasks: List["Task"] = field(default_factory=list)
    study_sessions: List["StudySession"] = field(default_factory=list)

    def add_course(self, course: "Course") -> None:
        """
        Adds a course to the student's list of courses.
        The Student does not create courses, the UI or controller will.
        """
        self.courses.append(course)

    def add_task(self, task: "Task") -> None:
        """Adds a task to the student's global list of tasks.
        
        Note:
        - Tasks also belong to specific courses.
        - This method simply stores a copy here so AnalyticsEngine and other
          components can quickly access all tasks in one place.
        """
        self.tasks.append(task)
        """
        * Is a seperate global list of tasks necessary? We could instead just cycle each through each course and take the list of tasks from there. *
        * Just since a global list would mostly be for viewing so the Student class wouldn't need immediate access to it. *
        * Same with study sessions as well. *
        """

    def add_study_session(self, session: "StudySession") -> None:
        """
        Stores a completed study session.
        
        The SessionController creates the session and calculates its duration.
        """
        self.study_sessions.append(session)

    # Added authentication methods (bcrypt) for password handling, because main.py requires secure login
    def set_password(self, password_plain):
        self.password_hash = bcrypt.hashpw(password_plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password_plain):
        if not self.password_hash: return False
        return bcrypt.checkpw(password_plain.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            "email": self.email,
            "password_hash": self.password_hash,
            "student_id": self.student_id,
            "courses": [c.to_dict() for c in self.courses],
            "tasks": [t.to_dict() for t in self.tasks],
            "study_sessions": [s.to_dict() for s in self.study_sessions],
        }

@dataclass
class Course:
    """
    The Course class stores all information related to one of a users courses.

    This class does NOT handle:
        - timing study sessions
        - saving/loading files
        - analytics calculations

    Those responsibilities are handled by other components
    (SessionController, DatabaseHandler, AnalyticsEngine).

    Course is simply a data container.
    """

    course_id: str # the course id, example ECED 3500 followed by the name of the course (must be unique)
    hours_study: float # the number of hours the student has spent studying for this course
    hours_lecture: float # the number of hours spent in lecture for this course
    hours_classwork: float # the number of hours spent working on classwork for this course
    grade_percent: float # total grade percentage earned for this course

    # Lists of objects connected to this course
    # These default to empty lists using field(default_factory=list)
    # This will ensure each Course instance has its own separate lists

    tasks: List["Task"] = field(default_factory=list)
    calendar: List["Day"] = field(default_factory=list)

    def add_task(self, task: "Task") -> None:
        #Adds a task to this course's list of tasks.
        self.tasks.append(task)

    def add_day(self, day: "Day") -> None:
        # Stores a completed day.
        self.calendar.append(day)

    # Added the to_dict() method to all classes in this file so storage.py can save them to JSON
    def to_dict(self):
        return {
            "course_id": self.course_id,
            "hours_study": self.hours_study,
            "hours_lecture": self.hours_lecture,
            "hours_classwork": self.hours_classwork,
            "grade_percent": self.grade_percent,
            "tasks": [t.to_dict() for t in self.tasks],
            "calendar": [d.to_dict() for d in self.calendar],
        }

@dataclass
class Task:
    """
    The Task class stores all information related to a specific task.

    This class does NOT handle:
        - timing study sessions
        - saving/loading files
        - analytics calculations

    Those responsibilities are handled by other components
    (SessionController, DatabaseHandler, AnalyticsEngine).

    Task is simply a data container.
    """

    task_id: int # unique identifier for the task
    title: str # name for the task
    date_assigned: datetime # date the task was assigned
    due_date: datetime # due date for the task
    weighted_percent: float # percentage of the total grade this task is worth
    points_earned: float # grade earned on this task
    task_status: Status # tracks whether the task is to be started, in progress or finished
    total_work_time: float # total time spent working on the task

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "title": self.title,
            "date_assigned": str(self.date_assigned),
            "due_date": str(self.due_date),
            "weighted_percent": self.weighted_percent,
            "points_earned": self.points_earned,
            "task_status": self.task_status,
            "total_work_time": self.total_work_time,
        }

@dataclass
class StudySession:
    """
    The StudySession class stores all information related to a specific study session.

    This class does NOT handle:
        - timing study sessions
        - saving/loading files
        - analytics calculations

    Those responsibilities are handled by other components
    (SessionController, DatabaseHandler, AnalyticsEngine).

    StudySession is simply a data container.
    """

    session_id: int # unique identifier for the study session
    start_time: datetime # when the study session started
    duration_minutes: int # how long the study session was in minutes
    session_type: Type # determines whether the session is a study, work or lecture section

    # Changed to Optional so the app doesn't crash if a student starts a session without selecting a task
    session_task: Optional["Task"] = None

    def to_dict(self):
        # Handle polymorphic data: session_task might be a Task object OR an integer ID
        task_data = None
        
        if self.session_task:
            # Check if it has a .to_dict method (meaning it's a real Task object)
            if hasattr(self.session_task, 'to_dict'):
                task_data = self.session_task.to_dict()
            else:
                # If not (it's likely an int ID loaded from JSON), just save the raw value
                task_data = self.session_task

        return {
            "session_id": self.session_id,
            "start_time": str(self.start_time),
            "duration_minutes": self.duration_minutes,
            "session_type": self.session_type,
            "session_task": task_data
        }

@dataclass
class Day:
    """
    The Day class stores all information related to a specific day for a specific course.

    This class does NOT handle:
        - timing study sessions
        - saving/loading files
        - analytics calculations

    Those responsibilities are handled by other components
    (SessionController, DatabaseHandler, AnalyticsEngine).

    Day is simply a data container.
    """

    date: datetime # the calendar date
    productivity_score: float # computed score based on work / time

    # List of objects connected to this course
    # These default to empty lists using field(default_factory=list)
    # This will ensure each Course instance has its own separate lists
    study_sessions: List["StudySession"] = field(default_factory=list)
    tasks: List["Task"] = field(default_factory=list)

    def add_study_session(self, session: "StudySession") -> None:
        """
        Stores a completed study session.
        
        The SessionController creates the session and calculates its duration.
        """
        self.study_sessions.append(session)

    def add_task(self, task: "Task") -> None:
        #Adds a task to this course's list of tasks.
        self.tasks.append(task)

    def to_dict(self):
        return {
            "date": str(self.date),
            "productivity_score": self.productivity_score,
            "study_sessions": [s.to_dict() for s in self.study_sessions],
            "tasks": [t.to_dict() for t in self.tasks],
        }