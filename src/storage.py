import json
import os
from models import Task, StudySession, Student, Course

# Storing the database in a separate folder so it doesn't clutter the root directory.
DATA_FILE = "data/database.json"

class DatabaseHandler:
    """
    Handles all interactions with the JSON storage file.
    Follows the 'Singleton' design pattern to make sure only one instance of this is used.
    Ensures we aren't overwriting data from multiple places at once.
    """
    def __init__(self):
        # We hold the list of students in memory while the program runs.
        self.students = []
        self.load_data()

    def load_data(self):
        """
        Loads raw JSON from disk and converts it back into actual Python objects (Students, Tasks, etc).
        
        We need this because JSON is just text, so it doesn't know what a 'Student' is.
        So we have to manually rebuild the objects everytime the program starts.
        """

        # Create the 'data' folder if its missing so we don't get errors.
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

        # If the file doesn't exist yet, create an empty one.
        if not os.path.isfile(DATA_FILE):
            self.save_data()  # This will create an empty file.
            return
        
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.students = []

                # Loop through the raw dictionaries in the JSON file and create actual objects for each one.
                for s_data in data.get("students", []):
                    new_student = Student(
                        email=s_data['email'],
                        password_hash=s_data.get('password_hash', ""), # Using .get() to avoid crashing if a field is missing in the JSON.
                        student_id=s_data.get('student_id', ""),
                    )

                    # The student has a list of tasks, so we need to rebuild those too.
                    for t in s_data.get('tasks', []):
                        new_student.tasks.append(Task(**t)) # '**t' is a shortcut that unpacks the dictionary into arguments.

                    # Same thing for study sessions.
                    for ss in s_data.get('study_sessions', []):
                        new_student.study_sessions.append(StudySession(**ss))

                    # Add the fully reconstructed student to the list.
                    self.students.append(new_student)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            # If the file is corrupted (if user edited it manually or something), we catch the error instead of crashing.
            print(f"Warning: Database corrupted or mising ({e}). Starting with empty data.")
            self.students = []

    def save_data(self):
        """
        Serializes all the Python objects into simple dictionaries so they can be written to the JSON file.
        """
        data = {
            "students": [s.to_dict() for s in self.students]  # Calling .to_dict() on every student because JSON can't save objects directly.
        }

        # Write to the file with indent=4 for better readability if you open it in Notepad or something like that.
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # Helper methods for the Controller
    
    def add_student(self, student):
        """
        Adds a new student and immediately saves to disk (Autosave).
        """
        self.students.append(student)
        self.save_data()

    def get_student(self, email):
        """
        Finds a student by email. Returns None if not found.
        """
        for s in self.students:
            if s.email == email:
                return s
        return None