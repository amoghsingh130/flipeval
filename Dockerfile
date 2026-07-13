FROM python:3.11.14-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/hf_cache

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git ninja-build && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY container/requirements.lock /tmp/requirements.lock
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install -r /tmp/requirements.lock

COPY . /workspace
RUN python -m pip install --no-deps . && \
    python -m pytest -q && \
    mkdir -p /opt/flipeval /kaggle/working/results && \
    python -m pip freeze > /opt/flipeval/environment.lock.txt

CMD ["python", "-m", "flipeval", "--help"]
