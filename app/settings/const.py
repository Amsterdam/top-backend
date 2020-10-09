BED_AND_BREAKFAST = "Bed en breakfast 2019"
BURGWALLEN_PROJECT_OUDEZIJDE = "Burgwallenproject Oudezijde"
CORPO_RICO = "Corpo-rico"
DIGITAAL_TOEZICHT_SAFARI = "Digital toezicht Safari"
DIGITAAL_TOEZICHT_ZEBRA = "Digital toezicht Zebra"
HAARLEMMERBUURT = "Haarlemmerbuurt"
HOTLINE = "Hotline"
MYSTERY_GUEST = "Mystery Guest"
PROJECT_ANDES = "Project Andes"
PROJECT_JORDAAN = "Project Jordaan"
PROJECT_LOBITH = "Project Lobith"
PROJECT_SAHARA = "Project Sahara"
SAFARI = "Safari"
PROJECT_SAFARI_2015 = "Safari 2015"
SAHARA_ADAMS_SUITES = "Sahara Adams Suites"
SAHARA_HELE_WONING = "Sahara hele woning"
SAHARA_MEER_DAN_4 = "Sahara meer dan 4"
SAHARA_RECENSIES = "Sahara Recensies"
SAHARA_VEEL_ADV = "Sahara veel adv"
PROJECT_SOCIAL_MEDIA_2019 = "Social Media 2019"
PROJECT_WOONSCHIP = "Woonschip (woonboot)"
PROJECT_ZEBRA = "Zebra"

PROJECT_ZKL_DOORVERHUUR = "ZKL Doorverhuur"
PROJECT_COMBI_BI_DOORPAK = "Combi BI Doorpak"
PROJECT_COMBI_BI_MELDING = "Combi BI Melding"
PROJECT_COMBI_DOORPAK = "Combi Doorpak"
PROJECT_COMBI_OVERBEWONING = "Combi Overbewoning"
PROJECT_COMBI_SAMENWONERS = "Combi Samenwoners"
PROJECT_COMBI_ZKL_DOORPAK = "Combi_ZKL_Doorpak"
PROJECT_COMBI_ZKL_MELDING = "Combi_ZKL_Melding"

PROJECTS = [
    BED_AND_BREAKFAST,
    BURGWALLEN_PROJECT_OUDEZIJDE,
    CORPO_RICO,
    DIGITAAL_TOEZICHT_SAFARI,
    DIGITAAL_TOEZICHT_ZEBRA,
    HAARLEMMERBUURT,
    HOTLINE,
    MYSTERY_GUEST,
    PROJECT_ANDES,
    PROJECT_JORDAAN,
    PROJECT_LOBITH,
    PROJECT_SAHARA,
    SAFARI,
    PROJECT_SAFARI_2015,
    SAHARA_ADAMS_SUITES,
    SAHARA_HELE_WONING,
    SAHARA_MEER_DAN_4,
    SAHARA_RECENSIES,
    SAHARA_VEEL_ADV,
    PROJECT_SOCIAL_MEDIA_2019,
    PROJECT_WOONSCHIP,
    PROJECT_ZEBRA,
    PROJECT_ZKL_DOORVERHUUR,
    PROJECT_COMBI_BI_DOORPAK,
    PROJECT_COMBI_BI_MELDING,
    PROJECT_COMBI_DOORPAK,
    PROJECT_COMBI_OVERBEWONING,
    PROJECT_COMBI_SAMENWONERS,
    PROJECT_COMBI_ZKL_DOORPAK,
    PROJECT_COMBI_ZKL_MELDING,
]

PROJECTS_WITHOUT_SAHARA = [
    BED_AND_BREAKFAST,
    BURGWALLEN_PROJECT_OUDEZIJDE,
    CORPO_RICO,
    DIGITAAL_TOEZICHT_SAFARI,
    DIGITAAL_TOEZICHT_ZEBRA,
    HAARLEMMERBUURT,
    HOTLINE,
    MYSTERY_GUEST,
    PROJECT_ANDES,
    PROJECT_JORDAAN,
    PROJECT_LOBITH,
    SAFARI,
    PROJECT_SAFARI_2015,
    PROJECT_SOCIAL_MEDIA_2019,
    PROJECT_WOONSCHIP,
    PROJECT_ZEBRA,
]

PROJECTS_VAKANTIEVERHUUR = PROJECTS_WITHOUT_SAHARA
PROJECTS_ONDERVERHUUR = [
    PROJECT_COMBI_BI_DOORPAK,
    PROJECT_COMBI_BI_MELDING,
    PROJECT_COMBI_DOORPAK,
    PROJECT_COMBI_OVERBEWONING,
    PROJECT_COMBI_SAMENWONERS,
    PROJECT_COMBI_ZKL_DOORPAK,
    PROJECT_COMBI_ZKL_MELDING,
]

