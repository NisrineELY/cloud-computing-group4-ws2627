# Failure Scenarios

## Camera Failure

### Test

Disconnect camera.

### Expected Result

- Alert generated
- Dashboard warning
- Telegram notification

---

## Sensor Node Restart

### Test

Restart Raspberry Pi sensor node.

### Expected Result

- Node reported offline
- Node reported online after recovery
- Telegram notification

---

## Network Connection Failure

### Test

Disconnect Ethernet cable.

### Expected Result

- Connectivity alert
- Dashboard warning

---

## Backend Service Failure

### Test

Stop API container.

### Expected Result

- Service unavailable alert
- Automatic recovery notification

---

## Storage Failure

### Test

Unmount storage device.

### Expected Result

- Storage warning
- Write error reporting

---

## Cluster Node Failure

### Test

Shutdown cluster node.

### Expected Result

- Node unavailable alert
- Resource monitoring updated
