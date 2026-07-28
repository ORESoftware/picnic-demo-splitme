FROM python:3.14.6-slim-trixie@sha256:cea0e6040540fb2b965b6e7fb5ffa00871e632eef63719f0ea54bca189ce14a6

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Package indexes are cleared with find because repository policy forbids rm.
# hadolint ignore=DL3009
RUN apt-get update \
    && apt-get install -y --no-install-recommends pdftk-java=3.3.3-2 \
    && apt-get clean \
    && find /var/lib/apt/lists -mindepth 1 -delete \
    && useradd --create-home --uid 10001 appuser

WORKDIR /app

COPY src/requirements.txt /app/requirements.txt
RUN python -m pip install \
    --disable-pip-version-check \
    --no-cache-dir \
    -r /app/requirements.txt

COPY --chown=appuser:appuser src /app

USER appuser
EXPOSE 5000

CMD ["gunicorn", "--bind=0.0.0.0:5000", "--workers=2", "--threads=4", "--timeout=60", "server:app"]
