def get_team_schedules():
    return {
        "actions": [{"id": 1, "name": "Huisbezoek"}],
        "week_segments": [
            {"id": 1, "name": "Doordeweek"},
            {"id": 2, "name": "Weekend"},
        ],
        "day_segments": [{"id": 2, "name": "Avond"}, {"id": 1, "name": "Overdag"}],
        "priorities": [
            {"id": 1, "name": "Hoog", "weight": 1.0},
            {"id": 2, "name": "Normaal", "weight": 0.0},
        ],
    }


def get_team_reasons():
    return [
        {"id": 30, "name": "Melding", "team": 58},
    ]


def get_team_state_types():
    return [
        {"id": 1, "name": "In behandeling", "team": 58},
        {"id": 2, "name": "Nog niet gelopen", "team": 58},
        {"id": 3, "name": "Niemand aanwezig", "team": 58},
        {"id": 4, "name": "Toegang verleend", "team": 58},
        {"id": 5, "name": "In looplijst", "team": 58},
        {"id": 6, "name": "Huisbezoek uitzetten", "team": 58},
        {"id": 7, "name": "Debrief", "team": 58},
        {"id": 8, "name": "Aanschrijvingen", "team": 58},
    ]
