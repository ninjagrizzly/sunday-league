FROM python:3.13-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only=main

# Copy application code
COPY . .

# Create directories
RUN mkdir -p data logs

# Run the application
CMD ["poetry", "run", "python", "main.py"]