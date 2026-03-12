from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# File paths
JSON_PATH = Path(os.getenv('JSON_PATH', str(BASE_DIR / "./data/diet.json")))
LOG_PATH = Path(os.getenv('LOG_PATH', str(BASE_DIR / "./log/log.log")))

# Login data
WEB_USERNAME = os.getenv('WEB_USERNAME')
WEB_PASSWORD = os.getenv('WEB_PASSWORD')
LOGIN_SITE = os.getenv('LOGIN_SITE')
TRAINING_SITE = os.getenv('TRAINING_SITE')

# Data Base
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')