# NOTE: More stages exist, but they are currently not used by this application
ONDERZOEK_BUITENDIENST = "Onderzoek buitendienst"
TWEEDE_CONTROLE = "2de Controle"
DERDE_CONTROLE = "3de Controle"
HERCONTROLE = "Hercontrole"
TWEEDE_HERCONTROLE = "2de hercontrole"
DERDE_HERCONTROLE = "3de hercontrole"
AVONDRONDE = "Avondronde"
ONDERZOEK_ADVERTENTIE = "Onderzoek advertentie"
WEEKEND_BUITENDIENST_ONDERZOEK = "Weekend buitendienstonderzoek"
ISSUEMELDING = "Issuemelding"

STADIA_ZL_CORPORATIE = "ZL Corporatie"
STADIA_CRIMINEEL_GEBRUIK_WONINGEN = "Crimineel gebruik woning"

STADIA = [
    ONDERZOEK_BUITENDIENST,
    TWEEDE_CONTROLE,
    DERDE_CONTROLE,
    HERCONTROLE,
    TWEEDE_HERCONTROLE,
    DERDE_HERCONTROLE,
    AVONDRONDE,
    ONDERZOEK_ADVERTENTIE,
    WEEKEND_BUITENDIENST_ONDERZOEK,
    ISSUEMELDING,
    STADIA_ZL_CORPORATIE,
    STADIA_CRIMINEEL_GEBRUIK_WONINGEN,
]

STADIA_VAKANTIEVERHUUR = [
    ONDERZOEK_BUITENDIENST,
    TWEEDE_CONTROLE,
    DERDE_CONTROLE,
    HERCONTROLE,
    TWEEDE_HERCONTROLE,
    DERDE_HERCONTROLE,
    AVONDRONDE,
    ONDERZOEK_ADVERTENTIE,
    WEEKEND_BUITENDIENST_ONDERZOEK,
    ISSUEMELDING,
]

STADIA_ONDERVERHUUR = [
    STADIA_ZL_CORPORATIE,
    TWEEDE_CONTROLE,
    DERDE_CONTROLE,
    AVONDRONDE,
    STADIA_CRIMINEEL_GEBRUIK_WONINGEN,
    HERCONTROLE,
    ONDERZOEK_BUITENDIENST,
]

STARTING_FROM_DATE = "2019-01-01"

EXAMPLE_PLANNER_SETTINGS = {
    "opening_date": "2019-01-01",
    "projects": PROJECTS_WITHOUT_SAHARA,
    # Optional postal code settings
    "postal_codes": [{"range_start": 1000, "range_end": 1109}],
    "days": {
        "monday": {
            "day": {
                "length_of_list": 6,
                "primary_stadium": ONDERZOEK_BUITENDIENST,
                "secondary_stadia": [TWEEDE_CONTROLE, DERDE_CONTROLE],
            },
            "evening": {
                "length_of_list": 6,
                "primary_stadium": AVONDRONDE,
                "secondary_stadia": [
                    HERCONTROLE,
                    TWEEDE_HERCONTROLE,
                    DERDE_HERCONTROLE,
                ],
            },
        },
        "tuesday": {
            "day": {},
            "evening": {
                "length_of_list": 6,
                "primary_stadium": AVONDRONDE,
                "secondary_stadia": [
                    HERCONTROLE,
                    TWEEDE_HERCONTROLE,
                    DERDE_HERCONTROLE,
                ],
            },
        },
        "wednesday": {
            "day": {},
            "evening": {
                "length_of_list": 6,
                "primary_stadium": AVONDRONDE,
                "secondary_stadia": [
                    HERCONTROLE,
                    TWEEDE_HERCONTROLE,
                    DERDE_HERCONTROLE,
                ],
            },
        },
        "thursday": {
            "day": {
                "length_of_list": 6,
                "primary_stadium": ONDERZOEK_BUITENDIENST,
                "secondary_stadia": [TWEEDE_CONTROLE, DERDE_CONTROLE],
            },
            "evening": {
                "length_of_list": 6,
                "primary_stadium": AVONDRONDE,
                "secondary_stadia": [
                    HERCONTROLE,
                    TWEEDE_HERCONTROLE,
                    DERDE_HERCONTROLE,
                ],
            },
        },
        "friday": {
            "day": {
                "length_of_list": 6,
                "primary_stadium": ONDERZOEK_BUITENDIENST,
                "secondary_stadia": [TWEEDE_CONTROLE, DERDE_CONTROLE],
            },
            "evening": {
                "length_of_list": 6,
                "primary_stadium": AVONDRONDE,
                "secondary_stadia": [
                    HERCONTROLE,
                    TWEEDE_HERCONTROLE,
                    DERDE_HERCONTROLE,
                ],
            },
        },
        "saturday": {
            "day": {
                "length_of_list": 6,
                "primary_stadium": WEEKEND_BUITENDIENST_ONDERZOEK,
                "secondary_stadia": [
                    HERCONTROLE,
                    TWEEDE_HERCONTROLE,
                    DERDE_HERCONTROLE,
                ],
            }
        },
        "sunday": {
            "day": {
                "length_of_list": 6,
                "primary_stadium": WEEKEND_BUITENDIENST_ONDERZOEK,
                "secondary_stadia": [
                    HERCONTROLE,
                    TWEEDE_HERCONTROLE,
                    DERDE_HERCONTROLE,
                ],
            }
        },
    },
}
