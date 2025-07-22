from dotenv import load_dotenv
import os

load_dotenv()

#Tron
BASE_URL=os.getenv("BASE_URL")
Prefix=os.getenv("Prefix")

#DB
BACKEND_URL = 'localhost:8000'
DB_HOST=os.getenv('DB_HOST')
DB_PORT=os.getenv('DB_PORT')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_SCHEMA = os.getenv('DB_SCHEMA')
DB_NAME=os.getenv('DB_NAME')

COOKIE_NAME = "access_token"

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"