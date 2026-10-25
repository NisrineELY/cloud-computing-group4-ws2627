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

- Firmware: `firmware/task6_pan_tilt/` (Arduino IDE 2, ESP32 core 3.x, board *ESP32C6 Dev Module*)
- Controller: `pip install -r pi/requirements.txt`
- Wiring and first lab test: see [docs/lab-session-prep.md](docs/lab-session-prep.md)
- Protocol: see [docs/serial-protocol.md](docs/serial-protocol.md)

## How to run

```bash
python pi/task6_cli.py --sim --selftest          # no hardware: simulator self-test
python pi/task6_cli.py --list                    # list serial ports
python pi/task6_cli.py --port COM5               # interactive console
python pi/task6_cli.py --port COM5 --selftest    # hardware self-test, log in docs/test-logs/
```

## Status

- [ ] Hardware ordered
- [x] Firmware written: servo control, serial commands, laser on/off (compiles for ESP32-C6, not yet tested on hardware)
- [x] Safety in firmware: tilt limit + watchdog (not yet tested on hardware)
- [x] Controller console with simulator and self-test
- [ ] First hardware test in the lab
- [ ] Calibration and pointing-accuracy measurement
