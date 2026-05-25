import json
import boto3
import os
from typing import Dict, Any

sqs_client = boto3.client("sqs", region_name=os.getenv("AWS_REGION", "us-east-1"))

QUEUE_URL = os.getenv("SQS_QUEUE_URL")


def send_task_notification(task_id: int, event_type: str, task_data: Dict[str, Any]):
    """Send async notification via SQS"""
    message = {
        "task_id": task_id,
        "event_type": event_type,  # 'created', 'updated', 'completed'
        "data": task_data,
    }

    try:
        response = sqs_client.send_message(
            QueueUrl=QUEUE_URL, MessageBody=json.dumps(message)
        )
        return response
    except Exception as e:
        print(f"Failed to send SQS message: {str(e)}")
        raise


def process_queue_messages():
    """Process messages from SQS queue"""
    try:
        messages = sqs_client.receive_message(
            QueueUrl=QUEUE_URL, MaxNumberOfMessages=10, WaitTimeSeconds=20
        )

        if "Messages" not in messages:
            return []

        for message in messages["Messages"]:
            body = json.loads(message["Body"])
            # Process notification here
            handle_notification(body)

            # Delete processed message
            sqs_client.delete_message(
                QueueUrl=QUEUE_URL, ReceiptHandle=message["ReceiptHandle"]
            )
    except Exception as e:
        print(f"Error processing SQS messages: {str(e)}")


def handle_notification(notification: Dict[str, Any]):
    """Handle individual notification"""
    event_type = notification.get("event_type")
    print(f"Processing event: {event_type} for task {notification.get('task_id')}")
    # Add your notification logic here (email, SMS, etc.)
