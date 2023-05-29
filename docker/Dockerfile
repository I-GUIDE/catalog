FROM python:3.10-slim

WORKDIR /app

COPY docker/requirements/api.txt requirements.txt
COPY docker/requirements/api-dev.txt requirements-dev.txt

COPY ./api /app/api
COPY ./tests /app/tests
COPY ./.env /app/.env

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

ENV PYTHONPATH "${PYTHONPATH}:/"

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["python api/models/management/generate_schema.py && python api/main.py"]
