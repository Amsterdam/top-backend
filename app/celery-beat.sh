#!/usr/bin/env bash
set -e

celery -A settings beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
