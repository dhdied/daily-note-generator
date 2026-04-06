import os
import logging
from datetime import datetime
from pathlib import Path
from config import OBSIDIAN_DAILY_DIR

def generate_note_name(date_obj: datetime) -> str:
    '''
    Функция создает название в формате "YYYY-MM-DD"
    '''
    return f"{date_obj.strftime('%Y-%m-%d')}.md"

def save_daily_note(content: str, date_obj: datetime) -> Path:
    '''
    Сохраняет сгенерированный файл в  формате .md в Obsidian
    Возвращает путь к созданному файлу или None в случае ошибки
    '''
    filename = generate_note_name(date_obj)
    filepath = OBSIDIAN_DAILY_DIR / filename

    if not OBSIDIAN_DAILY_DIR.exists():
        logging.warning(f"Папка {OBSIDIAN_DAILY_DIR} не найдена. Создается...")
        OBSIDIAN_DAILY_DIR.mkdir(parents=True, exist_ok=True)

    if filepath.exists():
        logging.warning(f"Заметка {filename} уже существует. Генерация пропущена.")
        return filepath
    
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)

        logging.info(f"Заметка {filepath.name} успешно создана")
        return filepath
    except Exception as e:
        logging.error(f"Ошибка при сохранении файла {filename}: {e}", exc_info=True)
        return None
    
def transfering_tasks(yesterday_obj: datetime) -> str:
    '''
    Построчно читает вчерашнюю заметку и вытаскивает невыполненные задачи,
    используя паттер "конечный автомат"
    '''
    filename = generate_note_name(yesterday_obj)
    filepath = OBSIDIAN_DAILY_DIR / filename

    if not filepath.exists():
        logging.info(f"Вчерашняя заметка {filename} не найдена. Перенос задач пропущен.")
        return ""
    
    unfinished_tasks = []
    is_collecting = False

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                clean_line = line.strip()

                if clean_line.startswith("## 🎯 Задачи на день"):
                    is_collecting = True
                    continue

                if is_collecting:
                    if clean_line == "" or clean_line.startswith("##"):
                        break

                    if clean_line.startswith("- [ ] "):
                        unfinished_tasks.append(clean_line)

        if unfinished_tasks:
            return "\n".join(unfinished_tasks)
        else:
            return ""
        
    except Exception as e:
        logging.error(f"Ошибка при чтении файла {filename}: {e}", exc_info=True)
        return ""