import sys
from datetime import date
import json

from database import Forecast

with open("customization/config.json", "r") as read_file:
    config = json.load(read_file)

preferences = config['preferences']
scenarios = config['scenarios']

forecast_from_db = Forecast.select().where(Forecast.city == preferences['city'], Forecast.date >= date.today())

if forecast_from_db.exists():
    user_input = scenarios["forecast_in_db"]
else:
    user_input = scenarios["no_forecast_in_db"]

for preference, value in preferences.items():
    i = user_input.index(preference)
    user_input[i] = value

sys.stdout.write('\n'.join(user_input))
