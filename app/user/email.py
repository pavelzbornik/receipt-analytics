"""Send reset email."""

from flask import current_app, render_template
from flask_mail import email_dispatched

from app.email import send_email


def log_message(message, current_app):
    """Log message."""
    current_app.logger.info(
        f"Email sent: {message.subject} to {', '.join(message.recipients)}"
    )


def send_password_reset_email(user):
    """Send password reset email."""
    token = user.get_reset_password_token()
    send_email(
        "[Receipt Analytics] Reset Your Password",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[user.email],
        text_body=render_template("email/reset_password.txt", user=user, token=token),
        html_body=render_template("email/reset_password.html", user=user, token=token),
        sync=True,
    )
    current_app.logger.info(f"Password reset email sent to {user.email}")
    email_dispatched.connect(log_message)
