import cv2
import numpy
from PIL.Image import Image
from PIL import Image, ImageDraw

from config import WEATHER_COLORS


class ImageMaker:
    BLANK_IMAGE_PATH = r'weather_img\probe.jpg'
    WEATHER = {
        'ясно': {
            'first_gradient_color': WEATHER_COLORS['yellow'],
            'image_path': r'weather_img\sun.jpg'
        },
        'дождь/гроза': {
            'first_gradient_color': WEATHER_COLORS['blue'],
            'image_path': r'weather_img\rain.jpg'
        },
        'дождь': {
            'first_gradient_color': WEATHER_COLORS['blue'],
            'image_path': r'weather_img\rain.jpg'
        },
        'снег': {
            'first_gradient_color': WEATHER_COLORS['sky_blue'],
            'image_path': r'weather_img\snow.jpg'},
        'облачно': {
            'first_gradient_color': WEATHER_COLORS['grey'],
            'image_path': r'weather_img\cloud.jpg'
        }
    }

    def make_postcard(self, records):
        records_generator = (record for record in records)

        record = next(records_generator)
        gradient_first_colour = self.WEATHER[record.weather]['first_gradient_color']

        image = self.draw_gradient(gradient_first_colour)
        self.draw_weather_picture(image, record.weather)
        cv_image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)

        text_params = {'first_line': {'x': 50, 'y': 50, 'text': 'TODAY  ' + str(record.date)},
                       'second_line': {'x': 70, 'y': 135, 'text': str(record.temperature[:-1])}}
        for line in text_params:
            image_with_text = self.put_text(cv_image, **text_params[line])

        cv2.imshow('Weather for today', image_with_text)
        print('Окно с открыткой открыто. Чтобы продолжить закройте его.')
        cv2.waitKey(0)

    def draw_gradient(self, first_colour):
        image = Image.open(self.BLANK_IMAGE_PATH)
        draw = ImageDraw.Draw(image)
        r, g, b = first_colour
        dr = (255 - r) / 512.
        dg = (255 - g) / 512.
        db = (255 - b) / 512.

        blank_image_width = image.size[0]
        for i in range(blank_image_width):
            r, g, b = r + dr, g + dg, b + db
            draw.line((i, 0, i, 512), fill=(int(r), int(g), int(b)))

        return image

    def draw_weather_picture(self, image_embracing, weather_type):
        image_to_paste_path = self.WEATHER[weather_type]['image_path']
        image_to_paste = Image.open(image_to_paste_path)

        image_embracing_width = image_embracing.size[0]
        image_embracing_height = image_embracing.size[1]

        image_embracing.paste(image_to_paste, (image_embracing_width * 6 // 11, image_embracing_height * 2 // 6))
        image_embracing.save('postcard.jpg', 'JPEG')

    @staticmethod
    def put_text(cv_image, x, y, text):
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (x, y)
        fontScale = 1.25
        color = (255, 0, 0)
        thickness = 3

        image_with_text = cv2.putText(cv_image, text, org, font, fontScale, color, thickness, cv2.LINE_AA)
        return image_with_text
