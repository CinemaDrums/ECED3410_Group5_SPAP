# Student Productivity Analytics Platform (SPAP)

## Project Structure
- `src/` — Source code (MVC architecture)
- `tests/` — Automated unit tests
- `data/` — JSON storage (Database)
- `docs/` — Project documentation
- `.github/` — CI/CD workflow configurations
- `launcher.py` — Entry point script

## Demo Login Credentials
To test the application with pre-loaded data (Tasks, Courses, etc):
* **Email:** email@dal.ca
* **Password:** 12345678

## How to Run
### Requirements:
Ensure dependencies are installed:
`pip install -r requirements.txt`

### Option 1: Run directly in terminal
Navigate to the project root directory and run:
`python launcher.py`

### Option 2: Build the executable file
1. Install PyInstaller:
`pip install pyinstaller`
2. Build the file
`python -m PyInstaller --name SPAP_Tool --onefile launcher.py`
3. Move the generated `.exe` file from the `dist/` folder to the root folder (next to the `data/` folder) before running it, or it will not be able to load the database.