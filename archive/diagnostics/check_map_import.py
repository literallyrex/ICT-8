import sys
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
try:
    import tkintermapview
    print("tkintermapview imported successfully.")
    print(f"Version: {tkintermapview.__version__}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Unexpected error during import: {e}")
    import traceback
    traceback.print_exc()
