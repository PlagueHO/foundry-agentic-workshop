# Container image for the Blob Relay MCP server.
# Built and published to its Azure Container App by `scripts/deploy-blob-relay-mcp-server.py`.
# The Container App is provisioned by default (AZURE_CONTAINER_APPS_DEPLOY). See the
# agent-framework-dotnet Module 11 README for details.
FROM python:3.13-slim

# Install uv from the official distroless image.
COPY --from=ghcr.io/astral-sh/uv:0.11.25 /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies first to leverage Docker layer caching.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy the server source.
COPY src/ ./src/

# Add the venv to PATH so the runtime python resolves from the venv.
ENV PATH="/app/.venv/bin:$PATH"

# The MCP server listens on this port; Azure Container Apps ingress targets it.
ENV BLOB_RELAY_MCP_SERVER_PORT=8080
EXPOSE 8080

CMD ["python", "src/server.py"]
