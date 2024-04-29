FROM python:3.11-slim

ENV FLASK_APP arctic_fox.py
ENV FLASK_ENV production

RUN apt-get update

RUN mkdir -p /var/log/gunicorn

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api api
COPY migrations migrations
COPY utils utils
COPY cli cli
COPY arctic_fox.py config.py boot.sh ./

EXPOSE 8080

CMD ./boot.sh
