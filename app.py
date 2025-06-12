from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, redirect
import csv
from datetime import datetime
import os

# Email
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# SMS
from twilio.rest import Client

# Stripe
import stripe

app = Flask(__name__)
# Ensure the bookings CSV is always written relative to this file so
# the app works no matter where it is executed from.
BOOKINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "bookings.csv")

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    data = {
        'name': request.form['name'],
        'email': request.form['email'],
        'address': request.form['address'],
        'date': request.form['date'],
        'time': request.form['time'],
        'bedrooms': request.form['bedrooms'],
        'bathrooms': request.form['bathrooms'],
        'notes': request.form.get('notes', ''),
        'timestamp': datetime.now().isoformat()
    }

    with open(BOOKINGS_FILE, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(data)

    # Send email confirmation
    message = Mail(
        from_email='nhafairi1@gmail.com',  # Must match your verified sender
        to_emails=data['email'],
        subject='Your Airbnb Cleaning is Booked!',
        html_content=f"<strong>Thanks {data['name']}! We'll see you at {data['address']} on {data['date']} at {data['time']}.</strong>"
)
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print("✅ Email sent:", response.status_code)
    except Exception as e:
        print("❌ Email failed:", e)

    # # Send SMS confirmation (to a test number)
    # try:
    #     client = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    #     client.messages.create(
    #         body=f"✅ Booking confirmed for {data['date']} at {data['time']} — {data['address']}",
    #         from_=os.getenv('TWILIO_PHONE'),
    #         to='+1XXXXXXXXXX'  # Replace with actual number or dynamic input
    #     )
    # except Exception as e:
    #     print("SMS failed:", e)

    return redirect('/thankyou')

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        base_url = os.getenv('BASE_URL') or request.url_root
        if base_url.endswith('/'):
            base_url = base_url[:-1]

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': 8000,
                    'product_data': {
                        'name': 'Airbnb Cleaning - Standard',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{base_url}/thankyou",
            cancel_url=f"{base_url}/",
        )
        return redirect(session.url, code=303)
    except Exception as e:
        print("Stripe session creation failed:", e)
        return redirect('/')

@app.route('/thankyou')
def thank_you():
    return render_template("thank_you.html")


if __name__ == '__main__':
    app.run(debug=True)
