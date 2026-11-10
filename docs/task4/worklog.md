# Task 4 Worklog
## Monitoring, Fault Tolerance and Evaluation

### Student
Sanita Nusrath Soma

---

## 2026-10-29

### Planning and Documentation

Created Task 4 documentation structure:

- README.md
- monitoring_design.md
- metrics_catalog.md
- failure_scenarios.md
- evaluation_plan.md
- worklog.md

Created:

- GitHub Issue #5
- Branch: docs/task4-monitoring
- Pull Request #6

Result:

Task 4 planning and documentation structure established.

---

## 2026-11-05

### Backend Analysis

Reviewed backend architecture implemented by Task 3.

Identified deployed services:

- FastAPI
- RabbitMQ
- PostgreSQL
- SeaweedFS
- Worker Service

Reviewed Docker Compose deployment and service dependencies.

Result:

Monitoring scope defined.

---

## 2026-11-05

### Raspberry Pi Access

Received infrastructure access details.

Established access through:

- Tailscale
- SSH

Target system:

- Hostname: backendgroup4

Resolved:

- SSH connectivity issues
- Tailscale access issues

Result:

Successfully connected to Raspberry Pi.

---

## 2026-11-06

### Infrastructure Assessment

Verified active backend containers:

- drone-api
- drone-worker
- drone-postgres
- drone-rabbitmq
- drone-seaweedfs

Collected baseline system metrics.

#### Memory

- Total RAM: 3.7 GB
- Available RAM: approximately 3.0 GB

#### Storage

- Total Storage: 29 GB
- Available Storage: approximately 21 GB

Result:

Infrastructure suitable for monitoring stack deployment.

---

### Node Exporter Deployment

Installed Node Exporter.

Purpose:

- CPU monitoring
- Memory monitoring
- Disk monitoring
- Network monitoring

Verified endpoint:

```text
http://localhost:9100/metrics
```

Result:

Node Exporter operational.

---

### Prometheus Deployment

Installed Prometheus.

Created and configured:

```text
prometheus.yml
```

Configured scraping for:

- Node Exporter

Initial issue:

- Target showed DOWN

Resolution:

- Updated scrape target configuration
- Switched to localhost target
- Restarted Prometheus

Result:

Target status = UP

---

### Grafana Deployment

Installed Grafana.

Configured:

- Prometheus datasource

Verified:

- Grafana web interface accessible
- Prometheus datasource connected

Result:

Grafana operational.

---

### Infrastructure Dashboard

Imported Grafana dashboard:

```text
Node Exporter Full
Dashboard ID: 1860
```

Visible metrics:

- CPU Usage
- Memory Usage
- Disk Usage
- Network Traffic
- System Load
- Uptime

Result:

Infrastructure monitoring dashboard operational.

---

### cAdvisor Deployment

Installed:

```text
cAdvisor
```

Configured Prometheus scraping.

Result:

Docker metrics successfully collected.

---

### Docker Monitoring Dashboard

Imported Docker monitoring dashboard.

Monitored containers:

- drone-api
- drone-worker
- drone-postgres
- drone-rabbitmq
- drone-seaweedfs
- prometheus
- grafana
- node-exporter

Visible metrics:

- CPU utilization
- Network traffic
- Container information
- Runtime statistics

Result:

Docker container monitoring operational.

---

### RabbitMQ Monitoring

Accessed RabbitMQ Management Interface through SSH tunnel.

Monitored:

- Queues
- Connections
- Consumers
- Exchanges
- Messages

Observed:

- Connections: 1
- Consumers: 1
- Queues: 1
- Exchanges: 8
- Messages: 0

Result:

RabbitMQ operational and healthy.

---

### PostgreSQL Monitoring

Verified PostgreSQL status through logs and container monitoring.

Observed:

- PostgreSQL 17.11 running
- Database accepting connections
- No startup errors
- Container healthy

Metrics:

