# Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye
# FROM --platform=linux/amd64 python:3.11-slim-bullseye as build

WORKDIR /daily-story-short-generator

RUN chmod 777 /daily-story-short-generator
RUN cd /daily-story-short-generator

ENV PYTHONPATH="/daily-story-short-generator"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    imagemagick \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Fix security policy for ImageMagick
RUN sed -i '/<policy domain="path" rights="none" pattern="@\*"/d' /etc/ImageMagick-6/policy.xml

# Copy only the requirements.txt first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the codebase into the image
COPY . .

RUN chmod +x scripts/run.sh

# Command to run the application
CMD ["bash", "scripts/run.sh"]