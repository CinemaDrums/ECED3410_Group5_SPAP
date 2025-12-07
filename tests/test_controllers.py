import pytest # to run the test do 'python -m pytest' in terminal
import time
from src.controllers import SessionController, AnalyticsEngine
from src.models import Type, Day, Task, Status
from datetime import datetime

def test_session_timer():
    """Tests that the session timer correctly records time."""
    controller = SessionController()

    # start a study session
    session = controller.start_session(session_type = Type.STUDY)
    assert session.start_time is not None
    assert session.duration_minutes == 0

    # simulate 60 seconds passing
    controller.start_timestamp -= 60

    session = controller.stop_session()

    # check if it calculatred duration correctly (should be 1 minute)
    assert session.duration_minutes == 1

def test_analytics_score():
    """Tests if the analytics engine calculates productivity score correctly."""
    # create a dummy task that is DONE (Status 3) and took 60 minutes to complete
    task1 = Task(
        task_id = 1,
        title = "Test",
        date_assigned = datetime.now(),
        due_date = datetime.now(),
        weighted_percent = 0.0,
        points_earned = 0.0,
        task_status = 3, # DONE
        total_work_time = 60.0 # 1 hour
    )

    # create a dummy 'Day' view
    day_view = Day(
        date = datetime.now(),
        productivity_score = 0.0,
        tasks = [task1]
    )

    # calculate productivity score
    score = AnalyticsEngine.calculate_daily_score(day_view)

    # expected score: 10 (time) + 50 (bonus for DONE task) = 60.0
    assert score == 60.0