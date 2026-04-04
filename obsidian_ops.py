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