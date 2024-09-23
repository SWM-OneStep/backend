import resend
from django.template.loader import render_to_string


def send_email(to_email_address, subject, message):
    params: resend.Emails.SendParams = {
        "from": "developers@stepby.one",
        "to": to_email_address,
        "subject": subject,
        "html": message,
    }

    email = resend.Emails.send(params)
    return email


def welcome_email(user_name):
    html_message = render_to_string(
        "welcome_email.html", {"username": user_name}
    )
    return html_message
