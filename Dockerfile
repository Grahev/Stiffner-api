FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Expose port (can be overridden)
EXPOSE ${PORT:-8000}

# Command to run the application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}