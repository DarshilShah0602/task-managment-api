import watchtower
import logging
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
tracer = Tracer()
metrics = Metrics()


def setup_cloudwatch_logging():
    """Configure CloudWatch logging"""
    cloudwatch_handler = watchtower.CloudWatchLogHandler()
    logging.getLogger().addHandler(cloudwatch_handler)
    return logging.getLogger()


def log_api_call(endpoint: str, method: str, status_code: int, latency: float):
    """Log API metrics to CloudWatch"""
    try:
        metrics.add_metric(name="APICallLatency", unit="Milliseconds", value=latency)
        metrics.add_metadata(key="endpoint", value=endpoint)
        metrics.add_metadata(key="method", value=method)
        metrics.add_metadata(key="status_code", value=status_code)
    except Exception as exc:
        logger.warning(f"Failed to record API metric: {exc}")

    logger.info(
        f"API Call: {method} {endpoint} - Status: {status_code} - Latency: {latency}ms"
    )
