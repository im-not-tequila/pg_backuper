import os
import subprocess
import datetime
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Bot


os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

LOG_FILE = os.path.join(BACKUP_DIR, "backup.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

async def send_to_telegram(backup_file: str):
    bot = Bot(token=TELEGRAM_TOKEN)
    async with bot:
        with open(backup_file, "rb") as f:
            await bot.send_document(
                chat_id=TELEGRAM_CHAT_ID,
                document=f,
                filename=os.path.basename(backup_file)
            )
    logging.info("Бэкап успешно отправлен в Telegram.")

def create_backup() -> str:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = os.path.join(BACKUP_DIR, f"{DB_NAME}_{timestamp}.dump")

    dump_command = [
        "pg_dump",
        "-U", DB_USER,
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-F", "c",
        "-f", backup_file,
        DB_NAME
    ]

    if os.getenv("PGPASSWORD"):
        os.environ["PGPASSWORD"] = os.getenv("PGPASSWORD")

    logging.info(f"Начало бэкапа базы данных: {DB_NAME}")
    subprocess.run(dump_command, check=True)
    logging.info(f"Бэкап успешно сохранён в: {backup_file}")
    return backup_file

async def main():
    try:
        backup_file = create_backup()
        await send_to_telegram(backup_file)
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка при выполнении pg_dump: {e}")
    except Exception as e:
        logging.exception("Непредвиденная ошибка:")

if __name__ == "__main__":
    asyncio.run(main())
