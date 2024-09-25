from dataclasses import dataclass
from typing import List, Union

import resend
from django.template.loader import render_to_string


@dataclass
class SendParams:
    def __init__(
        self,
        from_email_address: str,
        to_email_address: Union[str, List[str]],
        subject: str,
        message: str,
    ):
        self.from_address = from_email_address
        self.to_email_address = to_email_address
        self.subject = subject
        self.message = message

    def to_dict(self):
        return {
            "from": self.from_address,
            "to": self.to_email_address,
            "subject": self.subject,
            "html": self.message,
        }


def send_email(
    to_email_address: Union[str, List[str]], subject: str, message: str
):
    params = SendParams(
        from_email_address="developers@stepby.one",
        to_email_address=to_email_address,
        subject=subject,
        message=message,
    )

    email = resend.Emails.send(params.to_dict())
    return email


def send_welcome_email(
    to_email_address: Union[str, List[str]], user_name: str
):
    html_message = render_to_string(
        "welcome_email.html", {"username": user_name}
    )
    send_email(to_email_address, "Welcome to join us", html_message)


def get_welcome_email(user_name):
    html_message = render_to_string(
        "welcome_email.html", {"username": user_name}
    )
    return html_message
