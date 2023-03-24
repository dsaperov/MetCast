import json
import locale
import string
from datetime import date
import sys
import requests

from transliterate import translit
from transliterate.exceptions import LanguageDetectionError

from config import AMBIGUOUS_CITIES_NAMES, DAYS_DECLENSIONS, MONTHS
from database import Forecast, DatabaseUpdater, DayPeriodsPattern
from image_maker import ImageMaker
from weather_parser import WeatherParser


class DataProcessor:

    def validate_days_number(self, number):
        if not number.isdigit() or int(number) > 14 or int(number) < 1:
            print('Введите число от 1 до 14')
            number = self.validate_days_number(input())
        return int(number)

    def transliterate_city(self, city):
        if city in AMBIGUOUS_CITIES_NAMES:
            city_transliterated = AMBIGUOUS_CITIES_NAMES[city]
        else:
            try:
                city_transliterated = translit(city, 'ru', reversed=True).lower()
            except LanguageDetectionError:
                return False
        return self.substitute_dashes_with_underscores(city_transliterated)

    @staticmethod
    def substitute_dashes_with_underscores(word):
        if '-' in word:
            return word.replace('-', '_')
        return word

    @staticmethod
    def city_is_transliterated(city):
        for char in city:
            if char not in string.ascii_letters:
                return False
        return True

    @staticmethod
    def format_date(date_in_str):
        date_splitted = date_in_str.split(' ')
        day = date_splitted[0]
        month = MONTHS[date_splitted[1]]
        year = date.today().year
        date_formatted = str(year) + '-' + month + '-' + day
        return date_formatted


class ForecastMaker:
    ACTIONS = ['Добавить новый прогноз в базу данных',
               'Получить сформированный прогноз из базы данных',
               'Создать открытку c погодой на сегодня из полученного прогноза',
               'Вывести полученный прогноз на консоль',
               'Завершить работу программы']

    def __init__(self, data_processor, weather_parser, database_updater, image_maker):
        self.data_processor = data_processor
        self.weather_parser = weather_parser
        self.database_updater = database_updater
        self.image_maker = image_maker

        self.city = None
        self.forecast_from_db = None

        self.forecast_from_db_up_to_date = False
        self.postcard_made = False
        self.program_finished = False

    def run(self):
        print('Для проверки наличия в базе данных актуальных прогнозов введите название города')
        self.set_city(input())
        forecast_from_db = self.get_forecast_from_db()

        if forecast_from_db.exists():
            self.forecast_from_db = forecast_from_db
            self.forecast_from_db_up_to_date = True
            self.print_forecast_received_from_db_message()
        else:
            print('Актуальный прогноз по вашему городу в базе данных не обнаружен')
            self.add_forecast_to_db()

        while not self.program_finished:
            actions_enumerated = self.get_actions_enumerated()
            self.print_actions(actions_enumerated)
            self.handle_choice(input(), actions_enumerated)

        print('Работа программы завершена')

    def set_city(self, city):
        city_transliterated = self.data_processor.transliterate_city(city.lower())
        if city_transliterated:
            self.city = city_transliterated
        else:
            print('Введите название города на русском языке.')
            self.set_city(input())

    def print_forecast_received_from_db_message(self):
        days_number = len(self.forecast_from_db)
        days_declension = DAYS_DECLENSIONS.get(days_number, 'дней')
        print(f'Прогноз по вашему городу за {days_number} {days_declension} получен из базы данных')

    def add_forecast_to_db(self):
        forecast = self.make_forecast()
        self.database_updater.update(forecast, self.weather_parser.day_periods, self.data_processor, self.city)
        print('Прогноз сформирован и загружен в базу')
        self.forecast_from_db_up_to_date = False

    def get_forecast_from_db(self):
        return Forecast.select(Forecast, DayPeriodsPattern).join(DayPeriodsPattern).where(Forecast.city == self.city,
                                                                                          Forecast.date >= date.today())

    def make_forecast(self):
        print('На сколько дней необходимо сформировать прогноз? Введите число от 1 до 14.')
        days_number = self.data_processor.validate_days_number(number=input())
        forecast_from_service = self.get_forecast_from_service(days_number)
        return forecast_from_service

    def get_forecast_from_service(self, days_number):
        try:
            forecast = self.weather_parser.parse(self.city, days_number)
        except requests.exceptions.ConnectionError:
            print('Не удалось установить соединение с сайтом. Попробуйте еще раз позже.')
            sys.exit()

        if not forecast:
            print('К сожалению, город с таким названием не найден.'
                  ' Для продолжения введите название города на транслите.')
            self.city = input()
            forecast = self.get_forecast_from_service(days_number)

        return forecast

    def get_actions_enumerated(self):
        available_actions = self.ACTIONS[:-1].copy()

        if not self.forecast_from_db:
            for action_number in (2, 3):
                available_actions.remove(self.ACTIONS[action_number])
        if self.forecast_from_db_up_to_date:
            available_actions.remove(self.ACTIONS[1])
        if self.postcard_made:
            for action_number in (0, 2):
                available_actions.remove(self.ACTIONS[action_number])
            available_actions.append(self.ACTIONS[-1])

        actions_enumerated = {number: action for number, action in enumerate(available_actions, 1)}
        return actions_enumerated

    @staticmethod
    def print_actions(actions):
        print('Выберите следующее действие')
        for number, option in actions.items():
            print(f'{number}. {option}')

    def handle_choice(self, selected_number, actions_enumerated):
        selected_action = self.get_selected_action(selected_number, actions_enumerated)

        if selected_action == self.ACTIONS[0]:
            self.add_forecast_to_db()
        elif selected_action == self.ACTIONS[1]:
            self.forecast_from_db = self.get_forecast_from_db()
            self.forecast_from_db_up_to_date = True
            self.print_forecast_received_from_db_message()
        elif selected_action == self.ACTIONS[2]:
            self.image_maker.make_postcard(self.forecast_from_db)
            self.postcard_made = True
        elif selected_action == self.ACTIONS[3]:
            day_periods = json.loads(self.forecast_from_db[0].day_periods.content)
            day_periods_number = len(day_periods)
            for record in self.forecast_from_db:
                sky_clarity = json.loads(record.sky_clarity)
                temperature = json.loads(record.temperature)
                feels_like = json.loads(record.feels_like)
                locale.setlocale(locale.LC_TIME, 'ru_Ru')
                print(record.date.strftime('%d-%m-%Y, %A'))
                for i in range(day_periods_number):
                    print(day_periods[i].capitalize() + ' - ' + sky_clarity[i] + ', температура '
                          + temperature[i] + ', ощущается, как ' + feels_like[i])
                print()
            self.program_finished = True
        else:
            self.program_finished = True

    def get_selected_action(self, selected_number, actions_enumerated):
        try:
            selected_action = actions_enumerated[int(selected_number)]
        except (ValueError, KeyError) as exc:
            if exc.__class__.__name__ == 'ValueError':
                print('--- Нужно выбрать число ---')
            else:
                print('--- Выбрано число не из списка ---')
            selected_number = input()
            selected_action = self.get_selected_action(selected_number, actions_enumerated)
        return selected_action


if __name__ == '__main__':
    ForecastMaker(DataProcessor(), WeatherParser(), DatabaseUpdater(), ImageMaker()).run()
