import os
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

sys.modules['dotenv'] = ModuleType('dotenv')
sys.modules['dotenv'].load_dotenv = lambda: None
sys.modules['sendgrid'] = ModuleType('sendgrid')
sys.modules['sendgrid'].SendGridAPIClient = object
sys.modules['sendgrid.helpers'] = ModuleType('sendgrid.helpers')
sys.modules['sendgrid.helpers.mail'] = ModuleType('sendgrid.helpers.mail')
sys.modules['sendgrid.helpers.mail'].Mail = object
sys.modules['twilio'] = ModuleType('twilio')
sys.modules['twilio.rest'] = ModuleType('twilio.rest')
sys.modules['twilio.rest'].Client = object
sys.modules['stripe'] = ModuleType('stripe')
sys.modules['stripe'].checkout = SimpleNamespace(Session=SimpleNamespace(create=None))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app


def create_client():
    app.app.config['TESTING'] = True
    return app.app.test_client()


class DummySession:
    url = 'https://stripe.test/session'


@patch('app.stripe.checkout.Session.create')
def test_create_checkout_session_env_var(mock_create):
    client = create_client()
    os.environ['BASE_URL'] = 'https://example.com'

    def fake_create(**kwargs):
        assert kwargs['success_url'] == 'https://example.com/thankyou'
        assert kwargs['cancel_url'] == 'https://example.com/'
        return DummySession()

    mock_create.side_effect = fake_create

    response = client.post('/create-checkout-session')
    assert response.status_code == 303
    assert response.headers['Location'] == DummySession.url
    del os.environ['BASE_URL']


@patch('app.stripe.checkout.Session.create')
def test_create_checkout_session_request_root(mock_create):
    client = create_client()

    def fake_create(**kwargs):
        assert kwargs['success_url'] == 'http://localhost/thankyou'
        assert kwargs['cancel_url'] == 'http://localhost/'
        return DummySession()

    mock_create.side_effect = fake_create

    response = client.post('/create-checkout-session')
    assert response.status_code == 303
    assert response.headers['Location'] == DummySession.url
