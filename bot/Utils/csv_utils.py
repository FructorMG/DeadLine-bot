import csv
import logging

logger = logging.getLogger("bot")

def read_csv_data(file_path, data_type):
    result = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 2:
                    logger.warning(f"Некорректная строка в CSV: {row}")
                    continue
                fio = row[0].strip()
                if data_type == 'users':
                    username = row[1].strip()
                    result.append(f"{fio}: @{username}")
                elif data_type == 'birthdays':
                    bdate = row[1].strip()
                    result.append(f"{fio}: {bdate}")
    except FileNotFoundError:
        logger.error(f"Файл {file_path} не найден.")
        raise
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {file_path}: {e}")
        raise
    return result
