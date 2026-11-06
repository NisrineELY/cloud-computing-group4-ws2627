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

- Gained SSH access to backend Raspberry Pi through Tailscale
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
- Fixed scrape target configuration
- Verified target status is UP

### Evidence

- Screenshot of Docker containers
- Screenshot of Prometheus target health

### Next Steps

- Install Grafana
- Connect Grafana to Prometheus
- Build Infrastructure Dashboard

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
