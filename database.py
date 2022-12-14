import json
from datetime import date

import peewee


class DatabaseUpdater:

    @staticmethod
    def update(forecasts, data_processor, city):
        records = []
        for date_non_formatted, sky_clarity, temperature, feels_like in forecasts:
            date_formatted = data_processor.format_date(date_non_formatted)
            record = {'city': city, 'date': date_formatted, 'sky_clarity': json.dumps(sky_clarity),
                      'temperature': json.dumps(temperature), 'feels_like': json.dumps(feels_like)}
            records.append(record)
            Forecast.insert_many(records).on_conflict_replace(True).execute()


database = peewee.SqliteDatabase("forecasts.db")


class Forecast(peewee.Model):
    city = peewee.CharField()
    date = peewee.DateField(unique=True)
    sky_clarity = peewee.CharField()
    temperature = peewee.CharField()
    feels_like = peewee.CharField()

    class Meta:
        database = database
        order_by = date
        db_table = 'forecasts'


Forecast.create_table()
