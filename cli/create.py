from flask import Blueprint

from api.app import db

bp = Blueprint('create', __name__)


@bp.cli.command()
def all():
    try:
        db.create_all()
        print('All tables created successfully.')
    except Exception as e:
        print(f'An error occurred while creating tables: {e}')
