import logging

from apps.fraudprediction.models import FraudPrediction
from apps.itinerary.tasks import push_visit
from apps.visits.models import Visit, VisitMetaData
from django.conf import settings
from django.db import transaction
from django.db.models import signals
from django.dispatch import receiver
