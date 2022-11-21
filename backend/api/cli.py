import click
from flask import Blueprint

script = Blueprint('script', __name__)


@script.cli.command('test')
@click.argument('patern', default='*')
@click.option('--verbosity', default=2, type=int)
def test(patern, verbosity):
    """
        Run tests with a specific pattern.
        Use patern string like 'test_*.py' to run specific test.
        If no patern is provided, all tests will be run."""
    import unittest
    patern = f'test_*{patern}*.py'
    tests = unittest.TestLoader().discover('tests', patern)
    unittest.TextTestRunner(verbosity=verbosity).run(tests)

@script.cli.command('fake', help='Generate fake data and commit to database.')
def fake():
    from api.app import db
    db.drop_all()
    db.create_all()
    from api.fake import fake_users, fake_posts,\
        fake_comments, fake_follows, fake_notifications, fake_tasks
    fake_users()
    fake_follows()
    fake_posts()
    fake_comments()
    fake_notifications()
    fake_tasks()