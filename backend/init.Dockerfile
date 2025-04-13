# Dockerfile for init container
FROM python:3.11-slim AS init

# Set working directory
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files
COPY ./pyproject.toml /app
COPY ./poetry.lock /app

# Install Poetry
RUN pip install poetry==1.8.2

# Install top-level dependencies
RUN poetry install --no-root

# Make a directory for the backend
RUN mkdir /app/backend

# Copy backend source code
COPY ./backend/*.py /app/backend
COPY ./backend/pyproject.toml /app/backend
COPY ./backend/poetry.lock /app/backend

# Install the environment in the backend directory
WORKDIR /app/backend

#Configure poetry to create virtual environment in the backend directory
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-root

# Set PYTHONPATH for both /app and /app/backend
ENV PYTHONPATH="/app:/app/backend"
CMD ["poetry", "run", "python", "-m", "backend.setup"]
