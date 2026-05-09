FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies
COPY pyproject.toml .
RUN uv sync --frozen

# Copy source
COPY src/ src/
COPY config.toml .

# Create data directory for checkpoints
RUN mkdir -p data

EXPOSE 8080

CMD ["uv", "run", "python", "-m", "src.main"]
