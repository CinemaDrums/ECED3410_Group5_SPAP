import time
from models import StudySession, Task, Type

class SessionController:
    """
    Handles the logic for the timing and management of study sessions.
    Connects the user interface (main.py) to the data (models.py).
    """
    def __init__(self):
        # The actual session object we are building
        self.active_session = None

        # The exact time (in seconds) when "Start" was pressed
        self.start_timestamp = None

        # The task currently being worked on (if any)
        self.current_task = None

    def start_session(self, session_type = Type.STUDY, task = None):
        """
        Starts the timer.
        Defaults to 'STUDY' type if they don't specify.
        Defaults to 'None' for task if they don't specify.
        """

        # Capture the current timestamp ("Start" click)
        self.start_timestamp = time.time()
        self.current_task = task

        # Create the temporary session object
        # Giving it ID = 0 for now because the database will handle IDs later
        # Passing 0 for duration because it just started
        self.active_session = StudySession(
            session_id = 0,
            start_time = self.start_timestamp,
            duration_minutes = 0,
            session_type = session_type,
            session_task = task
        )

        # Then return it so the UI can tell the user the session has started
        return self.active_session
    
    def stop_session(self):
        """
        Stops the timer, calculates the duration in minutes, and updates the task stats.
        """

        # First check that a session is actually active
        if not self.active_session:
            return None
        
        # Capture the end time
        end_timestamp = time.time()

        # Calculate the difference in seconds
        duration_seconds = end_timestamp - self.start_timestamp

        # Convert to minutes (and force to int)
        self.active_session.duration_minutes = int(duration_seconds / 60)

        # Update the task
        # If working on a specific task, add this time to it's total history.
        if self.current_task:
            self.current_task.total_work_time += self.active_session.duration_minutes

        # Return the session so that main.py can save it to the database
        return self.active_session
    
class AnalyticsEngine:
    """
    Handles the calculations for productivity scores and stats.
    """
    @staticmethod
    def calculate_daily_score(day):
        """
        Calculates a productivity score for a specific day.

        The algorithm:
        1. 10 points for every 1 hour of study.
        2. 50 points for every completed task.
        """
        
        score = 0.0

        # Loop through every task recorded for this day
        for task in day.tasks:
            # 1. Time Bonus (Minutes / 60 * 10 points)
            hours_studied = task.total_work_time / 60.0
            score += (hours_studied * 10.0)

            # 2. Completion Bonus
            # Check if the task is finished
            if task.task_status == 3:  # Status 3 = DONE
                score += 50.0

        return round(score, 1) # Round to 1 decimal place