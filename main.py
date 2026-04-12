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

## 🎯 Задачи на день
{tasks_block}

## 🌇 Рефлексия
### Главное событие дня:
- 

### Что получилось хорошо / Что можно улучшить:
- 
'''
    return template

def main():
    setup_logging()
    logging.info("Запуск генератора ежедневных заметок")

    try:
        # Здесь будет основная логика программы
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        logging.info("Анализ отложенных задач...")
        carried_tasks = transfering_tasks(yesterday)

        if carried_tasks:
            logging.info(f"Найдено задач для переноса:\n{carried_tasks}")

        logging.info("Сбор внешних данных (API)...")
        current_weather = get_weather()
        current_quote = get_quote()
        current_rates = get_exchange_rates()

        logging.info("Сборка базового шаблона...")
        note_content = generate_base_template(today, carried_tasks, current_weather, current_quote, current_rates)

        logging.info("Сохранение файла в Obsidian...")
        saved_path = save_daily_note(note_content, today)

        if saved_path:
            logging.info("Генерация успешно завершена!")
        else:
            logging.warning("Заметка не была сохранена (возможно, уже существует).")
    
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}", exc_info=True)

if __name__ == "__main__":
    main()