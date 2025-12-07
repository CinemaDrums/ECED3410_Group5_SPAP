import os
import sys
import re
from datetime import datetime
import time

from .models import Student, Course, Task, Type, Day, Status
from .storage import DatabaseHandler
from .controllers import SessionController, AnalyticsEngine

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

def confirm_action(message):
    """
    Asks the user to confirm a destructive action.
    Returns True if confirmed, False otherwise.
    """
    response = input(f"\n{message} (yes/no): ").strip().lower()
    return response in ['yes', 'y']

def validate_date(date_string):
    """
    Validates if a date string is in YYYY-MM-DD format.
    Returns (is_valid, error_message)
    """
    if not date_string or date_string.upper() == "TBD":
        return True, None
    
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True, None
    except ValueError:
        return False, "Invalid date format. Please use YYYY-MM-DD (e.g., 2025-12-15)"

def validate_percentage(value_string):
    """
    Validates if a string is a valid percentage (0-100).
    Returns (is_valid, float_value, error_message)
    """
    try:
        value = float(value_string)
        if 0 <= value <= 100:
            return True, value, None
        else:
            return False, 0.0, "Percentage must be between 0 and 100"
    except ValueError:
        return False, 0.0, "Please enter a valid number"

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
        print("\nTip: Use option 2 if you're a first-time user")

        choice = input("\nSelect an option (1-3): ").strip()

        if choice == '1':
            # login logic
            email = input("Enter your email: ").strip()

            if not email:
                print("\nError: Email cannot be empty. Please try again.")
                pause()
                continue
            
            password = input("Enter your password: ").strip()
            
            if not password:
                print("\nError: Password cannot be empty. Please try again.")
                pause()
                continue

            student = db.get_student(email)

            if student and student.check_password(password):
                print(f"\n✓ Login successful! Welcome back, {email}.")
                time.sleep(1) # brief pause for user experience
                return student
            else:
                print("\n✗ Error: Invalid email or password.")
                print("Please check your credentials and try again.")
                pause()

        elif choice == '2':
            # registration logic
            print("\n--- Create New Account ---")
            print("Please provide the following information:\n")
            new_email = input("Enter your email: ").strip()

            if not new_email:
                print("\n✗ Error: Email cannot be empty.")
                pause()
                continue
        
            # check if user already exists
            if db.get_student(new_email):
                print("\n✗ Error: User with this email already exists.")
                print("Please use option 1 to login or try a different email.")
                pause()
                continue

            new_password = input("Enter your password (min 8 characters): ").strip()
            new_student_id = input("Enter your 6-digit student ID: ").strip()

            # check if email follows email pattern
            pattern = r'[0-9]{6}' # exactly 6 digits
            if not re.fullmatch(pattern, new_student_id):
                print("\n✗ Error: Student ID must be exactly 6 digits (e.g., 123456).")
                pause()
                continue

            # create the new Student object
            new_student = Student(email = new_email, student_id = new_student_id, password_hash = "")
            new_student.set_password(new_password) # this handles the bcrypt hashing

            # save them to the database
            db.add_student(new_student)

            print("\nAccount created successfully! Logging you in...")
            time.sleep(1)
            return new_student
        
        elif choice == '3':
            print("Thank you for using the SPAP. Goodbye!")
            sys.exit() # kils the program immediately

        else:
            print("✗ Invalid choice. Please enter 1, 2, or 3.")
            time.sleep(1)

