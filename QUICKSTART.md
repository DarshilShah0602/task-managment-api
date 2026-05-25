# Quick Start

This guide gets the Task Management API running locally and shows the live AWS URL.

## Live API

```text
API: http://task-management-api-alb-1285279760.us-east-1.elb.amazonaws.com
Docs: http://task-management-api-alb-1285279760.us-east-1.elb.amazonaws.com/docs
Health: http://task-management-api-alb-1285279760.us-east-1.elb.amazonaws.com/health
```

## Run Locally

From the project directory:

```powershell
docker compose up --build -d
```

Open:

```text
http://localhost:8000/docs
```

Check that the API is healthy:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "task-management-api"
}
```

## Create A Task

```powershell
$body = @{
  title = "My first task"
  description = "Created from local Docker"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/tasks `
  -ContentType "application/json" `
  -Body $body
```

## List Tasks

```powershell
Invoke-RestMethod http://localhost:8000/tasks
```

## Update Task Status

```powershell
Invoke-RestMethod -Method Patch `
  -Uri http://localhost:8000/tasks/1/status `
  -ContentType "application/json" `
  -Body '{"status":"completed"}'
```

## Delete A Task

```powershell
Invoke-RestMethod -Method Delete http://localhost:8000/tasks/1
```

## Stop Local Containers

```powershell
docker compose down
```

Reset local database:

```powershell
docker compose down -v
docker compose up --build -d
```

## Run Tests

```powershell
docker compose exec api pytest tests/ -v
```

## Local Services

Docker Compose starts:

| Service | URL/Port |
| --- | --- |
| FastAPI | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| PostgreSQL | `localhost:5432` |
| LocalStack | `localhost:4566` |

Local database values:

```text
Database: taskdb
User: taskuser
Password: taskpass123
```

## AWS Resources

Current deployment:

```text
Region: us-east-1
ECR: task-management-api
ECS cluster: task-management-cluster
ECS service: task-management-service
RDS: taskdb
SQS: task-notifications
CloudWatch logs: /ecs/task-management-api
```

Check ECS:

```powershell
aws ecs describe-services `
  --cluster task-management-cluster `
  --services task-management-service `
  --region us-east-1
```

View logs:

```powershell
aws logs tail /ecs/task-management-api --follow --region us-east-1
```

## CI/CD

Before automatic deployment from GitHub Actions, add this repository secret:

```text
AWS_ROLE_ARN=arn:aws:iam::922383606596:role/GitHubActionsRole
DATABASE_URL=postgresql+psycopg://postgres:<password>@taskdb.ckfokyawc9xp.us-east-1.rds.amazonaws.com:5432/taskdb
```

Then pushing to `main` will run tests, build the Docker image, push to ECR, and deploy to ECS.
