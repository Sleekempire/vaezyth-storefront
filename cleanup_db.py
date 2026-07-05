import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'outreach.db')
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 1. Identify and delete synthetic recruiters
    # contactX@domain.com, example@email.com, etc.
    # Also anything containing junk extensions that were accidentally saved
    junk_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf', '.css', '.js', '.webp']
    
    print("Deleting synthetic and junk recruiter leads...")
    
    # Simple query for common patterns
    c.execute("DELETE FROM recruiters WHERE email LIKE 'contact%'")
    c.execute("DELETE FROM recruiters WHERE email LIKE 'example%'")
    
    for ext in junk_extensions:
        c.execute("DELETE FROM recruiters WHERE email LIKE ?", (f'%{ext}%',))
    
    # 2. Cleanup corresponding email logs
    # SQLite doesn't always have cascaded deletes enabled by default
    c.execute("""
        DELETE FROM email_logs 
        WHERE recruiter_id NOT IN (SELECT id FROM recruiters)
    """)

    conn.commit()
    
    # Get final counts
    c.execute("SELECT COUNT(*) FROM recruiters")
    r_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM email_logs")
    e_count = c.fetchone()[0]
    
    print(f"Cleanup complete.")
    print(f"Remaining Real Recruiters: {r_count}")
    print(f"Remaining Real Email Logs: {e_count}")

    conn.close()
except Exception as e:
    print(f"Cleanup failed: {e}")
