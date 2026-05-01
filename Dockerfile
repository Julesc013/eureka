# Eureka hosted public search wrapper template.
#
# This image is a deployable wrapper artifact only. Building or committing it
# does not deploy a backend, enable live probes, add credentials, or prove
# hosted availability.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV EUREKA_PUBLIC_MODE=1
ENV EUREKA_SEARCH_MODE=local_index_only
ENV EUREKA_ALLOW_LIVE_PROBES=0
ENV EUREKA_ALLOW_DOWNLOADS=0
ENV EUREKA_ALLOW_UPLOADS=0
ENV EUREKA_ALLOW_LOCAL_PATHS=0
ENV EUREKA_ALLOW_ARBITRARY_URL_FETCH=0
ENV EUREKA_ALLOW_INSTALL_ACTIONS=0
ENV EUREKA_ALLOW_TELEMETRY=0
ENV EUREKA_MAX_QUERY_LEN=160
ENV EUREKA_MAX_RESULTS=20
ENV EUREKA_GLOBAL_TIMEOUT_MS=5000

WORKDIR /app
COPY . /app

EXPOSE 8080

CMD ["python", "scripts/run_hosted_public_search.py", "--public-mode", "--host", "0.0.0.0"]
