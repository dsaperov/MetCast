import itertools
import re
import requests
from bs4 import BeautifulSoup


class WeatherParser:

    def __init__(self):
        self.dates = []
        self.weather_data = []
        self.temperature_data = []

    def parse(self, city, days_number):
        url = f'https://pogoda.mail.ru/prognoz/{city}/14dney/'
        response = requests.get(url)

        if response.status_code == 404:
            return None

        soup = BeautifulSoup(response.text, features='html.parser')
        tags_with_date = soup.find_all('div', {'class': ["heading heading_minor heading_line",
                                                         "heading heading_minor heading_line text-red"]})
        self.extract_date(tags_with_date, days_number)

        tags_with_weather_and_temperature = soup.find_all('div', {'class': "day__date"}, string='Днем')
        self.extract_weather_and_temperature(tags_with_weather_and_temperature, days_number)

        forecast = zip(self.dates, self.weather_data, self.temperature_data)
        return forecast

    def extract_date(self, tags, days_number):
        for date_div_tag in itertools.islice(tags, days_number):
            date_div_tag.span.decompose()
            date_in_str = re.search(r'\d{1,2}\s[а-я]+', date_div_tag.text).group()
            self.dates.append(date_in_str)

    def extract_weather_and_temperature(self, tags, days_number):
        for day__date_div_tag in itertools.islice(tags, days_number):
            day_period_div_tag = day__date_div_tag.parent
            weather = day_period_div_tag.find('span', {'title': True}).text
            temperature = day_period_div_tag.find('div', {'class': 'day__temperature'}).text
            self.weather_data.append(weather)
            self.temperature_data.append(temperature)
