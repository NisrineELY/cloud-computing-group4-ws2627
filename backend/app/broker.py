"""Connect to the first reachable node of the RabbitMQ cluster."""
import logging
import os
import random

import pika

log = logging.getLogger("broker")


def connect(heartbeat: int = 30) -> pika.BlockingConnection:
    hosts = [h.strip() for h in os.environ.get("RABBITMQ_HOSTS", "rabbitmq").split(",") if h.strip()]
    random.shuffle(hosts)  # spread clients across the cluster
    credentials = pika.PlainCredentials(
        os.environ["RABBITMQ_USER"], os.environ["RABBITMQ_PASSWORD"]
    )
    errors = []
    for host in hosts:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=host, credentials=credentials, heartbeat=heartbeat,
                blocked_connection_timeout=10, connection_attempts=1,
                socket_timeout=3, stack_timeout=5,
            ))
            log.info("Connected to RabbitMQ node %s", host)
            return connection
        except Exception as exc:  # name not found, refused, timeout ...
            errors.append(f"{host}: {exc!r}")
    raise pika.exceptions.AMQPConnectionError("; ".join(errors))