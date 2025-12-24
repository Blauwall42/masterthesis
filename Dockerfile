FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

WORKDIR /code

COPY src/app ./app

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

ENV PYTHONPATH=/code

CMD ["flask", "--app", "app", "run", "--host=0.0.0.0"]