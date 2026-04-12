import requests
import logging
from config import WEATHER_API_KEY, CITY_LAT, CITY_LON

def get_weather() -> str:
    '''
    Запрашивает текущую погоду через OpenWeather API
    Возвращает отформатированную строку или заглушку в случае ошибки
    '''
    if not WEATHER_API_KEY:
        logging.warning("API-ключ для погоды не найден в конфигурации")
        return "Нет ключа API"
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": CITY_LAT,
        "lon": CITY_LON,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()

        city_name = data["name"]
        temp = round(data["main"]["temp"])
        description = data["weather"][0]["description"]

        temp_str = f"+{temp}" if temp > 0 else str(temp)

        result = f"{city_name} | {temp_str}°C, {description}"
        logging.info(f"Погода успешно получена: {result}")
        return result

    except requests.exceptions.Timeout:
        logging.error("Таймаут: сервер погоды не ответил за 5 секунд")
        return "Данные недоступны (Таймаут)"
    except requests.exceptions.RequestException as e:
        logging.error(f'Сетевая ошибка при запуске погоды: {e}')
        return "Данные недоступны (Ошибка сети)"
    except KeyError as e:
        logging.error(f'Ошибка парсинга ответа от сервера погоды: {e}')
        return "Ошибка данных"

def get_quote() -> str:
    '''
    Запрашивает случайную цитату через открытый API ZenQuotes
    '''
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        quote = data[0]["q"]
        author = data[0]["a"]
        
        result = f'"{quote}" — {author}'
        logging.info("Цитата успешно получена.")
        return result
        
    except Exception as e:
        logging.error(f"Ошибка при получении цитаты: {e}")
        return "Сегодняшняя цитата где-то затерялась."

def get_exchange_rates() -> str:
    '''
    Получает актуальные курсы доллара и евро от API ЦБ РФ
    '''
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()

        usd = round(data["Valute"]["USD"]["Value"], 2)
        eur = round(data["Valute"]["EUR"]["Value"], 2)
        
        result = f"USD: {usd} ₽ | EUR: {eur} ₽"
        logging.info(f"Курсы валют получены: {result}")
        return result
        
    except Exception as e:
        logging.error(f"Ошибка при получении курсов валют: {e}")
        return "Данные ЦБ недоступны"