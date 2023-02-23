import sys
from datetime import date
import json

from database import Forecast

SCENARIOS_PATH = 'customization/scenarios.json'
PREFERENCES_PATH = 'customization/preferences.json'


def read_in_utf(file):
    return open(file, mode='r', encoding='utf-8')


with read_in_utf(SCENARIOS_PATH) as scenarios_json, read_in_utf(PREFERENCES_PATH) as preferences_json:
    scenarios = json.load(scenarios_json)
    preferences = json.load(preferences_json)

forecast_from_db = Forecast.select().where(Forecast.city == preferences['city'], Forecast.date >= date.today())

if forecast_from_db.exists():
    user_input = scenarios["forecast_in_db"]
else:
    user_input = scenarios["no_forecast_in_db"]

for preference, value in preferences.items():
    i = user_input.index(preference)
    user_input[i] = value

sys.stdout.write('\n'.join(user_input))
