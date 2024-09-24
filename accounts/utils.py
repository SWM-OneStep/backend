from dataclasses import dataclass

import resend
from django.template.loader import render_to_string


@dataclass
class SendParams:
    from_email: str
    to: str
    subject: str
    html: str


def send_email(to_email_address: str, subject: str, message: str):
    params = SendParams(
        from_email="developers@stepby.one",
        to=to_email_address,
        subject=subject,
        html=message,
    )

    email = resend.Emails.send(params)
    return email


def welcome_email(user_name):
    html_message = render_to_string(
        "welcome_email.html", {"username": user_name}
    )
    return html_message
