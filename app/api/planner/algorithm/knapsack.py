import multiprocessing
import logging
from joblib import Parallel, delayed
from api.cases.const import ISSUEMELDING
from api.planner.utils import calculate_geo_distances, remove_cases_from_list
from api.planner.algorithm.base import ItineraryGenerateAlgorithm
from utils.queries import get_case

LOGGER = logging.getLogger(__name__)

class Weights():
    '''
    A configurable weight object which is used in our scoring function
    '''

    def __init__(self,
                 distance=1,
                 fraud_prediction=0.75,
                 primary_stadium=0.75,
                 secondary_stadium=0.5,
                 issuemelding=1):

        self.distance = distance
        self.fraud_prediction = fraud_prediction
        self.primary_stadium = primary_stadium
        self.secondary_stadium = secondary_stadium
        self.issuemelding = issuemelding

    def score(self,
              distance,
              fraud_prediction,
              primary_stadium,
              secondary_stadium,
              issuemelding):

        values = [distance, fraud_prediction, primary_stadium, secondary_stadium, issuemelding]
        weights = [self.distance, self.fraud_prediction,
                   self.primary_stadium, self.secondary_stadium, self.issuemelding]

        products = [value*weight for value, weight in zip(values, weights)]
        return sum(products)

    def __str__(self):
        settings = {
            'distance': self.distance,
            'fraud_prediction': self.fraud_prediction,
            'primary_stadium': self.primary_stadium,
            'secondary_stadium': self.secondary_stadium,
            'issuemelding': self.issuemelding
        }
        return str(settings)


class ItineraryKnapsackSuggestions(ItineraryGenerateAlgorithm):
    def __init__(self, settings, settings_weights=None):
        super().__init__(settings)

        self.weights = Weights()

        if settings_weights:
            self.weights = Weights(
                distance=settings_weights.distance,
                fraud_prediction=settings_weights.fraud_prediction,
                primary_stadium=settings_weights.primary_stadium,
                secondary_stadium=settings_weights.secondary_stadium,
                issuemelding=settings_weights.issuemelding)

    def get_score(self, case):
        '''
        Gets the score of the given case
        '''
        distance = case['normalized_inverse_distance']
        fraud_prediction = getattr(case['fraud_prediction'], 'fraud_prediction', False)

        stadium = case['stadium']
        has_primary_stadium = stadium == self.primary_stadium
        has_secondary_stadium = stadium in self.secondary_stadia
        has_issuemelding_stadium = stadium == ISSUEMELDING

        score = self.weights.score(
            distance,
            fraud_prediction,
            has_primary_stadium,
            has_secondary_stadium,
            has_issuemelding_stadium)

        return score

    def get_center(self, location):
        return (location.get('lat'), location.get('lng'))

    def generate(self, location, cases=[], fraud_predictions=[]):
        if not cases:
            cases = self.__get_eligible_cases__()

        if not fraud_predictions:
            fraud_predictions = self.__get_fraud_predictions__()

        # Calculate a list of distances for each case
        center = self.get_center(location)
        distances = calculate_geo_distances(center, cases)
        max_distance = max(distances)

        # Add the distances and fraud predictions to the cases
        for index, case in enumerate(cases):
            case_id = case['case_id']
            case['distance'] = distances[index]
            case['normalized_inverse_distance'] = (max_distance - case['distance']) / max_distance
            case['fraud_prediction'] = fraud_predictions.get(case_id, None)
            case['score'] = self.get_score(case)

        # Sort the cases based on score
        sorted_cases = sorted(cases, key=lambda case: case['score'], reverse=True)

        return sorted_cases


class ItineraryKnapsackList(ItineraryKnapsackSuggestions):

    def get_best_list(self, candidates):
        best_list = max(candidates, key=lambda candidate: candidate.get('score'))
        return best_list['list']

    def parallelized_function(self, case, cases, fraud_predictions, index):
        suggestions = super().generate(case, cases, fraud_predictions)
        suggestions = suggestions[:self.target_length]

        score = sum([case['score'] for case in suggestions])
        return {'score': score, 'list': suggestions}

    def generate(self):
        fraud_predictions = self.__get_fraud_predictions__()

        if self.start_case_id:
            case = get_case(self.start_case_id)
            case['fraud_prediction'] = fraud_predictions.get(self.start_case_id, None)

            suggestions = super().generate(case)
            suggestions = remove_cases_from_list(suggestions, [case])
            suggestions = suggestions[:self.target_length - 1]
            suggestions = [case] + suggestions

            return suggestions

        # If no location is given, generate all possible lists, and choose the best one
        cases = self.__get_eligible_cases__()

        # Run in parallel processes to improve speed
        jobs = multiprocessing.cpu_count()
        candidates = Parallel(n_jobs=jobs, backend='multiprocessing')(delayed(self.parallelized_function)(
            case, cases, fraud_predictions, index) for index, case in enumerate(cases))

        best_list = self.get_best_list(candidates)
        best_list = sorted(best_list, key=lambda case: case['distance'])

        return best_list
