from datetime import date

import peewee


class DatabaseUpdater:

    @staticmethod
    def update(forecasts, data_processor, city):
        records = []
        for date_non_formatted, weather, temperature in forecasts:
            date_formatted = data_processor.format_date(date_non_formatted)
            record = {'city': city, 'date': date_formatted, 'weather': weather,
                      'temperature': temperature}
            records.append(record)
            Forecast.insert_many(records).on_conflict_replace(True).execute()


database = peewee.SqliteDatabase("forecasts.db")


class Forecast(peewee.Model):
    city = peewee.CharField()
    date = peewee.DateField(unique=True)
    weather = peewee.CharField()
    temperature = peewee.IntegerField()

    class Meta:
        database = database
        order_by = date
        db_table = 'forecasts'


Forecast.create_table()
