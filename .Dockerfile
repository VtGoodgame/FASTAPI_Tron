FROM python:3.12

WORKDIR /FASTAPI_Tron

ENV REDIS_HOST=""
ENV REDIS_PORT=""
ENV REDIS_USERNAME=""
# The password is set in the .env file, but you can also set it here if you prefer
# If you set it here, make sure to keep it secure and not expose it in public
ENV REDIS_PASSWORD=""

#db
ENV DB_URL =""

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
