FROM python:3.12-slim AS builder
WORKDIR /tmp
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip download --no-binary=:all: -r requirements.txt   # (opcional, cache)

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000
