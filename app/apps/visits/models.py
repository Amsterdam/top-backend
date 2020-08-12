from apps.itinerary.models import ItineraryItem
from apps.users.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Visit(models.Model):
    """ Captures data of a visit """

    SITUATION_NOBODY_PRESENT = "nobody_present"
    SITUATION_NO_COOPERATION = "no_cooperation"
    SITUATION_ACCESS_GRANTED = "access_granted"

    SITUATIONS = (
        (SITUATION_NOBODY_PRESENT, "Niemand aanwezig"),
        (SITUATION_NO_COOPERATION, "Geen medewerking"),
        (SITUATION_ACCESS_GRANTED, "Toegang verleend"),
    )

    OBSERVATION_MALFUNCTIONING_DOORBEL = "malfunctioning_doorbell"
    OBSERVATION_VIDEO_CALL = "video_call"
    OBSERVATION_HOTEL_FURNISHED = "hotel_furnished"
    OBSERVATION_VACANT = "vacant"
    OBSERVATION_LIKELY_INHABITED = "likely_inhabited"

    OBSERVATIONS = (
        (OBSERVATION_MALFUNCTIONING_DOORBEL, "Bel functioneert niet"),
        (OBSERVATION_VIDEO_CALL, "Contact via videobel"),
        (OBSERVATION_HOTEL_FURNISHED, "Hotelmatig ingericht"),
        (OBSERVATION_VACANT, "Leegstaand"),
        (OBSERVATION_LIKELY_INHABITED, "Vermoedelijk bewoond"),
    )

    SUGGEST_VISIT_WEEKEND = "weekend"
    SUGGEST_VISIT_DAYTIME = "daytime"
    SUGGEST_VISIT_EVENING = "evening"
    SUGGEST_VISIT_UNKNOWN = "unknown"

    SUGGEST_NEXT_VISIT = (
        (SUGGEST_VISIT_WEEKEND, "Weekend"),
        (SUGGEST_VISIT_DAYTIME, "Overdag"),
        (SUGGEST_VISIT_EVENING, "'s Avonds"),
        (SUGGEST_VISIT_UNKNOWN, "Onbekend"),
    )

    situation = models.CharField(
        max_length=50, choices=SITUATIONS, null=True, blank=True
    )
    observations = ArrayField(
        models.CharField(max_length=50, choices=OBSERVATIONS), blank=True, null=True
    )
    itinerary_item = models.ForeignKey(
        ItineraryItem, on_delete=models.CASCADE, related_name="visits"
    )
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=False)

    description = models.TextField(
        null=True
    )  # these are the notes when access was granted

    # Describe if next visit can go ahead and why yes or no
    can_next_visit_go_ahead = models.BooleanField(default=True, blank=True, null=True)
    can_next_visit_go_ahead_description = models.TextField(null=True)

    # suggest_visit_next_time = models.BooleanField(default=True) # TODO not sure about this one
    suggest_next_visit = models.CharField(
        null=True, max_length=50, choices=SUGGEST_NEXT_VISIT
    )
    suggest_next_visit_description = models.TextField(null=True, blank=True)

    # personal notes to help make report at the office/as reminders for TH.
    personal_notes = models.TextField(blank=True, null=True)
