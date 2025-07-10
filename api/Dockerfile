FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY requirements-dev.txt requirements-dev.txt

COPY ./ /app/api
COPY ./tests /app/tests

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

ENV PYTHONPATH "${PYTHONPATH}:/"

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["python api/models/management/generate_schema.py && python api/main.py"]
