import aiohttp
import asyncio
import logging
from config import WEATHER_API_KEY, CITY_LAT, CITY_LON

async def get_weather(session: aiohttp.ClientSession) -> str:
    '''
    Асинхронный запрос погоды (OpenWeather)
    '''
    if not WEATHER_API_KEY:
        return "Нет ключа API"
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": CITY_LAT, "lon": CITY_LON,
        "appid": WEATHER_API_KEY, "units": "metric", "lang": "ru"
    }

    try:
        async with session.get(url, params=params, timeout=7) as response:
            if response.status == 200:
                data = await response.json()
                city = data["name"]
                temp = round(data["main"]["temp"])
                desc = data["weather"][0]["description"]
                temp_str = f"+{temp}" if temp > 0 else str(temp)
                return f"{city} | {temp_str}°C, {desc}"
            return "Ошибка погоды (status != 200)"
    except Exception as e:
        logging.error(f"Ошибка погоды: {e}")
        return "Погода недоступна"
    
async def get_quote(session: aiohttp.ClientSession) -> str:
    '''
    Ассинхронный запрос цитаты (ZenQuotes)
    '''
    url = "https://zenquotes.io/api/random"
    try:
        async with session.get(url, timeout=7) as response:
            data = await response.json()
            return f'"{data[0]["q"]}" - {data[0]["a"]}'
    except Exception:
        return "Сегодня без цитаты :D"
    
async def get_exchange_rates(session: aiohttp.ClientSession) -> str:
    '''
    Асинхронный запрос курсов валют (ЦБ РФ)
    '''
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        async with session.get(url, timeout=7) as response:
            # Добавляем content_type=None, чтобы отключить строгую проверку типа
            data = await response.json(content_type=None)
            
            usd = round(data["Valute"]["USD"]["Value"], 2)
            eur = round(data["Valute"]["EUR"]["Value"], 2)
            return f"USD: {usd} ₽ | EUR: {eur} ₽"
    except Exception as e:
        logging.error(f'Ошибка получения курсов валют: {e}')
        return "Курсы валют недоступны"