import json
from datetime import date

import peewee


class DatabaseUpdater:

    @staticmethod
    def update(forecasts, day_periods, data_processor, city):
        day_periods_instance = DayPeriodsPattern(content=json.dumps(day_periods)).save()
        records = []
        for date_non_formatted, sky_clarity, temperature, feels_like in forecasts:
            date_formatted = data_processor.format_date(date_non_formatted)
            record = {'city': city, 'date': date_formatted, 'sky_clarity': json.dumps(sky_clarity),
                      'temperature': json.dumps(temperature), 'feels_like': json.dumps(feels_like),
                      'day_periods': day_periods_instance}
            records.append(record)
            Forecast.insert_many(records).on_conflict_replace(True).execute()


database = peewee.SqliteDatabase("forecasts.db")


class BaseTable(peewee.Model):

    class Meta:
        database = database


class DayPeriodsPattern(BaseTable):
    content = peewee.CharField()

    class Meta:
        order_by = 'id'
        db_table = 'day_periods_patterns'


class Forecast(BaseTable):
    city = peewee.CharField()
    date = peewee.DateField(unique=True)
    sky_clarity = peewee.CharField()
    temperature = peewee.CharField()
    feels_like = peewee.CharField()
    day_periods = peewee.ForeignKeyField(DayPeriodsPattern)

    class Meta:
        order_by = date
        db_table = 'forecasts'


database.create_tables([Forecast, DayPeriodsPattern])
