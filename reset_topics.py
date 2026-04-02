import sqlite3
from pathlib import Path

def reset_all_topics():
    base_dir = Path("store/community_books")
    count = 0
    for db_file in base_dir.rglob("metadata.db"):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Check if topics table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='topics'")
            if cursor.fetchone():
                cursor.execute("DELETE FROM topics")
                conn.commit()
                count += 1
                print(f"Cleared topics for: {db_file.parent.name}")
            
            conn.close()
        except Exception as e:
            print(f"Error processing {db_file}: {e}")
            
    print(f"\nSuccessfully reset topics for {count} books.")

if __name__ == "__main__":
    reset_all_topics()
