import os
import re
import unicodedata
from datetime import datetime, timezone
from sqlalchemy import create_engine
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, DB_HOST, LOG_PATH

def log(message, level="INFO", echo=False):
    """
    Write a timestamped message to the log file and optionally print it.

    Args:
        message (str): Text to be logged.
        echo (bool): If True, also print the message to the console.
    """

    timestamp = datetime.now(timezone.utc)

    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f'{timestamp} UTC: [{level}] {message}\n')

    if echo is True:
        print(f'{timestamp} UTC: [{level}] {message}\n')

def clear_screen():
    """
        Clears CLI window
    """
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def connect_to_database():
    """
    Creates and returns SQLAlchemy engine for database connection
    """
    connection_string = (
        f"postgresql://{DB_USER}:{DB_PASSWORD or ''}@"
        f"{DB_HOST}:{DB_PORT or '5432'}/{DB_NAME}"
    )
    engine = create_engine(connection_string)
    return engine

def clean_img_name(name):
    """
    Cleans string from any special characters replacing them with '_' 
    to avoid file name conflict when saving an img
    """
    result = unicodedata.normalize('NFKD', name)
    result = result.encode('ascii', 'ignore').decode('ascii')
    result = re.sub(r'[^a-zA-Z0-9]', '_', result)
    return result
