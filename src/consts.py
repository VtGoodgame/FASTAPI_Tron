from dotenv import load_dotenv
import os

load_dotenv()

#Tests
VALID_ADDRESS=os.getenv("VALID_ADDRESS")
INVALID_ADDRESS=os.getenv("INVALID_ADDRESS")

#Tron
CHECK_ADDRESS=os.getenv("CHECK_ADDRESS")
CHECK_ACCAUNT=os.getenv("CHECK_ACCAUNT")
PREFIX=os.getenv("PREFIX")

#DB

DB_HOST=os.getenv('DB_HOST')
DB_PORT=os.getenv('DB_PORT')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_SCHEMA = os.getenv('DB_SCHEMA')
DB_NAME=os.getenv('DB_NAME')
DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
PREFIX = os.getenv("PREFIX")
