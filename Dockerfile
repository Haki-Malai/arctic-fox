# Build the flask app with the expo web build as static files
FROM python:3.8.10

LABEL maintainer="Haki-Malai" email="hakimalaj@outlook.com"

COPY backend .

#COPY --from=web-build /web-build ./static/web-build

RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", ":5000", "index:app"]
