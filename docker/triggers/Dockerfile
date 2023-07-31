FROM python:3.10-slim

WORKDIR /app

COPY ./docker/requirements/triggers.txt requirements.txt

COPY ./api /app/api
COPY ./triggers /app/triggers
COPY ./.env /app/.env

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app/api/"
ENV PYTHONPATH "${PYTHONPATH}:/app/triggers/"
