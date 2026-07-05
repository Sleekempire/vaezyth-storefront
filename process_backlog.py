
import os
import time
import random
from sqlalchemy.orm import Session
from . import models, database, ai_service, email_service
from .database import SessionLocal
from dotenv import load_dotenv

load_dotenv()

def process_backlog():
    db = SessionLocal()
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    # Path to CV
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cv_path = os.path.join(base_dir, "CV Ehiabor Success 2026.docx")
    
    try:
        profile = db.query(models.Profile).first()
        if not profile or not profile.email or not smtp_password:
            print("ERROR: Profile or SMTP_PASSWORD not configured.")
            return

        # Find all 'Not Contacted' recruiters
        backlog = db.query(models.Recruiter).filter(models.Recruiter.status == "Not Contacted").all()
        print(f"Found {len(backlog)} leads in backlog. Starting automated outreach...")

        for rec in backlog:
            # Skip excluded
            if "talentinsightgroup" in rec.company_name.lower():
                rec.status = "Excluded"
                db.commit()
                continue

            try:
                # Faster delay (30-60 seconds)
                delay = random.randint(30, 60)
                print(f"--- Sleeping for {delay}s before emailing {rec.recruiter_name} ({rec.email}) ---", flush=True)
                time.sleep(delay)

                print(f"Generating email for {rec.recruiter_name} at {rec.company_name}...", flush=True)
                email_body = ai_service.generate_cold_email(profile, rec)
                subject = f"Analyst Opportunities - {profile.name}"

                print(f"Attempting to send email to {rec.email}...", flush=True)
                success, error_msg = email_service.send_cv_email(
                    recipient_email=rec.email,
                    subject=subject,
                    body=email_body,
                    cv_path=cv_path,
                    sender_email=profile.email,
                    sender_password=smtp_password
                )

                if success:
                    rec.status = "Sent"
                    log = models.EmailLog(
                        recruiter_id=rec.id,
                        subject=subject,
                        body=email_body
                    )
                    db.add(log)
                    db.commit()
                    print(f"SUCCESS: Sent to {rec.email}")
                else:
                    print(f"FAILED: {error_msg}")
                    # If it's a "Daily Limit" error, we should stop
                    if "limit" in error_msg.lower() or "quotalimit" in error_msg.lower():
                        print("CRITICAL: Detected daily limit reaching again. Stopping backlog process.")
                        break

            except Exception as e:
                print(f"Error processing {rec.email}: {e}")
                db.rollback()

    except Exception as e:
        print(f"Backlog process crashed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    process_backlog()
