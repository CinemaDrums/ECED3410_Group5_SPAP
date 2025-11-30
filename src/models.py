from typing import List # 'List' is a type hint that says "this variable holds a list of things".
from dataclasses import dataclass, field # 

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

    def add_study_session(self, session: "StudySession") -> None:
        """
        Stores a completed study session.
        
        The SessionController creates the session and calculates its duration.
        """
        self.study_sessions.append(session)