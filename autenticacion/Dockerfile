# production-ready Dockerfile for autenticacion microservice
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

RUN python manage.py collectstatic --noinput || true

ENTRYPOINT ["/app/entrypoint.sh"]