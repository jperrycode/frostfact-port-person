release: python frostfact/manage.py migrate --noinput
web: gunicorn --pythonpath frostfact frostfact.wsgi --log-file -