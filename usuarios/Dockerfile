# production-ready Dockerfile for usuarios microservice
FROM python:3.11-slim

# set workdir
WORKDIR /app

# install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . /app

# prepare runtime entrypoint
RUN chmod +x /app/entrypoint.sh

# expose port
EXPOSE 8000

# collect static (if any)
RUN python manage.py collectstatic --noinput || true

# run migrations + optional superuser creation + app startup
ENTRYPOINT ["/app/entrypoint.sh"]
