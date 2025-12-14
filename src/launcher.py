import sys
import os

# Ensures the executable can find the 'src' folder
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Import using the full package name so relative imports (from .models) work
    from src.main import login_menu, main_menu
except ImportError as e:
    print("CRITICAL ERROR: Could not import project modules.")
    print(f"Details: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

if __name__ == "__main__":
    try:
        current_user = login_menu()
        if current_user:
            main_menu(current_user)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        input("Press Enter to close...")