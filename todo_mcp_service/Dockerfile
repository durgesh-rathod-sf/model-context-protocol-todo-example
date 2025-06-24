# Use a slim official Python base image
FROM python:3.12-slim


# Set working directory
WORKDIR /app

# Copy project metadata first for better Docker layer caching
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN pip install --no-cache-dir poetry
RUN poetry install --no-root

# Copy the full app code
COPY . .

# Expose MCP server port (default 9001)
EXPOSE 9002

# Run with uvicorn if mounting into FastAPI, OR use MCP's own runner for streamable-http
CMD ["poetry", "run", "python", "mcp_server.py"]
