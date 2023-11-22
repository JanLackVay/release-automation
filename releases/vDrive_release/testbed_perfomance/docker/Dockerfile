# Use the official Python 3.11 image as the base image
FROM python:3.11

# Set the working directory (you can change this to your project directory)
WORKDIR /usr/src/sing_off_cli

# Copy your application files into the container (if needed)
# COPY . /app

# Define the default command to run when the container starts
CMD ["python3"]

COPY src src

COPY pyproject.toml pyproject.toml

COPY requirements.txt requirements.txt

RUN python3 -m pip install --ignore-installed -r requirements.txt