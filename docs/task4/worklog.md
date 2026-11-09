# Task 4 Worklog
## Monitoring, Fault Tolerance and Evaluation

### Student
Sanita Nusrath Soma

---

## 2026-10-29

### Completed

- Created Task 4 documentation structure.
- Created monitoring design document.
- Created metrics catalog document.
- Created evaluation plan document.
- Created worklog file.
- Reviewed project requirements and identified monitoring objectives.

### Next Steps

- Obtain access to backend infrastructure.
- Identify monitoring tools.
- Review backend architecture.

---

## 2026-11-06

### Infrastructure Access

Successfully obtained access to the project Raspberry Pi infrastructure via Tailscale and SSH.

#### Raspberry Pi

- Hostname: backendgroup4
- Access method: SSH via Tailscale

### Backend Verification

Verified running backend services:

- drone-api
- drone-worker
- drone-postgres
- drone-rabbitmq
- drone-seaweedfs

Verified that all backend containers are running and healthy.

---

### Resource Assessment

Collected baseline infrastructure metrics.

#### Memory

- Total RAM: 3.7 GB
- Available RAM: approximately 3.0 GB

#### Storage

- Total Storage: 29 GB
- Free Storage: approximately 21 GB

Assessment:

- Infrastructure has sufficient resources to host the monitoring stack.

---

### Node Exporter Deployment

Installed Node Exporter on the Raspberry Pi.

Purpose:

- CPU monitoring
- Memory monitoring
- Disk monitoring
- Network monitoring

Verified metrics endpoint:

```text
http://localhost:9100/metrics
```

Result:

- Metrics endpoint operational.

---

### Prometheus Deployment

Installed Prometheus.

Created monitoring configuration.

Configured Prometheus scraping for:

- Node Exporter

Verified:

- Prometheus service running
- Web interface accessible
- Target health operational

Result:

- Target status = UP

---

### Grafana Deployment

Installed Grafana.

Configured Prometheus datasource.

Verified:

- Grafana accessible remotely
- Prometheus datasource connected successfully

Result:

- Grafana successfully consuming Prometheus metrics.

---

### Infrastructure Dashboard

Imported Node Exporter Full dashboard.

Metrics currently visible:

- CPU utilization
- Memory utilization
- Disk utilization
- Network traffic
- System load
- System uptime

Result:

- Infrastructure monitoring dashboard operational.

---

### cAdvisor Deployment

Installed cAdvisor for Docker monitoring.

Configured Prometheus to scrape cAdvisor metrics.

Verified:

- cAdvisor operational
- Docker metrics available

---

### Docker Monitoring Dashboard

Imported Docker monitoring dashboard.

Currently monitoring:

- drone-api
- drone-worker
- drone-postgres
- drone-rabbitmq
- drone-seaweedfs
- prometheus
- grafana
- node-exporter

Visible Metrics:

- Container CPU consumption
- Container memory usage
- Network traffic
- Container information
- Runtime statistics

Result:

- Container monitoring operational.

---

## Evidence

### Infrastructure Monitoring

- prometheus-target-up.png
- grafana-prometheus-connected.png
- node-exporter-dashboard.png

### Docker Monitoring

- docker-container-dashboard-cpu.png
- docker-container-dashboard-network.png
- docker-container-services.png

---

## Current Monitoring Coverage

### Host Monitoring

- CPU usage
- Memory usage
- Disk usage
- Network traffic
- System uptime

### Container Monitoring

- drone-api
- drone-worker
- drone-postgres
- drone-rabbitmq
- drone-seaweedfs

### Monitoring Components

- Node Exporter
- Prometheus
- Grafana
- cAdvisor

---

## Remaining Task 4 Work

### Monitoring

- RabbitMQ monitoring
- PostgreSQL monitoring
- SeaweedFS monitoring

### Alerting

- Telegram Bot integration
- Alert rules configuration

### Fault Tolerance

- RabbitMQ failure testing
- PostgreSQL failure testing
- API failure testing
- Storage failure testing

### Evaluation

- Network traffic analysis
- Backend throughput testing
- End-to-end latency measurement

---

## Current Status

### Completed

✅ Raspberry Pi monitoring

✅ Node Exporter deployment

✅ Prometheus deployment

✅ Grafana deployment

✅ Infrastructure dashboard

✅ Docker container monitoring

✅ Container dashboard

### In Progress

🔄 Backend service monitoring

### Pending

⬜ Telegram notifications

⬜ Fault tolerance testing

⬜ Throughput evaluation

⬜ Latency evaluation
