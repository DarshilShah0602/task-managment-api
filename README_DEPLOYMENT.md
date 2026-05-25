## AWS Cloud Deployment Guide

### Prerequisites
- AWS Account with appropriate IAM permissions
- GitHub repository configured with AWS credentials
- Docker installed locally
- AWS CLI installed

### Step 1: AWS Setup

#### 1.1 Create IAM Role for GitHub Actions
```bash
# Create trust policy JSON
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_USERNAME/task-managment-api:ref:refs/heads/main"
        }
      }
    }
  ]
}
EOF

# Create role
aws iam create-role --role-name GitHubActionsRole --assume-role-policy-document file://trust-policy.json
```

#### 1.2 Create RDS PostgreSQL Instance
```bash
aws rds create-db-instance \
  --db-instance-identifier task-management-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --publicly-accessible
```

#### 1.3 Create ECS Cluster
```bash
aws ecs create-cluster --cluster-name task-management-cluster
```

#### 1.4 Create SQS Queue
```bash
aws sqs create-queue --queue-name task-notifications
```

### Step 2: GitHub Secrets Configuration

Add these secrets to GitHub repository (Settings > Secrets):
- `AWS_ROLE_ARN`: ARN of GitHubActionsRole
- `SQS_QUEUE_URL`: URL of created SQS queue
- `DATABASE_URL`: PostgreSQL connection string

### Step 3: Local Testing

```bash
# Build locally
docker-compose build

# Run services
docker-compose up

# Run tests
pytest tests/

# Access API
curl http://localhost:8000/health
```

### Step 4: Deployment

Push to main branch triggers CI/CD:
```bash
git add .
git commit -m "Deploy to AWS"
git push origin main
```

### Live API Access

After deployment, get the ALB DNS:
```bash
aws elbv2 describe-load-balancers --region us-east-1 --query 'LoadBalancers[0].DNSName'
```

Example: `http://task-api-load-balancer-123456.us-east-1.elb.amazonaws.com`

### CloudWatch Monitoring

View logs:
```bash
aws logs tail /ecs/task-management --follow
```

Set CloudWatch alarms for errors and latency.

### Troubleshooting

- Check ECS task logs: `aws ecs describe-tasks --cluster task-management-cluster`
- Verify SQS queue: `aws sqs receive-message --queue-url <URL>`
- Database connectivity: Check security groups and RDS endpoint
