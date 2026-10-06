import sqlite3
import os
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "trustguard.db")
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # makes case_id links enforced
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Case_Table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            image_path TEXT,
            claimed_location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            module_name TEXT NOT NULL,
            findings_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (case_id) REFERENCES Case_Table (id)
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")
if __name__ == "__main__":
    init_db()
