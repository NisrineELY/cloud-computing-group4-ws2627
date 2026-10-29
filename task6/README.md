# Task 6 – Automatic Camera Control and Object Tracking

Part of the Group 4 drone-detection edge computing project (Cloud Computing WS2627, Frankfurt UAS).

## Purpose

Task 6 points a pan-tilt mount at drones detected by the stationary overview cameras (Task 1/2).
The first stage uses a **low-power laser pointer** on the mount instead of a camera, so pointing
accuracy can be measured by detecting the laser dot on a wall. Later stages add the tracking
camera and, optionally, the table-tennis-ball countermeasure demonstrator.

## Architecture (planned)

```
Overview webcams ──> Detection (Task 2, Pi 5) ──> task6 controller (Python, Pi 5)
                                                        │ USB serial
                                                        v
                                               ESP32-C6 firmware ──> pan/tilt servos + laser
                                                        │
                        MQTT (status/commands) <────────┘  (via the Task 3 backend)
```

## Folder layout

| Folder      | Contents                                              |
|-------------|-------------------------------------------------------|
| `firmware/` | ESP32-C6 code (servo control, laser, serial protocol) |
| `pi/`       | Python controller running on the Raspberry Pi 5       |
| `config/`   | Example configuration (copy and adapt locally)        |
| `docs/`     | Design notes, experiments, measurements, results      |

## Hardware (laser stage)

- ESP32-C6 microcontroller
- Pan-tilt bracket with 2 servos
- Laser module, Class 1/2 (≤ 1 mW)
- Separate 5 V supply for the servos (shared ground with the ESP32)

## Safety

- The laser is used **indoors only**, aimed at a wall or target, never at the sky or at people.
- The firmware enforces a maximum tilt angle so the laser cannot point upward.
- If the controller stops sending commands, a watchdog switches the laser off and parks the mount.

## Setup

_TODO: wiring diagram, firmware flashing steps, Python environment setup._

## How to run

_TODO_

## Status

- [ ] Hardware ordered
- [ ] Firmware: servo sweep
- [ ] Firmware: serial commands (pan, tilt, laser on/off)
- [ ] Safety: tilt limit + watchdog
- [ ] Pi controller: send commands over serial
- [ ] Calibration and pointing-accuracy measurement
