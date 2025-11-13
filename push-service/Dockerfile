# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY requirements.txt uv.lock ./

# Install dependencies using uv
RUN uv pip sync --system --no-cache requirements.txt

# Copy the rest of the application code
COPY ./app ./app

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
