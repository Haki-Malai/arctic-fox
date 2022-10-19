import os
import click
from flask import Blueprint

run_script = Blueprint('run_script', __name__)


@run_script.cli.command('test')
@click.option('--patern', default='test*.py')
@click.option('--verbosity', default=2, type=int)
def test(patern, verbosity):
    import unittest
    tests = unittest.TestLoader().discover('tests', patern)
    unittest.TextTestRunner(verbosity=verbosity).run(tests)

@run_script.cli.command('fake-data')
def fake(fake):
    from api.app import db
    db.drop_all()
    db.create_all()
    from api.fake import fake_admins, fake_users, fake_posts,\
        fake_comments, fake_follows, fake_notifications, fake_tasks
    fake_admins()
    fake_users()
    fake_posts()
    fake_comments()
    fake_tasks()