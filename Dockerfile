FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED 1
ARG DEV_BUILD
WORKDIR /app

RUN apt update \
  && apt upgrade -y \
  && apt install -y build-essential ffmpeg make python3-dev \
  && apt purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt clean \
  && rm -rf /var/lib/apt/lists/*

COPY . /app/

RUN pip install --no-cache-dir -U --upgrade pip \
  && if [ "$DEV_BUILD" = "true" ]; \
  then \
    pip install poetry==1.4.2; \
    poetry export -f requirements.txt --output requirements.txt --without-hashes --with dev; \
    pip install --no-cache-dir -r requirements.txt; \
  else pip install /app; fi