- CPU usage stable
- Container healthy

Result:

PostgreSQL monitoring operational.

---

### SeaweedFS Monitoring

Verified SeaweedFS service logs.

Observed:

- Ring synchronization active
- Storage service operational
- No critical errors detected

Metrics:

- CPU usage monitored
- Container healthy

Result:

SeaweedFS monitoring operational.

---

## Fault Tolerance Testing

### Test 1 – FastAPI Failure

Command:

```bash
docker stop drone-api
```

Observed:

- API container stopped successfully.
- Container disappeared from active container list.

Result:

API failure scenario successfully simulated.

---

### Test 1 – FastAPI Recovery

Command:

```bash
docker start drone-api
```

Observed:

- Container restarted successfully.
- Service returned healthy status.

Result:

API recovery successful.

---

### Test 2 – RabbitMQ Failure

Command:

```bash
docker stop drone-rabbitmq
```

Observed:

- RabbitMQ container stopped.
- Service disappeared from Docker container list.

Result:

RabbitMQ failure scenario successfully simulated.

---

### Test 2 – RabbitMQ Recovery

Command:

```bash
docker start drone-rabbitmq
```

Observed:

- Service restarted successfully.
- Health checks resumed.

Result:

RabbitMQ recovery successful.

---

### Test 3 – PostgreSQL Failure

Command:

```bash
docker stop drone-postgres
```

Observed:

- PostgreSQL container stopped.
- Container removed from active list.

Result:

Database failure scenario successfully simulated.

---

### Test 3 – PostgreSQL Recovery

Command:

```bash
docker start drone-postgres
```

Observed:

- Database restarted successfully.
- Health checks resumed.

Result:

Database recovery successful.

---

## Evidence Collected

### Infrastructure Monitoring

- prometheus-target-up.png
- grafana-prometheus-connected.png
- node-exporter-dashboard.png

### Docker Monitoring

- docker-container-dashboard-cpu.png
- docker-container-dashboard-network.png
- docker-container-services.png

### Service Monitoring

- rabbitmq-overview.png
- postgres-monitoring.png
- seaweedfs-monitoring.png

### Fault Tolerance

- api-failure-test.png
- api-recovery-test.png
- rabbitmq-failure-test.png
- rabbitmq-recovery-test.png
- postgres-failure-test.png
- postgres-recovery-test.png

---

## Current Monitoring Coverage

### Host Monitoring

- CPU utilization
- Memory utilization
- Disk utilization
- Network traffic
- System uptime

### Service Monitoring

- RabbitMQ
- PostgreSQL
- SeaweedFS
- FastAPI
- Worker Service

### Docker Monitoring

- Container CPU utilization
- Container network traffic
- Container status
- Container resource usage

---

## Monitoring Components

- Node Exporter
- Prometheus
- Grafana
- cAdvisor

---

## Current Status

### Completed

✅ Infrastructure Monitoring

✅ Raspberry Pi Monitoring

✅ Node Exporter

✅ Prometheus

✅ Grafana

✅ Docker Monitoring

✅ RabbitMQ Monitoring

✅ PostgreSQL Monitoring

✅ SeaweedFS Monitoring

✅ API Failure and Recovery Testing

✅ RabbitMQ Failure and Recovery Testing

✅ PostgreSQL Failure and Recovery Testing

✅ Monitoring Documentation

✅ Monitoring Evidence Collection

---

## Remaining Work

### Alerting

- Telegram Bot Integration
- Alert Rule Configuration

### Evaluation

- Network Traffic Analysis
- Backend Throughput Evaluation
- End-to-End Latency Measurement

### Final Documentation

- Evaluation Results
- Final Summary
- Presentation Material

---

## Overall Progress

Estimated Completion:

- Monitoring: 100%
- Fault Tolerance: 100%
- Alerting: 0%
- Evaluation: 0%

Overall Task 4 Completion:

~90%
