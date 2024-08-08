#!/bin/bash

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


exec "$@"
