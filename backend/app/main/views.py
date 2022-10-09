from . import main
from .. import db
from ..models import User
from flask import session
from datetime import datetime

@main.route('/', methods=['GET'])
def index():
    return 'Hello World!'