def validate_password(password):
    """Checks if password meets minimum security requirements."""
    if len(password) < 8:
        return False, "✗ Error: Password must be at least 8 characters"
    if not any(c.isdigit() for c in password):
        return False, "✗ Error: Password must contain at least one number"
    return True, "Valid"

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
        print(f"📊 Stats: {len(student.courses)} Courses | {len(student.tasks)} Tasks | {len(student.study_sessions)} Sessions")
        print("-" * 60)
        print("\n📚 MAIN MENU")
        print("─" * 60)  

        print("1. Start Study Session")
        print("2. Add New Task")
        print("3. Update Task Status")
        print("4. Edit Task Details")
        print("5. Delete Task")
        print("6. View Analytics Report")
        print("7. Add New Course")
        print("8. Save & Logout")
        print("\nTip: Choose option 6 to see your productivity score!")

        choice = input("\nSelect an option (1-8): ").strip()

        if choice == '1':
            # start/stop timer logic
            print("\n--- Start Study Session ---")
            print("Press Enter when you're ready to begin tracking your study time.")
            input("Press Enter to START the study session...")

            # start the logic
            session = controller.start_session(task = None) # default to no task
            start_time_str = time.strftime("%H:%M:%S", time.localtime(session.start_time))
            print(f"⏱️ Timer Started at {start_time_str}!")
            print("Focus on your work. Press Enter when you're done to stop the timer.")

            input("Press Enter to STOP the study session...")

            # stop the logic
            session = controller.stop_session()

            # save the results
            student.add_study_session(session)
            db.save_data()

            print(f"\n✓ Study Session Saved!")
            print(f"You studied for {session.duration_minutes} minute(s).")
            print(f"Keep up the great work! 🎉")
            pause()

        elif choice == '2':
            # add new task logic
            print("\n--- Add New Task ---")
            print("Fill in the task details below:\n")

            title = input("Enter task title: ").strip()

            if not title:
               print("\n✗ Error: Task title cannot be empty.")
               pause()
               continue

            # ask user for date the task was assigned
            date_assigned_input = input("Date assigned (YYYY-MM-DD) or press Enter to skip: ").strip()

            if date_assigned_input:
                is_valid, error_msg = validate_date(date_assigned_input)
                if not is_valid:
                    print(f"\n✗ Error: {error_msg}")
                    pause()
                    continue

            # use what they typed, or default to "TBD" if blank
            final_date_assigned = date_assigned_input if date_assigned_input else "TBD"

            # ask the user for the due date
            due_date_input = input("Due date (YYYY-MM-DD) or press Enter to skip: ").strip()

            if due_date_input:
                is_valid, error_msg = validate_date(due_date_input)
                if not is_valid:
                    print(f"\n✗ Error: {error_msg}")
                    pause()
                    continue

            # use what they typed, or default to "TBD" if blank
            final_due_date = due_date_input if due_date_input else "TBD"

            # ask user for assignments worth as a percentage of the courses grade
            task_percent_input = input("Worth as % of course grade (0-100): ").strip()

            # vailidate percentage input
            is_valid, task_percent, error_msg = validate_percentage(task_percent_input)
            if not is_valid:
                print(f"\n✗ Error: {error_msg}")
                pause()
                continue

            # simple ID generation
            new_task_id = len(student.tasks) + 1

            # createt Task using the model
            new_task = Task(
                task_id = new_task_id,
                title = title,
                date_assigned = final_date_assigned,
                due_date = final_due_date,
                weighted_percent = task_percent,
                points_earned = 0.0,
                total_work_time = 0.0,
                task_status = Status.TODO.value
            )

            student.add_task(new_task)
            db.save_data()
            print(f"\n✓ Task '{title}' added successfully!")
            pause()

        elif choice == '3':
            # update task status logic
            print("\n--- Update Task Status ---")

            if not student.tasks:
                print("No tasks found. Add a task first using option 2.")
                pause()
                continue

            else:
                # list all tasks
                print(f"{'ID':<5} {'Status':<15} {'Title'}")
                print("-" * 60)
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
                        print(f"\nUpdating status for: '{found_task.title}'")
                        print("1. TODO")
                        print("2. IN PROGRESS")
                        print("3. DONE (Earn 50 productivity points!)")
                        new_status = input("Select new status (1-3): ").strip()

                        if new_status in ['1', '2', '3']:
                            old_status = found_task.task_status
                            found_task.task_status = int(new_status)
                            db.save_data()
                            print(f"\n✓ Status updated from '{get_status_label(old_status)}' to '{get_status_label(int(new_status))}'")
                            if new_status == '3':
                                print("🎉 Congratulations on completing your task!")
                        else:
                            print("\n✗ Invalid status selection. No changes made.")
                    else:
                        print(f"\n✗ Error: Task ID '{t_id}' not found.")
                    pause()

        elif choice == '4':
            # edit task details logic
            print("\n--- Edit Task Details ---")

            if not student.tasks:
                print("No tasks found. Add a task first using option 2.")
                pause()
                continue

            # list all tasks
            print(f"\n{'ID':<5} {'Title':<30} {'Due Date'}")
            print("─" * 60)
            for t in student.tasks:
                print(f"{t.task_id:<5} {t.title:<30} {t.due_date}")

            t_id = input("\nEnter the Task ID to edit (or 0 to cancel): ").strip()
            
            if t_id == '0':
                continue

            # find the task
            found_task = None
            for t in student.tasks:
                if str(t.task_id) == t_id:
                    found_task = t
                    break

            if not found_task:
                print(f"\n✗ Error: Task ID '{t_id}' not found.")
                pause()
                continue

            print(f"\nEditing: '{found_task.title}'")
            print("─" * 40)
            print("Leave any field blank to keep the current value.\n")

            # Edit title
            new_title = input(f"New title (current: {found_task.title}): ").strip()
            if new_title:
                found_task.title = new_title

            # Edit due date
            new_due_date = input(f"New due date (current: {found_task.due_date}): ").strip()
            if new_due_date:
                is_valid, error_msg = validate_date(new_due_date)
                if is_valid:
                    found_task.due_date = new_due_date
                else:
                    print(f"⚠️  Warning: {error_msg}. Keeping original due date.")

            # Edit weight percentage
            new_percent = input(f"New weight % (current: {found_task.weighted_percent}): ").strip()
            if new_percent:
                is_valid, percent_value, error_msg = validate_percentage(new_percent)
                if is_valid:
                    found_task.weighted_percent = percent_value
                else:
                    print(f"⚠️  Warning: {error_msg}. Keeping original weight.")

            # Edit points earned
            new_points = input(f"Points earned (current: {found_task.points_earned}): ").strip()
            if new_points:
                is_valid, points_value, error_msg = validate_percentage(new_points)
                if is_valid:
                    found_task.points_earned = points_value
                else:
                    print(f"⚠️  Warning: {error_msg}. Keeping original points.")

            db.save_data()
            print("\n✓ Task updated successfully!")
            pause()


        elif choice == '5':
            # delete task logic
            print("\n--- Delete Task ---")

            if not student.tasks:
                print("No tasks found. Nothing to delete.")
                pause()
                continue

            # list all tasks
            print(f"\n{'ID':<5} {'Status':<15} {'Title'}")
            print("─" * 60)
            for t in student.tasks:
                status_str = get_status_label(t.task_status)
                print(f"{t.task_id:<5} {status_str:<15} {t.title}")

            t_id = input("\nEnter the Task ID to delete (or 0 to cancel): ").strip()
            
            if t_id == '0':
                continue

            # find the task
            found_task = None
            task_index = None
            for i, t in enumerate(student.tasks):
                if str(t.task_id) == t_id:
                    found_task = t
                    task_index = i
                    break

            if found_task:
                # Confirmation prompt for destructive action
                print(f"\n⚠️  WARNING: You are about to delete:")
                print(f"   Task: '{found_task.title}'")
                print(f"   Status: {get_status_label(found_task.task_status)}")
                print(f"   Due Date: {found_task.due_date}")
                print(f"\n   This action CANNOT be undone!")
                
                if confirm_action("Are you sure you want to delete this task?"):
                    task_title = found_task.title
                    student.tasks.pop(task_index)
                    db.save_data()
                    print(f"\n✓ Task '{task_title}' has been deleted.")
                else:
                    print("\n✓ Deletion cancelled. Task was not deleted.")
            else:
                print(f"\n✗ Error: Task ID '{t_id}' not found.")
            
            pause()

        elif choice == '6':
            # analytics report logic
            print("\n--- Productivity Analytics Report ---")
            print("═" * 60)

            today_view = Day(date=str(datetime.now().date()), tasks=student.tasks)
            score = AnalyticsEngine.calculate_daily_score(today_view)

            total_study_minutes = sum(s.duration_minutes for s in student.study_sessions)
            completed_tasks = sum(1 for t in student.tasks if t.task_status == 3)
            in_progress_tasks = sum(1 for t in student.tasks if t.task_status == 2)
            todo_tasks = sum(1 for t in student.tasks if t.task_status == 1)

            print(f"\n📊 Overview:")
            print(f"   Total Tasks: {len(student.tasks)}")
            print(f"   - Completed: {completed_tasks}")
            print(f"   - In Progress: {in_progress_tasks}")
            print(f"   - To Do: {todo_tasks}")
            print(f"\n   Total Study Sessions: {len(student.study_sessions)}")
            print(f"   Total Study Time: {total_study_minutes} minutes ({total_study_minutes / 60:.1f} hours)")
            
            print("\n" + "─" * 60)
            print(f"🏆 Daily Productivity Score: {score} points")
            print("─" * 60)

            if score >= 100:
                print("\n🌟 AMAZING! You are crushing it today!")
                print("   Keep up this incredible momentum!")
            elif score >= 50:
                print("\n👍 GOOD JOB! You're making solid progress.")
                print("   Complete another task to boost your score!")
            else:
                print("\n💪 TIME TO GET TO WORK!")
                print("   Finish a task to earn 50 points instantly!")
            
            pause()

        elif choice == '7':
            # add new course logic
            print("\n--- Add New Course ---")
            print("Enter the course code (e.g., ECED3410, MATH2000):\n")
            
            c_name = input("Course code: ").strip()
            
            if not c_name:
                print("\n✗ Error: Course code cannot be empty.")
                pause()
                continue
            
            # Check for duplicate courses
            if any(course.course_id == c_name for course in student.courses):
                print(f"\n✗ Error: Course '{c_name}' already exists.")
                pause()
                continue
                
            new_course = Course(course_id=c_name)
            student.add_course(new_course)
            db.save_data()
            
            print(f"\n✓ Course '{c_name}' added successfully!")
            pause()

        elif choice == '8':
            # save & logout logic
            print("\nSaving your data...")
            db.save_data()
            print("✓ All changes saved successfully!")
            print(f"\nThank you for using SPAP, {student.email}!")
            print("See you next time! 👋")
            time.sleep(2)
            break
        
        else:
            print("\n✗ Invalid choice. Please enter a number between 1 and 8.")
            time.sleep(1)

# program entry point
if __name__ == "__main__":
    try:
        current_user = login_menu()
        if current_user:
            main_menu(current_user)
    except KeyboardInterrupt:
        print("\n\n⚠️  Application interrupted by user.")
        print("Goodbye!")
        sys.exit()
    except Exception as e:
        print(f"\n\n✗ An unexpected error occurred: {e}")
        print("Please report this issue if it persists.")
        sys.exit(1)