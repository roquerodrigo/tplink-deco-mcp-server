FROM --platform=$BUILDPLATFORM python:3.15-slim AS build

COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /usr/local/bin/uv

WORKDIR /build

COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src

RUN uv build --wheel --out-dir dist \
    && uv export --frozen --no-default-groups --no-emit-project --format requirements-txt \
        --output-file dist/requirements.txt

FROM python:3.15-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN --mount=type=bind,from=build,source=/build/dist,target=/dist \
    pip install --no-cache-dir --require-hashes --requirement /dist/requirements.txt \
    && pip install --no-cache-dir --no-deps /dist/*.whl \
    && useradd --system --uid 10001 --no-create-home mcp

USER mcp

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=5).status < 500 else 1)"]

CMD ["tplink-deco-mcp-server", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
