# Metcast
Консольная программа `Metcast` написана в рамках финального задания курса Python-разработчик от Skillbox. Программа,
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

Для пользователей ОС Windows доступно формирование прогноза без необходимости ввода данных при каждом запуске программы.
Для этого необходимо:
1. В файле `customization/config.json` ввести значения для ключа `"preferences"`:
 - `"days"` - количество дней, на которое нужно получить прогноз. По умолчанию - `"3"`.
 - `"city"` - город, для которого нужно получить прогноз. По умолчанию - `"moskva"`.
2. В файле `MetCast.bat` присвоить значения переменным:
 - `"path_to_venv"` - пусть к виртуальному окружению проекта.
 - `"path_to_project"` - путь к проекту.
3. Запустить файл `MetCast.bat`. 

Таким образом, при каждом запуске программы через `MetCast.bat` на консоль будет выводиться прогноз погоды на указанное 
количество дней.

Блок-схема алгоритма, использующегося в работе программы, приведена в файлах папки `Algorithm` (различными цветами
отмечены компоненты, за выполнение которых в программе отвечают отдельные классы).