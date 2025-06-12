import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

message = Mail(
    from_email='nhafairi1@gmail.com',
    to_emails='youremail@gmail.com',
    subject='Test Email from SendGrid',
    html_content='<strong>This is a test email from your app</strong>'
)

try:
    sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(f"✅ Email sent. Status code: {response.status_code}")
except Exception as e:
    print("❌ Email failed:", e)
