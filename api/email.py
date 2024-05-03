from threading import Thread

from flask import Flask, current_app, render_template
from flask_mail import Message

from api.app import mail


def send_async_email(app: Flask, to:str, subject:str, template:str,
                     sender=None, **kwargs) -> None:
    """Send an email asynchronously.

    :param app: Flask app
    :param to: Email recipient
    :param subject: Email subject
    :param template: Email template
    :param sender: Email sender
    :param kwargs: Additional keyword arguments
    """
    with app.app_context():
        msg = Message(subject, recipients=[to], sender=sender)
        msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)
        mail.send(msg)


def send_email(to:str, subject:str, template:str, sender=None, **kwargs) -> Thread:
    """Send an email.

    :param to: Email recipient
    :param subject: Email subject
    :param template: Email template
    :param sender: Email sender
    :param kwargs: Additional keyword arguments

    :return: The email thread
    """
    if sender is None:
        sender = current_app.config['MAIL_DEFAULT_SENDER']
    app = current_app._get_current_object()
    thread = Thread(target=send_async_email, args=(app, to, subject, template),
                    kwargs={**kwargs, 'sender': sender})
    thread.start()
    return thread
