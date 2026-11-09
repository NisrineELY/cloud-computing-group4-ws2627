# Monitoring Architecture Design

## Objective

Provide monitoring, visualization, alerting, and performance evaluation for the complete drone detection infrastructure.

Task 4 requires monitoring of:

- Sensor status
- Cluster status
- Resource utilization
- Temperatures
- Network traffic
- Storage utilization
- Detection information
- End-to-end latency

---

# Architecture Overview

```text
+------------------+
| Sensor Node      |
| Raspberry Pi     |
+------------------+
         |
         | Metrics
         v
+------------------+
| Node Exporter    |
+------------------+
         |
         | Scraping
         v
+------------------+
| Prometheus       |
+------------------+
         |
         +------------------+
         |                  |
         v                  v
+------------------+    +------------------+
| Grafana          |    | Alert Manager    |
+------------------+    +------------------+
         |                  |
         |                  |
         +------------------+
                    |
                    v
             Telegram Bot
```

---

# Components

## Node Exporter

Runs on:

- Sensor Node
- Backend Nodes
- Cluster Nodes

Exports:

- CPU usage
- Memory usage
- Disk usage
- Temperature
- Network statistics

---

## Prometheus

Responsibilities:

- Collect metrics from all nodes
- Store time-series data
- Evaluate alert rules

Example Metrics:

- CPU utilization
- RAM utilization
- Network throughput
- Disk utilization
- Service availability

---

## Grafana

Responsibilities:

- Dashboard visualization
- Historical data analysis
- Performance monitoring

Planned Dashboards:

### Infrastructure Dashboard

- CPU
- Memory
- Temperature
- Disk
- Network

### Detection Dashboard

- Detection count
- Confidence values
- Images
- Video clips

### Cluster Dashboard

- Node health
- Service status
- Resource utilization

---

## Telegram Bot

Responsibilities:

- Health alerts
- Failure notifications
- Drone detection notifications

Example Alerts:

### Infrastructure

```text
WARNING:
Sensor Node Offline
```

### Detection

```text
DRONE DETECTED

Confidence: 95%
Camera: Cam-01
```

---

# Monitored System Components

## Sensor Node

Metrics:

- CPU
- Memory
- Disk
- Temperature
- Network traffic
- Camera status
- Detection rate

---

## Backend

Metrics:

- API response time
- Storage utilization
- Service availability
- Queue size

---

## Cluster

Metrics:

- Node availability
- Container status
- Resource consumption

---

# Alerting Strategy

## Warning Alerts

- CPU > 80%
- Temperature > 70°C
- Disk > 80%

## Critical Alerts

- Node offline
- Camera unavailable
- Storage unavailable
- Backend service failure

---

# Future Integration

Additional metrics will be integrated from:

- Drone detection service
- Tracking service
- Video storage service

These metrics include:

- Detection confidence
- Tracking status
- End-to-end latency
- Backend throughput

---

# Expected Outcome

The monitoring solution will provide:

- Real-time infrastructure monitoring
- Failure detection
- Telegram notifications
- Performance visualization
- Experimental evaluation support
