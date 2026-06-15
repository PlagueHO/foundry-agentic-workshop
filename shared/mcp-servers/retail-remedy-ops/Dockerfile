# Container image for the Retail Remedy Operations MCP server.
# Built and published to its Azure Container App by `scripts/deploy-mcp-server.py`.
# The Container App is provisioned by default (AZURE_CONTAINER_APPS_DEPLOY). See the
# Module 06 README for details.
FROM python:3.14-slim

WORKDIR /app

# Install dependencies first to leverage Docker layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server source and its mock data.
COPY src/ ./src/

# The MCP server listens on this port; Azure Container Apps ingress targets it.
ENV MCP_SERVER_PORT=8080
EXPOSE 8080

CMD ["python", "src/server.py"]
