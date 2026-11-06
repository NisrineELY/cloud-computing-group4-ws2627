# Monitoring Setup

## Node Exporter

```bash
docker run -d \
  --name node-exporter \
  --restart unless-stopped \
  -p 9100:9100 \
  prom/node-exporter
```

## Prometheus

```bash
docker run -d \
  --name prometheus \
  --restart unless-stopped \
  --network host \
  -v ~/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

## Grafana

```bash
docker run -d \
  --name grafana \
  --restart unless-stopped \
  -p 3000:3000 \
  grafana/grafana
```

## cAdvisor

```bash
docker run -d \
  --name cadvisor \
  --restart unless-stopped \
  -p 8080:8080 \
  -v /:/rootfs:ro \
  -v /var/run:/var/run:ro \
  -v /sys:/sys:ro \
  -v /var/lib/docker/:/var/lib/docker:ro \
  gcr.io/cadvisor/cadvisor
```
