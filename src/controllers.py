import time
from datetime import datetime
from .models import StudySession, Task, Type

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
    
    @staticmethod
    def calculate_course_grade(course):
        """Calculates weighted average for a course."""
        total_weight = sum(t.weighted_percent for t in course.tasks)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(
            (t.points_earned / 100.0) * t.weighted_percent 
            for t in course.tasks 
            if t.points_earned > 0
        )
        return round((weighted_sum / total_weight) * 100, 2)
    
    # --- MERGE SORT HELPERS ---
    
    @staticmethod
    def _merge_sort_tasks(tasks, score_func):
        """
        Custom implementation of Merge Sort (Divide & Conquer).
        Sorts tasks in DESCENDING order (Highest score first).
        """
        if len(tasks) <= 1:
            return tasks

        # DIVIDE step
        mid = len(tasks) // 2
        left_half = tasks[:mid]
        right_half = tasks[mid:]

        # RECURSIVE calls to sort the halves
        sorted_left = AnalyticsEngine._merge_sort_tasks(left_half, score_func)
        sorted_right = AnalyticsEngine._merge_sort_tasks(right_half, score_func)

        # MERGE step
        return AnalyticsEngine._merge(sorted_left, sorted_right, score_func)

    @staticmethod
    def _merge(left, right, score_func):
        """
        Helper method to merge two sorted lists.
        """
        sorted_list = []
        i = j = 0

        # Compare and merge
        while i < len(left) and j < len(right):
            # We want DESCENDING order, so we check if Left >= Right
            if score_func(left[i]) >= score_func(right[j]):
                sorted_list.append(left[i])
                i += 1
            else:
                sorted_list.append(right[j])
                j += 1

        # Add remaining elements (if any)
        sorted_list.extend(left[i:])
        sorted_list.extend(right[j:])
        
        return sorted_list

    @staticmethod
    def get_smart_recommendation(student):
        """
        Calculates the most critical task to work on right now.

        The algorithm:
        1. Filters out tasks that are already completed.
        2. Calculates a priority score based on weight vs days remaining.
        3. Sorts using a custom Merge Sort implementation (Divide & Conquer).
        4. Returns the highest scoring task.
        """
        
        # 1. Filter out completed tasks
        # We assume Status 3 is DONE
        active_tasks = [t for t in student.tasks if t.task_status != 3]

        if not active_tasks:
            return None, "No active tasks found! You are free."

        today = datetime.now()

        def urgency_heuristic(task):
            # Data Cleaning: Handle missing or "TBD" dates
            if not task.due_date or str(task.due_date).upper() == "TBD":
                return -1

            # Parse the date logic
            try:
                if isinstance(task.due_date, str):
                    due = datetime.strptime(task.due_date, "%Y-%m-%d")
                else:
                    due = task.due_date
            except ValueError:
                return -1 

            # Calculate days remaining
            delta = (due - today).days
            
            # Mathematical Safety: Prevent division by zero
            # If due today (0) or overdue (negative), set strict factor to 0.1
            days_left = max(delta, 0.1)

            # 2. Calculate Score (Weight / Time)
            return task.weighted_percent / days_left

        # 3. Sort tasks using our custom Merge Sort
        # Replaced the built-in .sort() with our own algorithm for the Bonus
        sorted_tasks = AnalyticsEngine._merge_sort_tasks(active_tasks, urgency_heuristic)

        # Select the winner
        top_task = sorted_tasks[0]
        score = urgency_heuristic(top_task)
        
        # Calculate days for display (safely)
        try:
             due_dt = datetime.strptime(top_task.due_date, '%Y-%m-%d')
             days_remaining = (due_dt - today).days
        except:
             days_remaining = "?"

        return top_task, f"Priority Score: {score:.1f} (Weight: {top_task.weighted_percent}% / Days Left: {days_remaining})"