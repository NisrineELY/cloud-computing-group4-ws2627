# Metrics Catalog

## Sensor Node Metrics

| Metric | Description | Unit |
|----------|-------------|---------|
| CPU Usage | Processor utilization | % |
| Memory Usage | RAM utilization | % |
| Disk Usage | Storage utilization | % |
| Temperature | CPU temperature | °C |
| Network Traffic | Incoming/Outgoing traffic | Mbps |
| Camera Status | Camera operational state | Up/Down |
| Detection Rate | Number of detections | detections/min |

---

## Backend Metrics

| Metric | Description | Unit |
|----------|-------------|---------|
| API Response Time | Backend response latency | ms |
| Database Health | Database availability | Up/Down |
| Queue Length | Pending messages | count |
| Storage Usage | Backend storage utilization | GB |
| Service Availability | Service operational state | Up/Down |

---

## Cluster Metrics

| Metric | Description | Unit |
|----------|-------------|---------|
| Node Status | Node availability | Up/Down |
| CPU Usage | Cluster CPU utilization | % |
| Memory Usage | Cluster memory utilization | % |
| Network Throughput | Cluster network traffic | Mbps |
| Container Status | Running container count | count |

---

## Evaluation Metrics

| Metric | Description | Unit |
|----------|-------------|---------|
| End-to-End Latency | Detection to display delay | ms |
| Throughput | Processed events per second | events/s |
| Peak Network Traffic | Maximum observed traffic | Mbps |
| Detection Confidence | AI confidence level | % |
