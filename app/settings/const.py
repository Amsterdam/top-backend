WEEK_DAYS = [
    "zondag",
    "maandag",
    "dinsdag",
    "woensdag",
    "donderdag",
    "vrijdag",
    "zaterdag",
]
WEEK_DAYS_CHOICES = [[i, wd] for i, wd in enumerate(WEEK_DAYS)]

STARTING_FROM_DATE = "2019-01-01"

POSTAL_CODE_RANGES = [
    {"range_start": 1000, "range_end": 1109},
    {"range_start": 1380, "range_end": 1384},
]

API_EXCEPTION_SEVERITY_ERROR = "ERROR"
API_EXCEPTION_SEVERITY_WARNING = "WARNING"
API_EXCEPTION_SEVERITY_INFO = "INFO"

ITINERARY_NOT_ENOUGH_CASES = {
    "severity": API_EXCEPTION_SEVERITY_INFO,
    "message": "Er zijn vandaag niet genoeg zaken die voldoen aan de ingestelde criteria. Neem contact op met je dagcoördinator of handhaver.",
    "title": "Helaas, geen looplijst mogelijk",
}

DAY_SETTING_IN_USE = {
    "severity": API_EXCEPTION_SEVERITY_INFO,
    "message": "De dag instelling is in gebruik. Als morgen deze instelling niet wordt gebruikt kun je hem alsnog verwijderen.",
    "title": "Verwijderen niet mogelijk",
}
