# Build Application
FROM python:3.10-slim AS build
ARG APP_DIR=/carefirst

## Install Curl
RUN apt-get update \
    && apt-get install -y \
         curl \
         build-essential \
         libffi-dev \
    && rm -rf /var/lib/apt/lists/*

## Install Poetry
ENV POETRY_VERSION=1.6.1
ENV POETRY_HOME=/etc/poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=${POETRY_HOME}/bin:${PATH}

## Setup virtual environment and run poetry install
RUN python -m venv --copies ${APP_DIR}/venv
WORKDIR ${APP_DIR}
COPY pyproject.toml poetry.lock ${APP_DIR}
RUN . ${APP_DIR}/venv/bin/activate && poetry install --only main

# Deploying application
FROM python:3.10-slim as deploy
ARG APP_DIR=/carefirst

## Install Curl
RUN apt-get update \
    && apt-get install -y \
         curl \
         build-essential \
         libffi-dev \
    && rm -rf /var/lib/apt/lists/*

## Copy venv and run application
WORKDIR ${APP_DIR}
COPY --from=build ${APP_DIR}/venv ${APP_DIR}/venv/
ENV PATH=${APP_DIR}/venv/bin:${PATH}
COPY . ${APP_DIR}

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD [ "curl", "-f", "http://localhost:8000/health"]

# HEALTHCHECK --interval=5s --timeout=10s --start-period=5s --retries=3 \
#   CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]