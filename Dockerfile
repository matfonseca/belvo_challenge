# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install poetry

# Configure poetry: don't create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only=main --no-root

# Copy the entire project
COPY . .

# Expose port
EXPOSE 8501
ENV DOCKER_ENV=true
# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run streamlit app
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
