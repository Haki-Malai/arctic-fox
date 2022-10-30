from flask import Blueprint, redirect, url_for

documentation = Blueprint('documentation', __name__)

@documentation.route('/')
def index():  # pragma: no cover
    return redirect(url_for('apifairy.docs'))