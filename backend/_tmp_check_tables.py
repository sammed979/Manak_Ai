import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent / "manak_ai.db"
print(f"DB exists: {db_path.exists()}")
if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    rows = cur.fetchall()
    print(f"Total tables: {len(rows)}")
    for (name,) in rows:
        print(" -", name)
    conn.close()
