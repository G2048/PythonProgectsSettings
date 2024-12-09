FROM python:3.12.7-slim-bookworm AS python-base

# prevents python creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1\
  # do not ask any interactive question
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  PATH="/root/.local/bin:$PATH"

RUN apt-get update \
  && apt-get install --no-install-recommends -y \
  curl \
  build-essential \
  ca-certificates

RUN update-ca-certificates
RUN curl -ksSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root
COPY app /app/app

CMD ["python", "-m", "app.main"]
