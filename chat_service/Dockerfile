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

EXPOSE 7000

CMD ["poetry", "run", "uvicorn", "mcp_client:app", "--host", "0.0.0.0", "--port", "7000", "--workers", "1"]
