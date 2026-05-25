#!/bin/bash

# Wait for API to be ready
sleep 5

# Test health endpoint
echo "Testing health endpoint..."
curl -s http://localhost:8000/health || echo "Health endpoint failed"

# Test root endpoint
echo -e "\n\nTesting root endpoint..."
curl -s http://localhost:8000/ || echo "Root endpoint failed"

# Create a task  
echo -e "\n\nCreating a task..."
curl -s -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","description":"This is a test","status":"pending"}' || echo "Create task failed"

# List tasks
echo -e "\n\nListing all tasks..."
curl -s http://localhost:8000/tasks || echo "List tasks failed"

echo -e "\n\nTests completed!"
