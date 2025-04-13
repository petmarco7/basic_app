# Dockerfile for backend service
FROM python:3.11-slim AS backend

# Set working directory
WORKDIR /app

# Copy the top-level pyproject.toml and poetry.lock files
COPY ./pyproject.toml /app/
COPY ./poetry.lock /app/

# Install Poetry
RUN pip install poetry==1.8.2

# Install top-level dependencies
RUN poetry install --no-root

# No need to copy the backend directory since it is mounted as a volume

# Move to backend directory to install backend dependencies
WORKDIR /app/backend
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-root --no-dev

# Set PYTHONPATH for both top-level and backend modules
ENV PYTHONPATH="/app:/app/backend"

# Expose port 8080
EXPOSE 8080

# Run Uvicorn server on port 8080 for the backend
CMD ["/app/backend/entrypoint.sh"]
