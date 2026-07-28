from django.core import mail

from notifications.tasks import send_welcome_email


def test_send_welcome_email_sends_one_email():
    result = send_welcome_email.delay("alice@example.com", "alice")

    assert result.successful()
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["alice@example.com"]
    assert "Welcome" in mail.outbox[0].subject
    assert "alice" in mail.outbox[0].body


def test_send_welcome_email_returns_confirmation_string():
    result = send_welcome_email.delay("bob@example.com", "bob")

    assert result.result == "welcome email sent to bob@example.com"
