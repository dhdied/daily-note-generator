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
productivity: 
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

> [!chart]+ Сон и продуктивность
> ```dataviewjs
> const pages = dv.pages("#daily")
>     .filter(p => p.date <= dv.current().date && p.date > dv.current().date.minus({{ days: 7 }}))
>     .sort(p => p.date);
>
> const dates = pages.map(p => p.date.toFormat("dd.MM")).array();
> const sleepData = pages.map(p => p.sleep_hours || 0).array();
> const productivityData = pages.map(p => p.productivity || 0).array();
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
>                 label: 'Продуктивность (1-10)',
>                 data: productivityData,
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

> [!info]- Год в цветах
> ```dataviewjs
> const DateTime = dv.luxon.DateTime;
> const colors = {{
>      10: "#D0BCFC", 9: "#B796FE", 8: "#A981FF", 7: "#7B45F0",
>      6: "#6631DB", 5: "#491AB1", 4: "#34117E", 3: "#221932",
>      2: "#060407", 1: "#060407"
> }};
>
> const legendItems = [
>      {{ c: "#D0BCFC", t: "Отлично" }},
>      {{ c: "#7B45F0", t: "Хорошо" }},
>     {{ c: "#491AB1", t: "Нормально" }},
>      {{ c: "#221932", t: "Плохо" }},
>      {{ c: "#060407", t: "Ужасно" }}
> ];
>
> const months = ["Я", "Ф", "М", "А", "М", "И", "И", "А", "С", "О", "Н", "Д"];
> const currentYear = new Date().getFullYear();
> const pages = dv.pages("#daily").where(p => {{
>      if (!p.date) return false;
>      const d = DateTime.fromISO(p.date.toString());
>      return d.year === currentYear;
> }});
>
> let html = "<div style='display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px; justify-content: center;'>";
> for (let item of legendItems) {{
>      html += `<div style='display: flex; align-items: center; gap: 4px;'>
>          <div style='width: 10px; height: 10px; border-radius: 2px; background-color: ${{item.c}}; border: 1px solid var(--background-modifier-border);'></div>
>          <span style='font-size: 0.7em; color: var(--text-muted);'>${{item.t}}</span>
>      </div>`;
> }}
> html += "</div>";
>
> html += "<div style='display: flex; justify-content: center; overflow-x: auto;'>";
> html += "<table style='border-spacing: 0; border-collapse: collapse; border: none; line-height: 0;'>";
> html += "<tr><th style='border: none;'></th>";
> for(let m of months) {{
>      html += `<th style='font-size: 0.7em; padding: 4px; color: var(--text-muted); font-weight: normal; border: none;'>${{m}}</th>`;
> }}
> html += "</tr>";
> 
> for(let d = 1; d <= 31; d++) {{
>      html += `<tr><td style='font-size: 0.65em; padding-right: 5px; color: var(--text-muted); text-align: right; border: none; line-height: 1;'>${{d}}</td>`;
>      for(let m = 1; m <= 12; m++) {{
>          const dt = DateTime.local(currentYear, m, d);
>          if(!dt.isValid) {{
>              html += `<td style="border: none; padding: 0;"></td>`;
>              continue;
>          }}
>          const dateStr = dt.toISODate();
>          const page = pages.find(p => DateTime.fromISO(p.date.toString()).toISODate() === dateStr);
>          let bgColor = "var(--background-modifier-border)";
>          let opacity = "0.15";
>          if (page && page.mood) {{
>              bgColor = colors[page.mood] || bgColor;
>             opacity = "1";
>          }}
>          html += `<td title="${{dateStr}} | Mood: ${{page?.mood || '?'}}" style="padding: 0; width: 16px; height: 16px; background-color: ${{bgColor}}; opacity: ${{opacity}}; border: 1px solid var(--background-primary); box-sizing: border-box;"></td>`;
>      }}
>      html += "</tr>";
> }}
> html += "</table></div>";
> dv.paragraph(html);
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