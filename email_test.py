from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create the email
message = Mail(
    from_email='nhafairi1@gmail.com',   # ✅ must match a verified sender in SendGrid
    to_emails='nhafairi1@gmail.com',     # 🔄 where you want the test email sent
    subject='Test Email from Airbnb Cleaner App',
    html_content='<strong>This is a test email from your Airbnb cleaner app!</strong>'
)

# Send the email
try:
    sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))  # ✅ .env must include correct API key
    response = sg.send(message)
    print("✅ Email sent:", response.status_code)
except Exception as e:
    print("❌ Email failed:", str(e))
