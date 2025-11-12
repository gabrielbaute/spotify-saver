FROM python:3.10-alpine

RUN apk add --no-cache ffmpeg

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY . .


RUN pip install --no-cache-dir -r requirements.txt && rm -rf ~/.cache/pip
RUN pip install .

RUN mkdir -p /music

ARG HOST
ENV SPOTIFYSAVER_OUTPUT_DIR="/music" \
  YTDLP_COOKIES_PATH="/config/cookies.txt" \
  SPOTIFYSAVER_AUTO_OPEN_BROWSER="false" \
  SPOTIFYSAVER_API_HOST=${HOST} \
  SPOTIFYSAVER_UI_HOST=${HOST}