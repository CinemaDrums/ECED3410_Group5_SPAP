from typing import List # 'List' is a type hint that says "this variable holds a list of things".
from dataclasses import dataclass, field # 
from enum import Enum
import datetime

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
        Is a seperate global list of tasks necessary? We could instead just cycle each through each course and take the list of tasks from there.
        Just since a global list would mostly be for viewing so the Student class wouldn't need immediate access to it.
        Same with study sessions as well.
        """

    def add_study_session(self, session: "StudySession") -> None:
        """
        Stores a completed study session.
        
        The SessionController creates the session and calculates its duration.
        """
        self.study_sessions.append(session)

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
    study_sessions: List["StudySession"] = field(default_factory=list)

    def add_task(self, task: "Task") -> None:
        #Adds a task to this course's list of tasks.
        self.tasks.append(task)

    def add_study_session(self, session: "StudySession") -> None:
        """
        Stores a completed study session.
        
        The SessionController creates the session and calculates its duration.
        """
        self.study_sessions.append(session)

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
    # Enum goes here
    total_work_time: float # total time spent working on the task

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

    sesion_id: int # unique identifier for the study session
    start_time: datetime # when the study session started
    duration_minutes: int # how long the study session was in minutes
    # Enum goes here
    # Task goes here (does anything specific need to be done for an optional attribute?)