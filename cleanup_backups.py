import os
import time
import logging
from dotenv import load_dotenv


load_dotenv()

BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
DAYS_TO_KEEP = 7

LOG_FILE = os.path.join(BACKUP_DIR, "cleanup.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def cleanup_old_backups():
    now = time.time()
    cutoff = now - (DAYS_TO_KEEP * 86400)  # 7 дней в секундах

    if not os.path.exists(BACKUP_DIR):
        logging.warning(f"Директория {BACKUP_DIR} не существует.")
        return

    deleted_files = 0
    for filename in os.listdir(BACKUP_DIR):
        file_path = os.path.join(BACKUP_DIR, filename)
        if os.path.isfile(file_path) and filename.endswith(".dump"):
            file_mtime = os.path.getmtime(file_path)
            if file_mtime < cutoff:
                try:
                    os.remove(file_path)
                    deleted_files += 1
                    logging.info(f"Удалён старый бэкап: {filename}")
                except Exception as e:
                    logging.error(f"Не удалось удалить {filename}: {e}")

    logging.info(f"Очистка завершена. Удалено файлов: {deleted_files}")

if __name__ == "__main__":
    cleanup_old_backups()
