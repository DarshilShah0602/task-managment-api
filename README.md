# Task Management API

A REST API for managing tasks, built with FastAPI, SQLAlchemy, PostgreSQL, Docker, and AWS ECS Fargate.

## Live Deployment

The API is deployed on Amazon ECS Fargate behind an Application Load Balancer.

```text
Live API: http://task-management-api-alb-1285279760.us-east-1.elb.amazonaws.com
Swagger UI: http://task-management-api-alb-1285279760.us-east-1.elb.amazonaws.com/docs
Health check: http://task-management-api-alb-1285279760.us-east-1.elb.amazonaws.com/health
```

## Features

- Create, list, read, update, and delete tasks
- Task status updates with `pending` and `completed`
- PostgreSQL persistence
- Swagger/OpenAPI documentation
- Docker Compose local development
- Unit tests with pytest
- CI/CD with GitHub Actions
- AWS ECS Fargate deployment
- Amazon SQS integration for async task notifications
- CloudWatch logs and alarms

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Docker and Docker Compose
- AWS ECR
- AWS ECS Fargate
- AWS RDS PostgreSQL
- Amazon SQS
- Amazon CloudWatch
- GitHub Actions

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/tasks` | Create a new task |
| `GET` | `/tasks` | List all tasks |
| `GET` | `/tasks/{id}` | Get a task by ID |
| `PATCH` | `/tasks/{id}/status` | Update task status |
| `PATCH` | `/tasks/{id}` | Update task details |
| `DELETE` | `/tasks/{id}` | Delete a task |
| `GET` | `/health` | Health check |

## Task Model

| Field | Type | Description |
| --- | --- | --- |
| `id` | Integer | Auto-generated unique task ID |
| `title` | String | Required task title, max 200 characters |
| `description` | Text | Optional task description |
| `status` | String | `pending` or `completed`, default `pending` |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

## Run Locally With Docker

Prerequisites:

- Docker Desktop
- Docker Compose

Start the full local stack:

```powershell
docker compose up --build -d
```

This starts:

- FastAPI on `http://localhost:8000`
- PostgreSQL 16 on port `5432`
- LocalStack for local SQS testing

Open:

```text
http://localhost:8000/docs
```

Check health:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Stop containers:

```powershell
docker compose down
```

Reset local database:

```powershell
docker compose down -v
docker compose up --build -d
```

## Local API Examples

Create a task:

```powershell
$body = @{
  title = "Learn FastAPI"
  description = "Build a task management API"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/tasks `
  -ContentType "application/json" `
  -Body $body
```

List tasks:

```powershell
Invoke-RestMethod http://localhost:8000/tasks
```

Update status:

```powershell
Invoke-RestMethod -Method Patch `
  -Uri http://localhost:8000/tasks/1/status `
  -ContentType "application/json" `
  -Body '{"status":"completed"}'
```

Delete a task:

```powershell
Invoke-RestMethod -Method Delete http://localhost:8000/tasks/1
```

## Run Tests

Using Docker:

```powershell
docker compose exec api pytest tests/ -v
```

Using local Python:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m pytest tests/ -v
```

## AWS Deployment

The current AWS deployment uses:

- Account: `922383606596`
- Region: `us-east-1`
- ECR repository: `task-management-api`
- ECS cluster: `task-management-cluster`
- ECS service: `task-management-service`
- Task definition family: `task-management-td`
- RDS database: `taskdb`
- SQS queue: `task-notifications`
- CloudWatch log group: `/ecs/task-management-api`
- ALB DNS: `task-management-api-alb-1285279760.us-east-1.elb.amazonaws.com`

Check ECS service:

```powershell
aws ecs describe-services `
  --cluster task-management-cluster `
  --services task-management-service `
  --region us-east-1
```

Check target health:

```powershell
aws elbv2 describe-target-health `
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:922383606596:targetgroup/task-management-api-tg/8ea099b32f1a2ff0 `
  --region us-east-1
```

View logs:

```powershell
aws logs tail /ecs/task-management-api --follow --region us-east-1
```

## CI/CD

GitHub Actions workflow:

```text
.github/workflows/ci-cd.yml
```

On push to `main`, the workflow:

1. Installs Python dependencies.
2. Runs flake8.
3. Checks formatting with black.
4. Runs pytest with coverage.
5. Builds a Docker image.
6. Pushes the image to Amazon ECR.
7. Deploys the task definition to ECS.

Required GitHub repository secret:

```text
AWS_ROLE_ARN=arn:aws:iam::922383606596:role/GitHubActionsRole
DATABASE_URL=postgresql+psycopg://postgres:<password>@taskdb.ckfokyawc9xp.us-east-1.rds.amazonaws.com:5432/taskdb
```

## Important Security Note

Do not commit real AWS access keys or database passwords to the repository. The CI/CD workflow expects the production database connection string from the GitHub Actions `DATABASE_URL` secret.

If a root AWS access key was exposed, delete or rotate it immediately in AWS IAM security credentials.

## Useful Files

```text
app/main.py
app/routers/tasks.py
app/models.py
app/schemas.py
app/database.py
app/sqs_handler.py
app/monitoring.py
Dockerfile
docker-compose.yml
.github/workflows/ci-cd.yml
.github/workflows/ecs-task-definition.json
```

## License

MIT
