<!--
  ╔════╗ ╔═══╗ ╔═══╗   ╔════╗       🚀 FASTAPI_Tron
  ║    ║ ║   ║ ║   ║   ║    ║       🔗 Интеграция с Tron API
  ╠══╦═╝ ║ ═╦╝ ║ ═╦╝   ║ ═╦═╝
  ║  ╚╗  ║  ║  ║  ║    ║  ║         💡 FastAPI • Docker • Redis
  ╚═══╝  ╚══╝  ╚══╝    ╚══╝
-->

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100-green?style=for-the-badge&logo=fastapi"/>
  <img src="https://img.shields.io/badge/Tron-Protocol-blue?style=for-the-badge&logo=tron"/>
  <img src="https://img.shields.io/badge/Redis-database-red?style=for-the-badge&logo=redis&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-container-2496ED?style=for-the-badge&logo=docker"/>
</p>

# 🚀 Тестовое задание Tron | FastAPI

## Описание
## 📝 Конфигурация проекта

Для взаимодействия с API Tron используется авторизационный токен, который хранится в файле `.env`.  
На текущую дату **(30.07.25)** токен **не обязателен** для базовых запросов, но предусмотрен на будущее.

### 🔐 Перед запуском добавьте переменные в `.env` файл:

```env
# === База данных (PostgreSQL / MySQL) ===
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database_name

# === Redis (кэширование) ===
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_USERNAME=default
REDIS_PASSWORD=your_redis_password

# === Tron API (опционально) ===
TRON_API_TOKEN=your_token_here
В приложении он считывается с помощью функции `os.getenv` в файле констант (`consts.py`) и далее используется в основном модуле проекта.
### Инструкция по запуску

## Установка (Windows)
**1.Клонирование репозитория**
 ```bash
 git clone https://github.com/VtGoodgame/FASTAPI_Tron.git
 ```
**2.Переход в директорию `FASTAPI_Tron`**
 ```bash
 cd FASTAPI_Tron/
```
**3.Создание виртуального окружения**
 ```bash
python -m venv venv
```
**4.Активировать виртуальное окружение**
 ```bash
 .\venv\Scripts\activate
```
**5.Установить зависимости из файла `requirements.txt`**
 ```bash
pip install -r requirements.txt
```
**6.Запуск сервера осуществляется с помощью команды**
 ```bash
 uvicorn main:app --reload
```
**Сервер будет доступен по адресу: http://127.0.0.1:8000
  Документация API: http://127.0.0.1:8000/docs**

**Запуск Тестов**
```bash
pytest
```

## Для создания и сборки Docker контейнера 

**1.Переход в директорию `FASTAPI_Tron`**
 ```bash
 cd FASTAPI_Tron/
```
**2.Создать образ докер контейнера с помощью команды**
 ```bash
 docker build -t Tron_Api-app .
```
**3.Выполнить сборку контейнера**
 ```bash
 docker run -d -p 8000:8000 --name Tron_Api-container Tron_Api-app
```
**4.Проверка запущенных контейнеров**
 ```bash
 docker ps
```

_После проверки работоспособности следует выполнить команды_

**1.Остановка работы контейнера**
  ```bash
 docker stop Tron_Api-container
```
**2.Удаление контейнера**
 ```bash
 docker rm Tron_Api-container
```
**3.Удаление образа**
 ```bash
 docker rmi Tron_Api-app
```

<p align="center"><i>Спасибо за использование моего проекта!</i></p>
