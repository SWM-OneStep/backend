import resend
from django.template.loader import render_to_string


def send_email(send_email, subject, message):
    params: resend.Emails.SendParams = {
        "from": "Acme <onboarding@resend.dev>",
        "to": ["szonestep@gmail.com"],
        "subject": "Work Report",
        "html": "<strong>it works!</strong>",
    }

    email = resend.Emails.send(params)
    return email


def welcome_email(user_name):
    html_message = render_to_string(
        "welcome_email.html", {"user_name": user_name}
    )
    return html_message
