FROM python:3.13-slim-trixie
LABEL maintainer="datapunt@amsterdam.nl"

ENV PYTHONUNBUFFERED=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_VERSION=2.1.4

# Setup Certificates for ADP/Motiv
COPY certificates/adp_rootca.crt /usr/local/share/ca-certificates/extras/adp_rootca.crt
RUN chmod 644 /usr/local/share/ca-certificates/extras/adp_rootca.crt \
  && update-ca-certificates --fresh

# Setup datapunt directories and user
RUN adduser --system datapunt
ARG DIRECTORYLIST="/static /app /downloads /certificates /deploy /var/log/uwsgi"
RUN mkdir -p "$DIRECTORYLIST" && chown datapunt "$DIRECTORYLIST"

# Setup application
WORKDIR /app

RUN apt-get update && apt-get install -y \
  gdal-bin \
  libgdal-dev \
  graphviz \
  graphviz-dev \
  postgresql-client \
  tzdata \
  media-types \
  wget \
  curl \
  netcat-openbsd \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools uwsgi
RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-interaction --no-ansi --no-root

COPY . /app/

RUN chmod +x /app/wait-for.sh
RUN chmod +x /app/celery.sh
RUN chmod +x /app/celery-beat.sh
RUN chmod +x /app/deploy/entrypoint.sh
RUN chmod +x /app/deploy/entrypoint.development.sh

ENTRYPOINT ["/app/deploy/entrypoint.sh"]
CMD ["uwsgi", "--ini", "/app/deploy/config.ini"]
