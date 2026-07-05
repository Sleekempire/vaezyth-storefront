import os
import smtplib
from email.message import EmailMessage

def send_deal_email(recipient_email, subject, body, sender_email, sender_password, unsubscribe_url):
    """
    Sends a B2C deals email with a legal unsubscribe link using SMTP.
    """
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # Append unsubscribe footer
        footer = f"\n\n---\nYou are receiving this because you signed up for Summer Cooling Deals alerts.\nTo unsubscribe, click here: {unsubscribe_url}"
        full_body = body + footer
        
        msg.set_content(full_body, charset='utf-8')

        # Connect to Gmail SMTP server with 30s timeout
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
            
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)
