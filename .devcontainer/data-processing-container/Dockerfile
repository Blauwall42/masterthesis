FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

COPY requirements.txt /tmp/requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    graphviz-dev \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip install --no-cache-dir -r /tmp/requirements.txt
