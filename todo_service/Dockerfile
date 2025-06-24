# Use official Python image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy project metadata first for better Docker layer caching
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN pip install --no-cache-dir poetry
RUN poetry install --no-root

# Copy the full app code
COPY . .

# Expose port 8000
EXPOSE 9001

# Command to run the app
CMD ["poetry", "run" , "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "9001"]
