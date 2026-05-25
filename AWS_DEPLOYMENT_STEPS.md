# AWS ECS Fargate Deployment Steps

This project deploys as:

GitHub Actions -> Amazon ECR -> Amazon ECS Fargate -> Application Load Balancer -> FastAPI

The API uses Amazon RDS PostgreSQL for production data and Amazon SQS for async task notifications.

## 1. Create AWS Resources

Use region `us-east-1` unless you change `.github/workflows/ci-cd.yml`.

Create these resources in AWS:

- ECR repository: `task-management-api`
- RDS PostgreSQL database: `taskdb`
- SQS queue: `task-notifications`
- ECS cluster: `task-management-cluster`
- ECS service: `task-management-service`
- Application Load Balancer with target group port `8000`
- CloudWatch log group: `/ecs/task-management-api`

The load balancer target group health check path must be:

```text
/health
```

## 2. Create ECR Repository

```bash
aws ecr create-repository \
  --repository-name task-management-api \
  --region us-east-1
```

## 3. Create SQS Queue

```bash
aws sqs create-queue \
  --queue-name task-notifications \
  --region us-east-1
```

Save the returned `QueueUrl`.

## 4. Create RDS PostgreSQL

Create a PostgreSQL RDS instance from the AWS Console.

Use:

```text
Database name: taskdb
Username: admin
Port: 5432
```

Your production database URL will look like:

```text
postgresql+psycopg://admin:PASSWORD@RDS_ENDPOINT:5432/taskdb
```

The RDS security group must allow inbound PostgreSQL traffic from the ECS service security group.

## 5. Prepare ECS Task Definition

Open `.github/workflows/ecs-task-definition.json` and replace:

```text
ACCOUNT_ID
REPLACE_WITH_SQS_QUEUE_URL
REPLACE_PASSWORD
REPLACE_RDS_ENDPOINT
```

For a real production setup, store `DATABASE_URL` in AWS Secrets Manager instead of plain text.

Create the CloudWatch log group:

```bash
aws logs create-log-group \
  --log-group-name /ecs/task-management-api \
  --region us-east-1
```

## 6. Create GitHub OIDC IAM Role

Create a GitHub Actions IAM role and add its ARN as a GitHub repository secret:

```text
AWS_ROLE_ARN
```

The trust policy must match this repository:

```text
repo:DarshilShah0602/task-managment-api:ref:refs/heads/main
```

The role needs permissions for ECR push, ECS deploy, CloudWatch logs, and `iam:PassRole`.

## 7. Create ECS Service

Create an ECS Fargate service using:

```text
Cluster: task-management-cluster
Service name: task-management-service
Container port: 8000
Health path: /health
Desired tasks: 1
```

Attach the service to an Application Load Balancer.

## 8. Deploy from GitHub Actions

Push to `main`:

```bash
git add .
git commit -m "Add ECS deployment pipeline"
git push origin main
```

GitHub Actions will:

1. Install dependencies.
2. Run flake8.
3. Check black formatting.
4. Run pytest.
5. Build the Docker image.
6. Push the image to ECR.
7. Deploy the new task definition to ECS.

## 9. Get Live URL

After the ECS service is healthy, get your load balancer DNS:

```bash
aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query "LoadBalancers[*].DNSName" \
  --output table
```

Test:

```bash
curl http://YOUR_ALB_DNS/health
curl http://YOUR_ALB_DNS/tasks
```

Use that ALB URL as the live API URL in your submission.

## 10. CloudWatch Alarms

Create alarms for:

- ALB `HTTPCode_Target_5XX_Count > 5`
- ALB `TargetResponseTime > 1`
- ECS `CPUUtilization > 70`
- ECS `MemoryUtilization > 80`

These cover API errors, latency, and resource usage.
