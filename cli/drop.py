from flask import Blueprint
from sqlalchemy.exc import SQLAlchemyError

from api.app import db
from api import models

bp = Blueprint('drop', __name__)


@bp.cli.command()
def all():
    """Drop all tables from the database."""
    warning_msg = (
        "You are about to DROP ALL TABLES from the database. "
        "This action is IRREVERSIBLE. Do you wish to proceed? (y/N): ")
    confirm = input(warning_msg)

    if confirm.lower() == 'y':
        engine = db.get_engine()
        for attr in dir(models):
            model = getattr(models, attr)
            if model == db.Model:
                try:
                    db.session.scalars(model.select()).delete()
                    db.session.commit()
                    print(f"Table {model.__tablename__} dropped.")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    print(f"Error dropping table {model.__tablename__}: {e}")
        print("All tables have been dropped.")
    else:
        print("Action aborted.")
