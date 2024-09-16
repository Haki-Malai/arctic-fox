FROM python:3.12-slim

ENV FLASK_ENV production

RUN apt-get update

RUN mkdir -p /var/log/gunicorn

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY .dockenv .env
COPY api api
COPY database database
COPY migrations migrations
COPY utils utils
COPY cli cli
COPY app.py config.py boot.sh ./

EXPOSE 80

CMD ./boot.sh
