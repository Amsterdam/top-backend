# Same as entrypoint.sh, but with py-auto-reload enabled to allow auto reloading when making changes during development

#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

until PGPASSWORD=$DATABASE_PASSWORD psql -h $DATABASE_HOST -U $DATABASE_USER -c '\q'; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done
echo "Postgres is up!"

echo Collecting static files
python manage.py collectstatic --no-input

yes yes | python manage.py migrate --noinput

chmod -R 777 /static

# modify permission so scoring files can be cached
chmod -R 700 /fraud_prediction_cache

celery -A settings worker -l INFO -D --purge
celery -A settings beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --detach

# run uwsgi
exec uwsgi --ini /app/deploy/config.ini --py-auto-reload=1 --cheaper-initial=1 --cheaper=1 --processes=10
# /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
