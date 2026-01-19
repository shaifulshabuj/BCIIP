FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

COPY pyproject.toml poetry.lock* ./

# Optimization: Pre-install torch CPU to avoid massive CUDA binaries
# Then run poetry install.
RUN poetry run pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    && poetry install --no-root --no-ansi \
    && rm -rf /root/.cache/pip \
    && rm -rf /root/.cache/pypoetry

# Final stage
FROM python:3.11-slim as runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Copy only the virtualenv from builder
COPY --from=builder /app/.venv ./.venv

# Copy only the necessary source code
COPY services ./services
COPY libs ./libs
COPY pyproject.toml ./

# Default command
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
