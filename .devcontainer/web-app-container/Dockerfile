FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Copy requirements into image
COPY requirements.txt /tmp/requirements.txt

# Install dependencies (no persistent cache)
RUN pip install --no-cache-dir -r /tmp/requirements.txt
