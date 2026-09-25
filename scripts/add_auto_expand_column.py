import sqlite3
from pathlib import Path


DB_PATH = Path("task.db")


def main():

    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH.resolve()}")
        return

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        # Check whether column already exists
        cursor.execute("PRAGMA table_info(tasks)")

        columns = {
            row[1]
            for row in cursor.fetchall()
        }

        if "auto_expand" in columns:
            print(
                "auto_expand column already exists. "
                "No change required."
            )
            return

        # Add the new column
        cursor.execute(
            """
            ALTER TABLE tasks
            ADD COLUMN auto_expand
            BOOLEAN NOT NULL DEFAULT 0
            """
        )

        connection.commit()

        print(
            "auto_expand column added successfully."
        )

        # Verify existing task values
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM tasks
            WHERE auto_expand = 0
            """
        )

        count = cursor.fetchone()[0]

        print(
            f"{count} existing tasks have "
            "auto_expand=False."
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()