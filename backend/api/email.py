from api.app import mail
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message


def send_async_email(app, msg):
    with app.app_context():  # pragma: no cover
        try:
            mail.send(msg)
        except Exception as e:
            print('Failed to send email to %s: %s' % msg.recipients[0] % str(e))


def send_email(to, subject, template, **kwargs):  # pragma: no cover
    app = current_app._get_current_object()
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    msg.msgId = app.config['MAIL_SUBJECT_PREFIX']
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr