# Light academy image: Python + PyYAML only. Curriculum + engine.
# Build: docker build -t pi-sdr-academy .
# Run:   docker run --rm -p 8080:8080 pi-sdr-academy

FROM python:3.12-alpine

WORKDIR /app

# PyYAML only runtime dep (matches platform/pyproject.toml)
RUN pip install --no-cache-dir "PyYAML>=6.0"

COPY platform/academy ./academy
COPY curriculum ./curriculum

ENV PYTHONPATH=/app \
    ACADEMY_CURRICULUM=/app/curriculum \
    ACADEMY_DATA=/data \
    ACADEMY_WORKSPACE=/challenge \
    ACADEMY_FLAG_PATH=/data/flag.txt

RUN mkdir -p /data /challenge \
 && printf '%s\n' \
    'import os' \
    'from academy.api import serve_api' \
    'from pathlib import Path' \
    'serve_api(Path("/app/curriculum"), Path("/data"), host="0.0.0.0", port=int(os.environ.get("PORT","8080")), admin=os.environ.get("ACADEMY_ADMIN","0") in ("1","true","yes"))' \
    > /app/run.py

EXPOSE 8080
VOLUME ["/data", "/challenge"]

CMD ["python", "-u", "/app/run.py"]
