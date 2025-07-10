# Use the official Python image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Make migrations

RUN python manage.py makemigrations

RUN python manage.py migrate

# Initialize the database

RUN python manage.py initialize_db


# Alternative: Set environment variables using DJANGO_SETTINGS_MODULE variable. We are using env_file in docker compose
#ENV DJANGO_SETTINGS_MODULE=cryptotracker.settings.production

# Default command will be overridden by docker-compose or entrypoints
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
