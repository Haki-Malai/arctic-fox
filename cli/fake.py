import random
import click
from datetime import datetime, timedelta
from flask import Blueprint
from faker import Faker
from sqlalchemy.exc import IntegrityError
from api.app import db
from api.models import User, Folder, File
from api.enums import Role

fake = Blueprint('fake', __name__)
faker = Faker()


def random_datetime_this_year() -> datetime:
    """Generate a random datetime within the current year."""
    year_start = datetime(datetime.now().year, 1, 1)
    year_end = datetime(datetime.now().year, 12, 31, 23, 59, 59)

    random_datetime = year_start + timedelta(
        seconds=random.randint(0, int((year_end - year_start).total_seconds())))

    return random_datetime


@fake.cli.command('users')
@click.argument('num', type=int)
def users(num):
    """Create the given number of fake users."""
    for _ in range(num):
        email = faker.email()
        try:
            user = User(
                email=email,
                username=faker.user_name(),
                role=random.choice(list(Role)),
                activated=faker.boolean(),
                avatar_url=faker.image_url()
            )
            db.session.add(user)
            db.session.commit()
            print(f'Added user: {user.email}')
        except IntegrityError:
            db.session.rollback()
            print(f'User with email {email} already exists.')


@fake.cli.command('folders')
@click.argument('num', type=int)
@click.option('--user-id', type=int, help='Specific user ID to assign the folders. If not provided, a random user will be chosen.')
def folders(num, user_id=None):
    """Create the given number of fake folders."""
    if user_id:
        user = db.session.scalar(User.select().filter_by(id=user_id).first())
        if not user:
            print(f'No user found with ID: {user_id}')
            return
    else:
        users = db.session.scalars(User.select()).all()
        if not users:
            print('No users found. Add some users first.')
            return
        user = random.choice(users)

    for _ in range(num):
        folder = Folder(
            name=faker.word(),
            description=faker.paragraph(),
            created_by=user.id
        )
        db.session.add(folder)

    db.session.commit()
    print(f'Added {num} folders.')


@fake.cli.command('files')
@click.argument('num', type=int)
def files(num: int) -> None:
    """Create the given number of fake files, assigned to random users."""
    users = db.session.scalars(User.select()).all()
    folders = db.session.scalars(Folder.select()).all()
    if not users:
        print('No users found. Add some users first.')
        return

    added_files = 0
    for _ in range(num):
        try:
            user = random.choice(users)
            folder = random.choice(folders)
            mimetype_extension_mapping = {
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/gif': '.gif',
                'video/mp4': '.mp4',
            }
            mimetype = random.choice(list(mimetype_extension_mapping.keys()))
            filename = faker.file_name(extension=mimetype_extension_mapping[mimetype].strip('.'))

            random_date = random_datetime_this_year()
            
            file = File(
                filename=filename,
                mimetype=mimetype,
                description=faker.paragraph(),
                processed=faker.boolean(),
                dominant_color=faker.color(),
                error=None if faker.boolean(chance_of_getting_true=75) else faker.sentence(),
                created_by=user.id,
                created_at=random_date,
                folder_id=folder.id
            )
            db.session.add(file)
            db.session.commit()
            added_files += 1
        except Exception as e:
            db.session.rollback()
            print(f'Failed to add a file: {e}')

    print(f'Added {added_files} files.')
