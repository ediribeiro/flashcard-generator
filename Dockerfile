# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define environment variable for PYTHONTZPATH if needed
ENV PYTHONTZPATH=/path/to/timezone/data

# Define entrypoint script for running the executable creation process
ENTRYPOINT ["./create_executable.sh"]
