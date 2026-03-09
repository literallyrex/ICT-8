import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import initialize_db


def migrate():
    # initialize_db() now creates the social tables if they do not exist yet.
    initialize_db()
    print("Migration v11 complete. Friends and chat tables are ready.")


if __name__ == "__main__":
    migrate()
