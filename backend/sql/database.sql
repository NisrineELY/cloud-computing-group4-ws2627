-- Cloud Computing Group 4
-- Drone Detection Backend
-- PostgreSQL Database Schema

-- Table 1: Cameras
CREATE TABLE IF NOT EXISTS cameras (
    camera_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table 2: Detections
CREATE TABLE IF NOT EXISTS detections (
    detection_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    camera_id TEXT NOT NULL,
    object_type TEXT NOT NULL,
    confidence NUMERIC(4,3) NOT NULL
        CHECK (confidence >= 0 AND confidence <= 1),
    detected_at TIMESTAMPTZ NOT NULL,
    tracking_id TEXT,
    image_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_camera
        FOREIGN KEY (camera_id)
        REFERENCES cameras(camera_id)
);

-- Index for faster detection queries
CREATE INDEX IF NOT EXISTS idx_detections_camera_time
ON detections (camera_id, detected_at DESC);