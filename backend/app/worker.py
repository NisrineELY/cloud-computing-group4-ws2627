"""Consume RabbitMQ events and persist metadata in PostgreSQL."""
import json
import logging
import os
import time

import pika
import psycopg
from app import broker

QUEUE = "drone.detections"
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("drone-worker")


def save_detection(event: dict) -> None:
    with psycopg.connect(
        host="postgres", dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"], password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO cameras (camera_id, name)
                VALUES (%s, %s)
                ON CONFLICT (camera_id) DO NOTHING
            """, (event["camera_id"], event["camera_id"]))
            cur.execute("""
                INSERT INTO detections
                  (event_id, camera_id, object_type, confidence,
                   detected_at, tracking_id, image_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
            """, (
                event["event_id"], event["camera_id"], event["object_type"],
                event["confidence"], event["detected_at"],
                event.get("tracking_id"), event.get("image_path"),
            ))


def on_message(channel, method, _properties, body):
    try:
        event = json.loads(body)
        save_detection(event)
        # Only acknowledge after the database transaction commits.
        channel.basic_ack(delivery_tag=method.delivery_tag)
        log.info("Stored event %s", event["event_id"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        log.error("Discarding malformed event: %s", exc)
        channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
    except Exception:
        log.exception("Database write failed. Will retry the event.")
        time.sleep(3)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def run():
    while True:
        connection = None
        try:
            connection = broker.connect()
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE, on_message_callback=on_message,
                                  auto_ack=False)
            log.info("Waiting for drone detection events")
            channel.start_consuming()
        except Exception:
            log.exception("Worker connection lost. Reconnecting")
            time.sleep(3)
        finally:
            if connection is not None and connection.is_open:
                connection.close()


if __name__ == "__main__":
    run()
