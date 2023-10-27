from apps.visits.models import Observation, SuggestNextVisit, Visit
from apps.visits.serializers import (
    ObservationSerializer,
    SuggestNextVisitSerializer,
    VisitSerializer,
)
from rest_framework.viewsets import ModelViewSet


# Create your views here.
class VisitViewSet(ModelViewSet):
    serializer_class = VisitSerializer
    queryset = Visit.objects.all()


class ObservationViewSet(ModelViewSet):
    serializer_class = ObservationSerializer
    queryset = Observation.objects.all()


class SuggestNextVisitViewSet(ModelViewSet):
    serializer_class = SuggestNextVisitSerializer
    queryset = SuggestNextVisit.objects.all()
