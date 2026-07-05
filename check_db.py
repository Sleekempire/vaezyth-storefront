from . import database, models

db = next(database.get_db())
recruiters = db.query(models.Recruiter).all()
logs = db.query(models.EmailLog).all()

print(f"Total Recruiters: {len(recruiters)}")
for r in recruiters:
    print(f"- {r.recruiter_name} ({r.email}): status={r.status}")

print(f"\nTotal Email Logs: {len(logs)}")
for l in logs:
    print(f"- To Recruiter ID {l.recruiter_id}: {l.subject}")

db.close()
