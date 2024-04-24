#!/usr/bin/env bash
set -e

celery -A settings worker --beat --scheduler django_celery_beat.schedulers:DatabaseScheduler  -l INFO
