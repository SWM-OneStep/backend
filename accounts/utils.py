import resend


def send_email(send_email, subject, message):
    params: resend.Emails.SendParams = {
        "from": "Acme <onboarding@resend.dev>",
        "to": ["szonestep@gmail.com"],
        "subject": "Work Report",
        "html": "<strong>it works!</strong>",
    }

    email = resend.Emails.send(params)
    return email
