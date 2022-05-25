from enum import Enum


# Note: currently the weights are defined as an Enum class.
# Eventually we might want to make this configurable through the settings page or admin
class SCORING_WEIGHTS(Enum):
    DISTANCE = 0.25
    FRAUD_PROBABILITY = 1
    PRIORITY = 0.3


MAX_SUGGESTIONS_COUNT = 20
