import click
import psycopg2
from flask import Blueprint
from sqlalchemy import inspect

from api import db
from config import config

bp = Blueprint('database', __name__)


@bp.cli.command()
def init():
    """Initialize the database."""
    db.create_all()


@bp.cli.command()
@click.argument('tables', default='all')
def drop(tables: str = 'all'):
    """Drop all tables in the database.

    :param tables: The tables to drop. Default is 'all'.
    """
    if tables == 'all':
        db.drop_all()
        print('All tables dropped')
        return

    DROP_TABLES_SCRIPT = """
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name LIKE %s)
            LOOP
                EXECUTE 'DROP TABLE ' || quote_ident(r.table_name) || ' CASCADE';
            END LOOP;
        END $$;
    """
    try:
        conn = psycopg2.connect(config.ALCHEMICAL_DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute(DROP_TABLES_SCRIPT, (f'{tables}%',))
        conn.commit()
    except psycopg2.Error as e:
        print('Error dropping tables:', e)
    finally:
        if conn:
            conn.close()


@bp.cli.command()
def view():
    """View all tables in the database"""
    engine = db.get_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    for table in tables:
        print(table)
