FROM python:3.12-slim

ENV FLASK_APP arctic_fox.py
ENV FLASK_ENV production

RUN apt-get update

RUN mkdir -p /var/log/gunicorn

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY .env .env
COPY api api
COPY migrations migrations
COPY utils utils
COPY cli cli
COPY arctic_fox.py config.py boot.sh ./

EXPOSE 80

CMD ./boot.sh
