from flask import current_app, render_template, url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from threading import Thread

def send_async_email(msg):
    import sys
    sys.path.append("..")
    from flask_manage import app, mail
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, html_body):
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    sender = Thread(target=send_async_email, args=[msg])
    sender.start()

def send_password_reset_email(user_email):
    # Generate reset token
    password_reset_serializer = URLSafeTimedSerializer("square2020")

    # TODO: Fix Generate the reset link

    token = password_reset_serializer.dumps(user_email, salt='password-reset-salt')
    password_reset_url = "http://localhost/#/ResetPassword/"+token
    html = render_template('email_password_reset.html', password_reset_url=password_reset_url)
    send_email('Password Reset Requested', [user_email], html)

def send_confirmation_email(user_email):
    # Generate confirmation token,
    confirm_serializer = URLSafeTimedSerializer("square2020")

    #TODO: Fix Generate confirmation token

    token = confirm_serializer.dumps(user_email, salt='email-confirmation-salt')
    confirm_url = "http://localhost/#/ConfirmEmailLanding/"+token
    html = render_template('email_confirmation.html', confirm_url=confirm_url)
    send_email('Please complete your registration', [user_email], html)
