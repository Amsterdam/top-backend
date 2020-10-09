from datetime import datetime

from apps.itinerary.models import Itinerary, ItineraryItem, Note
from apps.itinerary.serializers import (
    ItineraryItemCreateSerializer,
    ItineraryItemSerializer,
    ItineraryItemUpdateSerializer,
    ItinerarySerializer,
    ItineraryTeamMemberSerializer,
    NoteCrudSerializer,
)
from apps.planner.serializers import (
    TeamSettingsSerializer
)
from apps.users.models import User
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class ItineraryViewSet(ViewSet, GenericAPIView, DestroyModelMixin, CreateModelMixin):
    """
    CRUD for itineraries and teams
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ItinerarySerializer
    queryset = Itinerary.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["created_at"]

    def get_object(self):
        MESSAGE = (
            "De looplijst is niet gevonden. De lijst is misschien verwijderd door een"
            " andere gebruiker."
        )
        try:
            return super().get_object()
        except Http404:
            raise NotFound(MESSAGE)

    def __get_all_itineraries__(self, user, date=None):
        itineraries = Itinerary.objects.filter(team_members__user=user)

        if date:
            itineraries = itineraries.filter(created_at=date)

        serializer = self.serializer_class(itineraries, many=True)

        return serializer.data

    def __get_date_from_query_parameter__(self, request):
        """
        Returns a datetime date object if the query parameters contained a date
        """
        date_string = self.request.query_params.get("created_at", None)

        if not date_string:
            return

        try:
            date = datetime.strptime(date_string, "%Y-%m-%d")
            return date
        except ValueError as e:
            raise APIException("Could not read date query parameter: {}".format(e))

    def __get_serialized_team__(self, itinerary_pk):
        itinerary = self.get_object()
        team_members = itinerary.team_members
        team_members_serialized = ItineraryTeamMemberSerializer(team_members, many=True)

        return Response({"team_members": team_members_serialized.data})

    def __replace_team_members__(self, itinerary_pk, user_ids):
        itinerary = self.get_object()
        serializer = ItineraryTeamMemberSerializer(data=user_ids, many=True)

        if not serializer.is_valid():
            raise APIException(
                "Could not add team members: {}".format(serializer.errors)
            )

        user_ids = [user_id.get("user").get("id") for user_id in user_ids]

        itinerary.clear_team_members()
        itinerary.add_team_members(user_ids)

    @action(detail=True, methods=["get", "put"])
    def team(self, request, pk):
        if request.method == "GET":
            return self.__get_serialized_team__(pk)

        if request.method == "PUT":
            new_team_members = request.data.get("team_members")
            self.__replace_team_members__(pk, new_team_members)
            return self.__get_serialized_team__(pk)

    @action(detail=True, methods=["get"])
    def suggestions(self, request, pk):
        """ Returns a list of suggestions for the given itinerary """
        itinerary = self.get_object()
        cases = itinerary.get_suggestions()
        return JsonResponse({"cases": cases})

    @transaction.atomic
    def create(self, request):
        serializer = ItinerarySerializer(data=request.data)

        if not serializer.is_valid():
            raise APIException(
                "Could not create itinerary (serializer): {}".format(serializer.errors)
            )

        # Create the itinerary
        try:
            itinerary = serializer.create(request.data)
            cases = itinerary.get_cases_from_settings()
            assert len(cases), "Not enough cases available for given settings"
        except Exception as e:
            raise APIException("Could not create itinerary from settings: {}".format(e))

        # Populate the itinerary with cases
        for case in cases:
            case_id = case.get("case_id")
            itinerary.add_case(case_id)

        # Serialize the itinerary again
        serializer = ItinerarySerializer(itinerary)

        return Response(serializer.data)

    def list(self, request):
        date = self.__get_date_from_query_parameter__(request)
        user = get_object_or_404(User, id=request.user.id)
        itineraries = self.__get_all_itineraries__(user, date)

        return Response({
            "itineraries": itineraries,
        })


class ItineraryItemViewSet(
    ViewSet, GenericAPIView, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
):
    """
    A view for adding/removing an item to a user's itinerary
    """

    permission_classes = [IsAuthenticated]
    queryset = ItineraryItem.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ItineraryItemCreateSerializer
        elif self.request.method in ["PATCH", "PUT"]:
            return ItineraryItemUpdateSerializer
        return ItineraryItemSerializer

    def create(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)

        if not serializer.is_valid():
            raise APIException(
                "Could not create itinerary item: {}".format(serializer.errors)
            )

        try:
            itinerary_item = serializer.create(request.data)
        except Exception as e:
            raise APIException(str(e))

        # Serialize and return data
        serializer = ItineraryItemSerializer(itinerary_item, many=False)
        return Response(serializer.data)


class NoteViewSet(
    ViewSet, GenericAPIView, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
):
    """
    A view for adding/updating/removing a note
    """

    permission_classes = [IsAuthenticated]
    serializer_class = NoteCrudSerializer
    queryset = Note.objects.all()

    def retrieve(self, request, pk=None):
        note = get_object_or_404(self.queryset, pk=pk)
        serializer = NoteCrudSerializer(note)
        return Response(serializer.data)

    def create(self, request):
        # Get the current user and it's itinerary
        user = get_object_or_404(User, id=request.user.id)

        text = request.data["text"]
        itinerary_item_id = request.data["itinerary_item"]

        itinerary_item = get_object_or_404(ItineraryItem, id=itinerary_item_id)
        note = Note.objects.create(
            author=user, text=text, itinerary_item=itinerary_item
        )
        note.save()

        # Serialize and return data
        serializer = NoteCrudSerializer(note, many=False)
        return Response(serializer.data)
