from datetime import datetime

from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

import utils.queries as q
import utils.queries_bag_api as bag_api
import utils.queries_brk_api as brk_api
from api.cases.serializers import UnplannedCasesSerializer
from api.cases.swagger_parameters import unplanned_parameters, case_search_parameters
from api.fraudprediction.utils import get_fraud_prediction, add_fraud_predictions
from api.itinerary.models import Itinerary
from api.itinerary.serializers import CaseSerializer, ItineraryTeamMemberSerializer
from utils.safety_lock import safety_lock
from drf_spectacular.utils import extend_schema


@method_decorator(safety_lock, 'retrieve')
@method_decorator(safety_lock, 'unplanned')
class CaseViewSet(ViewSet):
    """
    A Viewset for showing a single Case in detail
    """

    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk):
        case_id = pk
        related_case_ids = q.get_related_case_ids(case_id)

        wng_id = related_case_ids.get('wng_id', None)
        adres_id = related_case_ids.get('adres_id', None)

        if not wng_id or not adres_id:
            return HttpResponseNotFound('Case not found')

        # Get the bag_data first in order to retrieve the 'verblijfsobjectidentificatie' id
        bag_data = bag_api.get_bag_data(wng_id)
        bag_id = bag_data.get('verblijfsobjectidentificatie')

        data = {
            'bwv_hotline_bevinding': q.get_bwv_hotline_bevinding(wng_id),
            'bwv_hotline_melding': q.get_bwv_hotline_melding(wng_id),
            'bwv_personen': q.get_bwv_personen(adres_id),
            'import_adres': q.get_import_adres(wng_id),
            'import_stadia': q.get_import_stadia(case_id),
            'bwv_tmp': q.get_bwv_tmp(case_id, adres_id),
            'statements': q.get_statements(case_id),
            'vakantie_verhuur': q.get_rental_information(wng_id),
            'bag_data': bag_data,
            'brk_data': brk_api.get_brk_data(bag_id),
            'related_cases': q.get_related_cases(adres_id),
            'fraud_prediction': get_fraud_prediction(case_id)
        }

        return JsonResponse(data)

    @extend_schema(parameters=unplanned_parameters, description='Unplanned Cases')
    @action(detail=False, methods=['get'], name='unplanned')
    def unplanned(self, request):
        """ Returns a list of unplanned cases, based on the given date and stadium """
        serializer = UnplannedCasesSerializer(data=request.GET)
        is_valid = serializer.is_valid()

        if not is_valid:
            return JsonResponse({
                'message': 'Could not validate data',
                'errors': serializer.errors
            }, status=HttpResponseBadRequest.status_code)

        date = request.GET.get('date')
        stadium = request.GET.get('stadium')
        unplanned_cases = Itinerary.get_unplanned_cases(date, stadium)
        cases = add_fraud_predictions(unplanned_cases)

        return JsonResponse({'cases': cases})


class CaseSearchViewSet(ViewSet, ListAPIView):
    """
    A temporary search ViewSet for listing cases
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CaseSerializer
    queryset = ''

    def __add_fraud_prediction__(self, cases):
        """
        Enriches the cases with fraud predictions
        """
        cases = cases.copy()

        for case in cases:
            case_id = case.get('case_id')
            case['fraud_prediction'] = get_fraud_prediction(case_id)

        return cases

    def __add_teams__(self, cases, itineraries_created_at):
        """
        Enriches the cases with teams
        """
        # Enrich the search result data with teams whose itinerary contains this item
        mapped_cases = {}
        cases = cases.copy()

        for case in cases:
            # Map the objects so that they're easily accessible through the case_id
            case_id = case.get('case_id')
            mapped_cases[case_id] = case
            # Add a teams arrar to the case object as well
            case['teams'] = []

        # Get today's itineraries
        itineraries = Itinerary.objects.filter(created_at=itineraries_created_at).all()

        for itinerary in itineraries:
            team = itinerary.team_members.all()
            itinerary_cases = itinerary.get_cases()

            # Match the mapped_cases to the itinerary_cases, and add the teams
            for case in itinerary_cases:
                case_id = case.case_id
                mapped_case = mapped_cases.get(case_id, {'teams': []})
                serialized_team = ItineraryTeamMemberSerializer(team, many=True)
                mapped_case['teams'].append(serialized_team.data)

        return cases

    @extend_schema(parameters=case_search_parameters, description='Search query parameters')
    @action(detail=False, methods=['get'])
    @safety_lock
    def list(self, request):
        """
        Returns a list of cases found with the given parameters
        """
        postal_code = request.GET.get('postalCode', None)
        street_number = request.GET.get('streetNumber', None)
        suffix = request.GET.get('suffix', '')

        if postal_code is None:
            return HttpResponseBadRequest('Missing postal code is required')
        elif not street_number:
            return HttpResponseBadRequest('Missing steet number is required')
        else:
            cases = q.get_search_results(postal_code, street_number, suffix)
            cases = self.__add_fraud_prediction__(cases)
            cases = self.__add_teams__(cases, datetime.now())

            return JsonResponse({'cases': cases})
