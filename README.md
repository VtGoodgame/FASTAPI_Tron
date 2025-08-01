<!--
  ╔════╗ ╔═══╗ ╔═══╗   ╔════╗       🚀 FASTAPI_Tron
  ║    ║ ║   ║ ║   ║   ║    ║       🔗 Интеграция с Tron API
  ╠══╦═╝ ║ ═╦╝ ║ ═╦╝   ║ ═╦═╝
  ║  ╚╗  ║  ║  ║  ║    ║  ║         💡 FastAPI • Docker • Redis
  ╚═══╝  ╚══╝  ╚══╝    ╚══╝
-->

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.116-green?style=for-the-badge&logo=fastapi"/>
  <img src="https://img.shields.io/badge/Tron-Protocol-blue?style=for-the-badge&logo=tron"/>
  <img src="https://img.shields.io/badge/Redis-database-red?style=for-the-badge&logo=redis&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-container-2496ED?style=for-the-badge&logo=docker"/>
</p>

# 🚀 FASTAPI_Tron | Интеграция с API Tron

> 📌 Тестовое задание: получение и кэширование данных о кошельках Tron с использованием FastAPI, PostgreSQL, Redis и Docker.

---

## 📌 Описание

Проект представляет собой REST API на **FastAPI**, который:
- Валидирует адреса Tron.
- Получает информацию о ресурсах аккаунта через внешнее API.
- Кэширует данные в **Redis** для ускорения повторных запросов.
- Сохраняет историю запросов в **PostgreSQL**.
- Поддерживает пагинацию и автоматическое развертывание через **Docker**.

---

## 🔐 Конфигурация (`.env`)

Перед запуском создайте файл `.env` в корне проекта с переменными окружения:

```env
# === База данных (PostgreSQL) ===
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database_name

# === Redis (кэширование) ===
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# === Tron API ===
CHECK_ADDRESS=https://api.trongrid.io/wallet/validateaddress
CHECK_ACCAUNT=https://api.trongrid.io/wallet/getaccount
PREFIX=/api/v03

# === Опционально: токен для расширенных запросов ===
TRON_API_TOKEN=your_token_here 

 === ⚠️ На данный момент TronGrid не требует токен для базовых запросов, но в будущем он может понадобиться. === 
```

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

##Запуск Тестов

**1. Перейти в папку проекта**
```bash
cd .\FASTAPI_Tron\
```  
**Запустить тесты с подробным выводом**
```bash
pytest --v
```
**Только тесты эндпоинтов**
```bash
pytest tests/test_endpoint_moking.py
```

## 🐳 Запуск в Docker

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

**Остановить и удалить (по завершении)**
  ```bash
 docker stop Tron_Api-container
 docker rm Tron_Api-container
 docker rmi Tron_Api-app
```

<p align="center"><i>Спасибо за использование моего проекта!</i></p>
