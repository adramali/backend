# Use the official Python 3.11 image from Docker Hub
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y pkg-config libmysqlclient-dev

# Set the working directory inside the container
WORKDIR /app

# Copy the code into the container
COPY . .

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app will run on (adjust as needed)
EXPOSE 5000

# Define the default command to run your Python application
CMD ["python", "app.py"]
