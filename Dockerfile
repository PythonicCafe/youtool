FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED 1
ARG DEV_BUILD
WORKDIR /app

RUN apt update \
  && apt upgrade -y \
  && apt install -y build-essential make python3-dev \
  && apt purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt clean \
  && rm -rf /var/lib/apt/lists/*

COPY requirements/ /app/requirements
RUN pip install --no-cache-dir -U pip \
  && pip install --no-cache-dir -r /app/requirements/base.txt \
  && pip install --no-cache-dir -r /app/requirements/cli.txt \
  && pip install --no-cache-dir -r /app/requirements/livechat.txt \
  && pip install --no-cache-dir -r /app/requirements/transcription.txt \
  && if [ "$DEV_BUILD" = "true" ]; then pip install --no-cache-dir -r /app/requirements/dev.txt; fi

COPY . /app/
