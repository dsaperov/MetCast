"""
Консольная программа Metcast написана в рамках финального задания курса Python-разработчик от Skillbox. Программа,
используя парсинг сайта pogoda.mail.ru, получает данные о погоде по выбранному пользователем городу за выбранный
диапазон дат (от 1 до 14 дней). Согласно условиям задания, прогноз сначала сохраняется в базу данных (для этого при
первой генерации прогноза создается файл "forecasts.db"), после чего может быть оттуда извлечен и выведен в одной из
двух форм:
- Прогноз на первый день может быть выведен в форме открытки, внешний вид которой варьируется в зависимости от погодных
условий: "осадки" --> синий цвет фона и картинка с тучей, "ясно" --> желтый цвет фона и картинка с солнцем и т.д.
- Целиком прогноз может быть выведен на консоль в формате "{дата} - {тип погоды], {температура}".

Согласно условиям задания, пользователю должны быть доступны следующие команды:
- Добавление прогнозов за диапазон дат в базу данных
- Получение прогнозов за диапазон дат из базы
- Создание открытки из полученного прогноза
- Выведение полученного прогноза на консоль

Блок-схема алгоритма, использующегося в работе программы, приведена в файлах папки "Algorithm" (различными цветами
отмечены компоненты, за выполнение которых в программе отвечают отдельные классы).
"""

from datetime import date
import sys
import requests

from transliterate import translit
from transliterate.exceptions import LanguageDetectionError

from config import AMBIGUOUS_CITIES_NAMES, DAYS_DECLENSIONS, MONTHS
from database import Forecast, DatabaseUpdater
from image_maker import ImageMaker
from weather_parser import WeatherParser


class DataProcessor:

    def validate_days_number(self, number):
        if not number.isdigit() or int(number) > 14 or int(number) < 1:
            print('Введите число от 1 до 14')
            number = self.validate_days_number(input())
        return int(number)

    @staticmethod
    def transliterate_city(city):
        if city in AMBIGUOUS_CITIES_NAMES:
            city_transliterated = AMBIGUOUS_CITIES_NAMES[city]
        else:
            try:
                city_transliterated = translit(city, 'ru', reversed=True).lower()
            except LanguageDetectionError:
                return False

        if '-' in city_transliterated:
            city_transliterated = city_transliterated.replace('-', '_')
        return city_transliterated

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
        forecast_from_db = Forecast.select().where(Forecast.city == self.city, Forecast.date >= date.today())

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
        self.database_updater.update(forecast, self.data_processor, self.city)
        print('Прогноз сформирован и загружен в базу')
        self.forecast_from_db_up_to_date = False

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
            print('К сожалению город с таким названием не найден.'
                  ' Для продолжения введите название города на транслите.')
            forecast = self.get_forecast_from_service(input())

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
            self.forecast_from_db = Forecast.select().where(Forecast.city == self.city, Forecast.date >= date.today())
            self.forecast_from_db_up_to_date = True
            self.print_forecast_received_from_db_message()
        elif selected_action == self.ACTIONS[2]:
            self.image_maker.make_postcard(self.forecast_from_db)
            self.postcard_made = True
        elif selected_action == self.ACTIONS[3]:
            for record in self.forecast_from_db:
                print(f'{record.date} - {record.weather}, температура {record.temperature}')
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
