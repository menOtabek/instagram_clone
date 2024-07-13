import re
import threading
from twilio.rest import Client

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
from decouple import config

email_regex = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
phone_regex = re.compile(r"(^\+998([- ])?(90|91|93|94|95|98|99|33|97|71)([- ])?(\d{3})([- ])?(\d{2})([- ])?(\d{2})$)")
username_regex = re.compile(r"\b[A-Za-z0-9._-]{3,}\b")


def check_email_or_phone(email_or_phone):
    if re.fullmatch(email_regex, email_or_phone):
        email_or_phone = "email"

    elif re.fullmatch(phone_regex, email_or_phone):
        email_or_phone = "phone"

    else:
        raise ValidationError("Email or phone is not valid")
    return email_or_phone


def check_user_type(user_input):
    if re.fullmatch(username_regex, user_input):
        user_input = "username"
    elif re.fullmatch(phone_regex, user_input):
        user_input = "phone"
    elif re.fullmatch(email_regex, user_input):
        user_input = "email"
    else:
        data = {
            'success': False,
            'message': "Username or phone or email is not valid"
        }
        return ValidationError(data)
    return user_input


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']],
        )
        if data.get('content_type') == 'html':
            email.content_subtype = 'html'
        EmailThread(email).start()


def send_email(email, code):
    html_content = render_to_string(
        'email/authentication/activate_account.html',
        {'code': code}
    )
    Email.send_email(
        {
            'subject': "Registration",
            'to_email': email,
            'body': html_content,
            'content_type': 'html'
        }
    )


def send_phone_code(phone, code):
    account_sit = config('account_sit')
    auth_token = config('auth_token')
    client = Client(account_sit, auth_token)
    client.messages.create(
        body="Hi, your confirmation code is {}\n".format(code),
        from_="+998938340103",
        to=f"{phone}"
    )
