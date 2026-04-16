import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database.connection import db_manager

def wipe():
    print("Initializing...")
    db_manager.initialize()
    conn = db_manager.get_connection()
    try:
        cur = conn.cursor()
        print("Executing delete...")
        cur.execute("DELETE FROM audit_log;")
        cur.execute("DELETE FROM blockchain;")
        cur.execute("UPDATE voters SET has_voted=FALSE, voted_at=NULL;")
        conn.commit()
        print("Database wiped via app pool.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        db_manager.return_connection(conn)

if __name__ == '__main__':
    wipe()
