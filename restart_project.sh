#!/bin/bash

# Build the Docker image
echo "Building the streaming-app image..."
docker build -t streaming-app .

# Stop and remove all containers from docker-compose
echo "Stopping and removing existing containers..."
docker-compose down

# Start containers in detached mode
echo "Starting containers with docker-compose..."
docker-compose up -d

echo "Done! Project restarted successfully."