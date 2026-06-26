# Container image for the Attendee Onboarding Portal.
FROM python:3.13-slim

# Install uv from the official distroless image.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/

# Add the venv to PATH so uvicorn resolves from the venv.
ENV PATH="/app/.venv/bin:$PATH"

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
