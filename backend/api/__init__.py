"""
Welcome to ArcticFox's API documentation. If you want to learn more about this project or how to contribute, please visit our [GitHub repository](https://github.com/Haki-Malai/arctic-fox).

This API is built using [Flask](https://flask.palletsprojects.com/) web framework, 
a modern, lightweight [WSGI](https://wsgi.readthedocs.io/en/latest/) micro web framework for building APIs with Python.
 This API is also uses:
  - [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/latest/), an extension for Flask that adds support for [SQLAlchemy](https://www.sqlalchemy.org/),
  - [Flask-Marshmallow](https://flask-marshmallow.readthedocs.io/en/latest/), a thin integration layer for [Marshmallow](https://marshmallow.readthedocs.io/en/stable/),
  - [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/en/latest/), a Flask extension that simplifies the use of HTTP authentication with Flask routes and
  - [APIFairy](https://apifairy.readthedocs.io/en/latest/), a minimalistic API framework that uses Marshmallow schemas to generate API documentation.
And others like [Flask-Mail](https://pythonhosted.org/Flask-Mail/), [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/), [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/en/latest/) 
and other common Python libraries.

## Quickstart

#### If you want to run this API locally, you can follow these steps:
  - With Docker:
    - Install [Docker](https://docs.docker.com/get-docker/).
    - Clone the [repository](https://github.com/Haki-Malai/arctic-fox).
    - Cd into the cloned repository.
    - Run `docker build -t arcticfox` and wait for the build to finish.
    - Run `docker run -p 5000:5000 arcticfox` and wait for the container to start.
    - The API should be available at http://localhost:5000.
  - Directly:
    - Clone the [repository](https://github.com/Haki-Malai/arctic-fox).
    - Cd into the backend folder of the cloned repository.
    - Create a virtual environment using [virtualenv](https://virtualenv.pypa.io/en/latest/) or [venv](https://docs.python.org/3/library/venv.html).
    - Activate the virtual environment.
    - Run `pip install -r requirements.txt`.
    - With gunicorn
      - Run `gunicorn -b :5000 index:app`.
    - With flask (debug mode)
      - Run `flask --app index --debug run`.
    - The API should be available at http://localhost:5000.

#### If you want to push your own API to heroku, you can follow these steps:
  - Make a heroku account.
  - Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) and run `heroku login` to login to your heroku account. 
  - Then run `heroku create <app-name>`.
  - Login to the heroku container registry by running `heroku container:login`.
  - Push the docker image to heroku by running `heroku container:push web`.
  - Release the docker image to heroku by running `heroku container:release web`.
  - Open the app by running `heroku open`.

#### If you want to automatically deploy to heroku when you push to GitHub, you can follow these steps:
  - Follow the steps above to install heroku CLI and login to your heroku account.
  - Run `heroku auth:token` to get your heroku API key and copy it.
  - Navigate to your github fork.
  - Go to 'Settings>Secrets>Actions>New repository secret'.
  - Create a new secret with the name `HEROKU_API_KEY` and paste your heroku API key as the value.
  - Create a new secret with the name `HEROKU_APP_NAME` and paste your heroku app name as the value.
  - Create a new secret with the name `HEROKU_EMAIL` and paste your heroku email as the value.
  - Now the app will be automatically deployed to heroku when you push to GitHub.
"""
from api.app import create_app, db, ma  # noqa: F401