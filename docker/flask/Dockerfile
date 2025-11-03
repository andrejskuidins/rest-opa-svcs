# Use an official Python runtime as a parent image
FROM python:3.12-slim

RUN apt-get update && \
    apt-get install --no-install-recommends -y jq curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app with Gunicorn: 1 worker, 0.0.0.0:8000, unbuffered output for logs
CMD ["gunicorn", "--workers=1", "--bind=0.0.0.0:8000", "--access-logfile=-", "--error-logfile=-", "app:app"]
