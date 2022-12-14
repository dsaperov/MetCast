import itertools
import re
import requests

from bs4 import BeautifulSoup


class WeatherParser:

    def __init__(self):
        self.dates = []
        self.day_periods = []
        self.sky_clarity_data = []
        self.temperature_data = []
        self.feels_like_data = []

    def parse(self, city, days_number):
        url = f'https://pogoda.mail.ru/prognoz/{city}/14dney/'
        response = requests.get(url)

        if response.status_code == 404:
            return None

        soup = BeautifulSoup(response.text, features='html.parser')
        tags_with_date = soup.find_all('span', {'class': ["hdr__inner"]})
        self.extract_date(tags_with_date, days_number)

        tags_with_weather_data = soup.find_all('div', {'class': "p-flex__column p-flex__column_percent-16"})
        self._parse_day_periods(tags_with_weather_data)
        self.extract_weather_data(tags_with_weather_data, days_number)

        forecast = zip(self.dates, self.sky_clarity_data, self.temperature_data, self.feels_like_data)
        return forecast

    def extract_date(self, tags, days_number):
        for date_div_tag in itertools.islice(tags, days_number):
            date_in_str = re.search(r'\d{1,2}\s[а-я]+', date_div_tag.text).group()
            self.dates.append(date_in_str)

    def extract_weather_data(self, tags, days_number):
        tags = iter(tags)
        for _ in range(days_number):
            sky_clarity, temperature, feels_like = ([] for _ in range(3))
            for _ in range(len(self.day_periods)):
                div_for_day_period = next(tags)
                span_tags = div_for_day_period.select('div>span')
                sky_clarity.append(span_tags[3].get_text())
                temperature.append(span_tags[2].get_text())
                feels_like.append(span_tags[4].get_text().split(' ')[-1])

            self.sky_clarity_data.append(sky_clarity)
            self.temperature_data.append(temperature)
            self.feels_like_data.append(feels_like)

    def _parse_day_periods(self, tags):
        for tag in tags:
            day_period = tag.select_one('div>span').get_text()
            if day_period in self.day_periods:
                return
            self.day_periods.append(day_period)
