import asyncio
import sys
import logging
from datetime import datetime, timedelta

from config import LOG_FILE_PATH
from obsidian_ops import save_daily_note, transfering_tasks
from integrations import get_weather, get_quote, get_exchange_rates

RU_WEEKDAYS = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}

def setup_logging():
    '''
    Настраивает логирование проекта.
    Пишет логи в файл и в консоль
    '''
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def generate_base_template(date_obj: datetime, carried_tasks: str = "", weather_info: str = "", quote_info: str = "", rates_info: str = "") -> str:
    '''
    Генерирует базовый шаблон с YAML Frontmatter для Dataview
    '''
    date_iso = date_obj.strftime("%Y-%m-%d")
    weekday_ru = RU_WEEKDAYS[date_obj.weekday()]
    week_number = date_obj.strftime("%V")

    yesterday_obj = date_obj - timedelta(days=1)
    tomorrow_obj = date_obj + timedelta(days=1)

    yesterday_iso = yesterday_obj.strftime("%Y-%m-%d")
    tomorrow_iso = tomorrow_obj.strftime("%Y-%m-%d")

    tasks_block = carried_tasks if carried_tasks else "- [ ] \n- [ ] \n- [ ] "

    template = f'''---
date: {date_iso}
weekday: {weekday_ru}
week_number: {week_number}
mood: 
energy: 
sleep_hours: 
tags: [daily]
---
# 📅 {date_iso} | {weekday_ru}

<< [[{yesterday_iso}|Предыдущий день]] | [[{tomorrow_iso}|Следующий день]] >> 

> *{quote_info}*

## 🌍 Контекст
- **Погода**: {weather_info}
- **Валюта**: {rates_info}

## 📈 Аналитика состояния

> [!chart]+ График сна и энергии (7 дней)
> ```dataviewjs
> const pages = dv.pages("#daily")
>     .filter(p => p.date <= dv.current().date && p.date > dv.current().date.minus({{ days: 7 }}))
>     .sort(p => p.date);
>
> const dates = pages.map(p => p.date.toFormat("dd.MM")).array();
> const sleepData = pages.map(p => p.sleep_hours || 0).array();
> const energyData = pages.map(p => p.energy || 0).array();
>
> const chartData = {{
>     type: 'line',
>     data: {{
>         labels: dates,
>         datasets: [
>             {{
>                 label: 'Сон (часы)',
>                 data: sleepData,
>                 backgroundColor: 'rgba(54, 162, 235, 0.2)',
>                 borderColor: 'rgba(54, 162, 235, 1)',
>                 borderWidth: 2,
>                 fill: true,
>                 tension: 0.3
>             }},
>             {{
>                 label: 'Энергия (1-10)',
>                 data: energyData,
>                 backgroundColor: 'rgba(255, 99, 132, 0.2)',
>                 borderColor: 'rgba(255, 99, 132, 1)',
>                 borderWidth: 2,
>                 fill: true,
>                 tension: 0.3
>             }}
>         ]
>     }},
>     options: {{
>         scales: {{
>             y: {{ beginAtZero: true, max: 12 }}
>         }}
>     }}
> }};
>
> window.renderChart(chartData, this.container);
> ```

> [!info]- Таблица настроения (Месяц)
> ```dataview
> TABLE 
>     mood as "Настроение",
>     energy as "Энергия",
>     sleep_hours as "Сон"
> FROM #daily
> WHERE date <= this.date AND date > this.date - dur(30 days)
> SORT date DESC
> ```

## 🎯 Задачи на день
{tasks_block}

## 🌇 Рефлексия
### Главное событие дня:
- 

### Что получилось хорошо / Что можно улучшить:
- 

### Общие сведения

'''
    return template

async def run_generator():
    '''
    Ассинхронная генерация
    '''
    setup_logging()
    logging.info("Запуск ассинхронного генератора...")

    try:
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        logging.info("Анализ отложенных задач...")
        carried_tasks = transfering_tasks(yesterday)

        logging.info("Параллельный сбор данных из API...")
        import aiohttp
        async with aiohttp.ClientSession() as session:
            weather_task = get_weather(session)
            quote_task = get_quote(session)
            rates_task = get_exchange_rates(session)

            weather, quote, rates = await asyncio.gather(
                weather_task, quote_task, rates_task
            )

        logging.info("Сборка и сохранение заметки...")
        note_content = generate_base_template(today, carried_tasks, weather, quote, rates)
        saved_path = save_daily_note(note_content, today)

        if saved_path:
            logging.info("Генерация успешно завершена!")

    except Exception as e:
        logging.error(f"Критическая ошибка: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(run_generator())