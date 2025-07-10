FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt requirements.txt

COPY ./ /app/api
COPY ./ /app/triggers

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app/api/"
ENV PYTHONPATH "${PYTHONPATH}:/app/triggers/"
