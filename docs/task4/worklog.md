# Task 4 Work Log

Owner: Sanita Nusrath Soma

---

## 2026-10-29

### Objectives

- Set up Task 4 documentation structure
- Define monitoring requirements

### Completed

- Created docs/task4 folder
- Created README.md
- Created monitoring_design.md
- Created metrics_catalog.md
- Created failure_scenarios.md
- Created evaluation_plan.md

### Challenges

- Learning GitHub workflow
- Understanding repository structure

### Notes

- Monitoring will use Prometheus and Grafana.
- Telegram notifications will be implemented later.

### Next Steps

- Create GitHub Issues for Task 4
- Research Prometheus deployment on Raspberry Pi
- Design Grafana dashboard layout

---
## 2026-11-06

### Completed

- Connected to Raspberry Pi through Tailscale
- Verified backend services:
  - drone-api
  - drone-worker
  - drone-postgres
  - drone-rabbitmq
  - drone-seaweedfs
- Installed Node Exporter
- Verified metrics endpoint on port 9100
- Installed Prometheus
- Configured Prometheus scraping
- Verified target health is UP
- Installed Grafana
- Connected Grafana to Prometheus
- Imported Node Exporter Full dashboard

### Results

Successfully visualized:

- CPU usage
- Memory usage
- Disk utilization
- Network traffic
- System uptime

### Evidence

- prometheus-target-up.png
- grafana-prometheus-connected.png
- node-exporter-dashboard.png

### Next Steps

- Docker container monitoring
- RabbitMQ monitoring
- PostgreSQL monitoring
- Telegram alerts
- Failure testing

## YYYY-MM-DD

### Objectives

-

### Completed

-

### Challenges

-

### Notes

-

### Next Steps

-
