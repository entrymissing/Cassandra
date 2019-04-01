# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN apt-get update && apt-get -y install iputils-ping

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python3", "cassandra.py", "-c", "settings/outpost.json"]
