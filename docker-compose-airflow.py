version: '3'
x-airflow-common:
  &airflow-common
  image: apache/airflow:2.9.3
  environment:
    &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: CeleryExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    AIRFLOW__CORE__FERNET_KEY: 'YTz8VL3x4v2djMq_hpLAlCKZl77GT8CIXtjp1c2XhTY='
    AIRFLOW__CORE__LOAD_EXAMPLES: 'true'
    POSTGRES_USER: airflow
    POSTGRES_PASSWORD: airflow
    POSTGRES_DB: airflow
  volumes:
    - ./dags:/opt/airflow/dags
    - ./plugins:/opt/airflow/plugins
  depends_on:
    - postgres

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 30s
      retries: 5

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "8080:8080"
    depends_on:
      - "airflow-init"

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler
    depends_on:
      - airflow-init
      - postgres
      - redis

  airflow-worker:
    <<: *airflow-common
    command: celery worker
    depends_on:
      - airflow-scheduler
      - redis

  airflow-init:
    <<: *airflow-common
    entrypoint: /bin/bash
    tty: true
    command:
      - -c
      - |
        airflow db init && \
        airflow users create \
          --username admin \
          --firstname Admin \
          --lastname Admin \
          --role Admin \
          --email admin@example.com \
          --password admin123