import os
import sys
from datetime import datetime
import time

from src.models import Student, Course, Task, Type, Day, Status
from src.storage import DatabaseHandler
from src.controllers import SessionController, AnalyticsEngine

# initialize the DatabaseHandler globally so all modules can access it
db = DatabaseHandler()

def clear_screen():
    """Clears the terminal screen for a cleaner UI."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Prints a perfectly centered header for the current menu."""
    clear_screen()
    width = len(title) + 4
    print("=" * width)
    print(title.center(width))
    print("=" * width)
    print()

def pause():
    """Waits for the user to press Enter before continuing."""
    input("\nPress Enter to continue...")

def get_status_label(status_int):
    """Converts status integer to text string."""
    if status_int == 1:
        return "TODO"
    if status_int == 2:
        return "IN PROGRESS"
    if status_int == 3:
        return "DONE"
    return "UNKNOWN"

def login_menu():
    """
    Handles user login and registration.
    Returns:
        Student: The authenticated student object.
    """
    while True:
        print_header("Welcome to the Student Productivity Analytics Platform!")
        print("1. Login")
        print("2. Create New Account")
        print("3. Exit")

        choice = input("\nSelect an option (1-3): ").strip()

        if choice == '1':
            # login logic
            email = input("Enter your email: ").strip()
            password = input("Enter your password: ").strip()

            student = db.get_student(email)

            if student and student.check_password(password):
                print(f"\nLogin successful! Welcome back, {email}.")
                time.sleep(1) # brief pause for user experience
                return student
            else:
                print("\nError: Invalid email or password.")
                pause()

        elif choice == '2':
            # registration logic
            print("\n--- Create New Account ---")
            email = input("Enter your email: ").strip()

            # check if user already exists
            if db.get_student(email):
                print("\nError: User with this email already exists.")
                pause()
                continue

            password = input("Enter your password: ").strip()
            student_id = input("Enter your student ID: ").strip()

            # create the new Student object
            new_student = Student(email = email, student_id = student_id, password_hash = "")
            new_student.set_password(password) # this handles the bcrypt hashing

            # save them to the database
            db.add_student(new_student)

            print("\nAccount created successfully! Logging you in...")
            time.sleep(1)
            return new_student
        
        elif choice == '3':
            print("Goodbye!")
            sys.exit() # kils the program immediately

        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

def main_menu(student):
    """
    The main application loop.
    Args:
        student (Student): The currently logged-in user.
    """
    # create a controller for this specific user session
    controller = SessionController()

    while True:
        print_header(f"Dashboard - {student.email}")
        print(f"Stats: {len(student.courses)} Courses | {len(student.tasks)} Tasks | {len(student.study_sessions)} Sessions")
        print("-" * 40)

        print("1. Start Study Session")
        print("2. Add New Task")
        print("3. Update Task Status")
        print("4. View Analytics Report")
        print("5. Add New Course")
        print("6. Save & Logout")

        choice = input("\nSelect an option (1-6): ").strip()

        if choice == '1':
            # start/stop timer logic
            print("\n--- Start Study Session ---")
            input("Press Enter to START the study session...")

            # start the logic
            session = controller.start_session(task = None) # default to no task
            start_time_str = time.strftime("%H:%M:%S", time.localtime(session.start_time))
            print(f"Timer Started at {start_time_str}! Good luck studying!")

            input("Press Enter to STOP the study session...")

            # stop the logic
            session = controller.stop_session()

            # save the results
            student.add_study_session(session)
            db.save_data()

            print(f"\nStudy Session Saved! You studied for {session.duration_minutes} minutes.")
            pause()

        elif choice == '2':
            # add new task logic
            print("\n--- Add New Task ---")
            title = input("Enter task title: ").strip()

            # ask the user for the due date
            due_date_input = input("Enter due date (YYYY-MM-DD) or leave blank for none: ").strip()

            # use what they typed, or default to "TBD" if blank
            final_due_date = due_date_input if due_date_input else "TBD"

            # simple ID generation
            new_task_id = len(student.tasks) + 1

            # createt Task using the model
            new_task = Task(
                task_id = new_task_id,
                title = title,
                date_assigned = str(datetime.now().date()),
                due_date = final_due_date,
                weighted_percent = 0.0,
                points_earned = 0.0,
                total_work_time = 0.0,
                task_status = Status.TODO.value
            )

            student.add_task(new_task)
            db.save_data()
            print("Task added successfully!")
            pause()

        elif choice == '3':
            # update task status logic
            print("\n--- Update Task Status ---")

            if not student.tasks:
                print("No tasks found.")
            else:
                # list all tasks
                print(f"{'ID':<5} {'Status':<15} {'Title'}")
                print("-" * 40)
                for t in student.tasks:
                    status_str = get_status_label(t.task_status)
                    print(f"{t.task_id:<5} {status_str:<15} {t.title}")

                    t_id = input("\nEnter the Task ID to update: ").strip()

                    # find the task
                    found_task = None
                    for t in student.tasks:
                        if str(t.task_id) == t_id:
                            found_task = t
                            break

                    if found_task:
                        print(f"\nUpdating '{found_task.title}'")
                        print("1. TODO")
                        print("2. IN PROGRESS")
                        print("3. DONE (Earn 50 points!)")
                        new_status = input("Select new status (1-3): ").strip()

                        if new_status in ['1', '2', '3']:
                            found_task.task_status = int(new_status)
                            db.save_data()
                            print("Status updated!")
                        else:
                            print("Invalid status selected.")
                    else:
                        print("Task ID not found.")
            pause()

        elif choice == '4':
            # analytics report logic
            print("\n--- Productivity Analytics Report ---")

            today_view = Day(date = str(datetime.now().date()), tasks = student.tasks)
            score = AnalyticsEngine.calculate_daily_score(today_view)

            print(f"Total Tasks: {len(student.tasks)}")
            print(f"Total Study Sessions: {len(student.study_sessions)}")
            print("-" * 20)
            print(f"Daily Productivity Score: {score} points")
            print("-" * 20)

            if score > 100:
                print("Amazing! You are crushing it today!")

            elif score > 50:
                print("Good job! Keep up the work.")
            else:
                print("Time to get to work! Finish a task for 50 points!")
            pause()

        elif choice == '5':
            # add new course logic
            print("\n--- Add New Course ---")
            c_name = input("Enter course code: ")
            new_course = Course(course_id = c_name)
            student.add_course(new_course)
            db.save_data()
            print(f"Course '{c_name}' added successfully!")
            pause()

        elif choice == '6':
            # save & logout logic
            db.save_data()
            print("Data saved! Logging out...")
            time.sleep(1)
            break
        
        else:
            print("Invalid choice.")
            time.sleep(0.5)

# program entry point
if __name__ == "__main__":
    try:
        current_user = login_menu()
        if current_user:
            main_menu(current_user)
    except KeyboardInterrupt:
        print("\n\nForce closing the application. Goodbye!")
        sys.exit()