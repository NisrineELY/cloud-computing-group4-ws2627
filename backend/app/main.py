"""HTTP ingestion API, database queries and minimal web dashboard."""

import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

import boto3
import pika
import psycopg

from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse, Response
from psycopg.rows import dict_row


app = FastAPI(
    title="Group 4 Drone Backend",
    version="0.1.0",
)

QUEUE = "drone.detections"
BUCKET = os.getenv("S3_BUCKET", "drone-media")

MAX_MEDIA_BYTES = 10 * 1024 * 1024

MEDIA_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "video/mp4": ".mp4",
}


def require_api_key(
    x_api_key: str | None = Header(default=None),
) -> None:
    expected = os.environ["API_KEY"]

    if not x_api_key or not secrets.compare_digest(
        x_api_key, expected
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )


def open_database():
    return psycopg.connect(
        host="postgres",
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
        row_factory=dict_row,
    )


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url="http://seaweedfs:8333",
        aws_access_key_id=os.environ["S3_ACCESS_KEY"],
        aws_secret_access_key=os.environ["S3_SECRET_KEY"],
        region_name="us-east-1",
        config=Config(
            s3={"addressing_style": "path"},
            connect_timeout=5,
            read_timeout=10,
            retries={"max_attempts": 3},
        ),
    )


def publish_event(event: dict) -> None:
    credentials = pika.PlainCredentials(
        os.environ["RABBITMQ_USER"],
        os.environ["RABBITMQ_PASSWORD"],
    )

    hosts = os.environ.get("RABBITMQ_HOSTS", "rabbitmq").split(",")
    connection = pika.BlockingConnection([
        pika.ConnectionParameters(
            host=h.strip(),
            credentials=credentials,
            connection_attempts=2,
            retry_delay=1,
            blocked_connection_timeout=10,
            heartbeat=30,
        )
        for h in hosts
    ])

    try:
        channel = connection.channel()

        channel.queue_declare(
            queue=QUEUE,
            durable=True,
        )

        # Enable publisher confirmations.
        channel.confirm_delivery()

        # basic_publish returns None on success.
        # It raises an exception if RabbitMQ rejects the message.
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE,
            body=json.dumps(event).encode("utf-8"),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
                content_type="application/json",
            ),
            mandatory=True,
        )

    finally:
        connection.close()


@app.get("/health")
def health():
    return {"status": "running"}


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    return FileResponse(
        Path(__file__).with_name("dashboard.html")
    )


@app.post(
    "/events",
    status_code=202,
    dependencies=[Depends(require_api_key)],
)
def submit_event(
    camera_id: str = Form(min_length=1, max_length=100),
    object_type: str = Form(min_length=1, max_length=60),
    confidence: float = Form(ge=0, le=1),
    event_id: str | None = Form(default=None),
    detected_at: datetime | None = Form(default=None),
    tracking_id: str | None = Form(default=None),
    media: UploadFile | None = File(default=None),
):
    try:
        identifier = (
            str(UUID(event_id))
            if event_id
            else str(uuid4())
        )
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="event_id must be a UUID",
        )

    timestamp = detected_at or datetime.now(timezone.utc)

    if timestamp.tzinfo is None:
        raise HTTPException(
            status_code=422,
            detail="detected_at needs a timezone",
        )

    object_key = None

    if media is not None:
        extension = MEDIA_TYPES.get(
            media.content_type or ""
        )

        if not extension:
            raise HTTPException(
                status_code=415,
                detail="Use JPEG, PNG or MP4 media",
            )

        data = media.file.read(MAX_MEDIA_BYTES + 1)

        if len(data) > MAX_MEDIA_BYTES:
            raise HTTPException(
                status_code=413,
                detail="Maximum media size is 10 MiB",
            )

        object_key = f"detections/{identifier}{extension}"

        try:
            s3_client().put_object(
                Bucket=BUCKET,
                Key=object_key,
                Body=data,
                ContentType=media.content_type,
            )

        except (
            BotoCoreError,
            ClientError,
            OSError,
        ) as exc:
            raise HTTPException(
                status_code=503,
                detail="Object storage unavailable",
            ) from exc

    event = {
        "event_id": identifier,
        "camera_id": camera_id,
        "object_type": object_type,
        "confidence": confidence,
        "detected_at": timestamp.isoformat(),
        "tracking_id": tracking_id,
        "image_path": object_key,
    }

    try:
        publish_event(event)

    except (
        pika.exceptions.AMQPError,
        OSError,
        RuntimeError,
    ) as exc:
        raise HTTPException(
            status_code=503,
            detail="Message broker unavailable",
        ) from exc

    return {
        "accepted": True,
        "event_id": identifier,
        "media_key": object_key,
    }


@app.get(
    "/detections",
    dependencies=[Depends(require_api_key)],
)
def list_detections():
    try:
        with open_database() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT event_id,
                           camera_id,
                           object_type,
                           confidence,
                           detected_at,
                           tracking_id,
                           image_path
                    FROM detections
                    ORDER BY detected_at DESC
                    LIMIT 50
                    """
                )

                return cur.fetchall()

    except psycopg.Error as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from exc


@app.get(
    "/detections/{event_id}/media",
    dependencies=[Depends(require_api_key)],
)
def get_media(event_id: str):
    try:
        with open_database() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT image_path
                    FROM detections
                    WHERE event_id = %s
                    """,
                    (event_id,),
                )

                row = cur.fetchone()

    except psycopg.Error as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from exc

    if not row or not row["image_path"]:
        raise HTTPException(
            status_code=404,
            detail="No media for this detection",
        )

    try:
        result = s3_client().get_object(
            Bucket=BUCKET,
            Key=row["image_path"],
        )

        try:
            content = result["Body"].read(
                MAX_MEDIA_BYTES + 1
            )
        finally:
            result["Body"].close()

        if len(content) > MAX_MEDIA_BYTES:
            raise HTTPException(
                status_code=413,
                detail="Media exceeds 10 MiB",
            )

        return Response(
            content=content,
            media_type=result.get(
                "ContentType",
                "application/octet-stream",
            ),
            headers={
                "Cache-Control": "no-store",
            },
        )

    except (
        BotoCoreError,
        ClientError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=503,
            detail="Object storage unavailable",
        ) from exc