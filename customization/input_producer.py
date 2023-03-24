import sys
from datetime import date
import json

from database import Forecast
from main import DataProcessor

SCENARIOS_PATH = 'customization/scenarios.json'
PREFERENCES_PATH = 'customization/preferences.json'


def read_in_utf(file):
    return open(file, mode='r', encoding='utf-8')


def process_city_to_db_representation(city):
    data_processor = DataProcessor()
    if not data_processor.city_is_transliterated(city):
        return data_processor.transliterate_city(city)
    return data_processor.substitute_dashes_with_underscores(city)


with read_in_utf(SCENARIOS_PATH) as scenarios_json, read_in_utf(PREFERENCES_PATH) as preferences_json:
    scenarios = json.load(scenarios_json)
    preferences = json.load(preferences_json)

city_db_representation = process_city_to_db_representation(preferences['city'])
forecast_from_db = Forecast.select().where(Forecast.city == city_db_representation, Forecast.date >= date.today())

if forecast_from_db.exists():
    user_input = scenarios["forecast_in_db"]
else:
    user_input = scenarios["no_forecast_in_db"]

for preference, value in preferences.items():
    i = user_input.index(preference)
    user_input[i] = value

sys.stdout.write('\n'.join(user_input))
