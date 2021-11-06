#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

echo Collecting static files
python manage.py collectstatic --no-input

yes yes | python manage.py migrate --noinput

chmod -R 777 /static

# echo Create root user
# python manage.py shell -c "from apps.users.models import User; User.objects.create_superuser('admin@admin.com', 'admin')"

# Run celery worker and beat
celery -A settings worker -l INFO -D
celery -A settings beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --detach

# run uwsgi
exec uwsgi --ini /app/deploy/config.ini # --py-auto-reload=1
