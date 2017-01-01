web: newrelic-admin run-program gunicorn --pythonpath="$PWD/rugbystat" wsgi:application
worker: python rugbystat/manage.py rqworker default