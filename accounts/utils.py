import resend
from django.template.loader import render_to_string


def send_email(to_email_address, subject, message):
    params: resend.Emails.SendParams = {
        "from": "Acme <onboarding@resend.dev>",
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


def render_to_string_html(template_name):
    return render_to_string(template_name)
