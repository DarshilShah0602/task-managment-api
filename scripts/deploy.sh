#!/bin/bash

set -e

AWS_REGION="us-east-1"
ECR_REPO="task-management-api"
CLUSTER_NAME="task-management-cluster"
SERVICE_NAME="task-management-service"

echo "🚀 Deploying Task Management API to AWS ECS..."

# 1. Create ECR Repository (if not exists)
echo "📦 Creating ECR repository..."
aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION || true

# 2. Get ECR login token
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

# 3. Build and push Docker image
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
IMAGE_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest"
echo "🐳 Building Docker image..."
docker build -t $IMAGE_URI .
docker push $IMAGE_URI

# 4. Update ECS service
echo "📡 Updating ECS service..."
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service $SERVICE_NAME \
  --force-new-deployment \
  --region $AWS_REGION

echo "✅ Deployment completed!"
echo "📍 Live URL: http://$(aws elbv2 describe-load-balancers --region $AWS_REGION --query 'LoadBalancers[0].DNSName' --output text)"
