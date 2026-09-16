# Build image

FROM python:3.13-slim

# Update Debian packages to latest security fixes

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Working directory

WORKDIR /app

# Create non-root user

RUN useradd --create-home --shell /bin/bash appuser

# Copy the requirements file from build context

COPY requirements.txt .

# Install app dependencies

RUN pip install --no-cache-dir -r requirements.txt

# Copy application from local to the image

COPY application ./application

# Run application as non-root user

USER appuser

# Expose port on which app will run

EXPOSE 8000

# Container health check

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Start the Uvicorn server
# Find app inside application/main.py
# Listen on all network interfaces inside the container

CMD ["uvicorn", "application.main:app", "--host", "0.0.0.0", "--port", "8000"]