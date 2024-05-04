#!/bin/sh
#flask db upgrade
exec gunicorn --timeout 240 -b :80 --access-logfile /var/log/gunicorn/access.log --error-logfile /var/log/gunicorn/error.log arctic_fox:app
