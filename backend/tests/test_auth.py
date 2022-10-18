from api.models import User, Role, Post, Comment
import unittest
import json
import re
from base64 import b64encode
from api.app import create_app, db
from werkzeug.http import HTTP_STATUS_CODES


class AuthenticationTestCase(unittest.TestCase):
    s = 1