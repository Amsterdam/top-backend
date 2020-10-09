from enum import Enum

from apps.visits.models import Visit
from settings import const


class SCORING_WEIGHTS(Enum):
    DISTANCE = 1
    FRAUD_PROBABILITY = 1
    PRIMARY_STADIUM = 0.75
    SECONDARY_STADIUM = 0.5
    ISSUEMELDING = 0.75


MAX_SUGGESTIONS_COUNT = 20


TEAM_TYPE_VAKANTIEVERHUUR = "Vakantieverhuur"
TEAM_TYPE_ONDERVERHUUR = "Onderverhuur"

TEAM_TYPE_SETTINGS = {
    TEAM_TYPE_VAKANTIEVERHUUR: {
        "name": TEAM_TYPE_VAKANTIEVERHUUR,
        "project_choices": const.PROJECTS_VAKANTIEVERHUUR,
        "stadia_choices": const.STADIA_VAKANTIEVERHUUR,
        "observation_choices": Visit.OBSERVATIONS,
        "suggest_next_visit_choices": Visit.SUGGEST_NEXT_VISIT,
        "situation_choices": Visit.SITUATIONS,
        "week_day_choices": [0, 1, 2, 3, 4, 5, 6],
        "show_list_fraudprediction": True,
        "show_fraudprediction": True,
        "show_issuemelding": True,
    },
    TEAM_TYPE_ONDERVERHUUR: {
        "name": TEAM_TYPE_ONDERVERHUUR,
        "project_choices": const.PROJECTS_ONDERVERHUUR,
        "stadia_choices": const.STADIA_ONDERVERHUUR,
        "observation_choices": Visit.OBSERVATIONS,
        "suggest_next_visit_choices": Visit.SUGGEST_NEXT_VISIT,
        "situation_choices": Visit.SITUATIONS,
        "week_day_choices": [0, 1, 2, 3, 4],
        "show_list_fraudprediction": False,
        "show_fraudprediction": False,
        "show_issuemelding": False,
    },
}

TEAM_TYPE_CHOICES = [[k, k] for k, v in TEAM_TYPE_SETTINGS.items()]
