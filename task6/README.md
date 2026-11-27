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
                                           Pico 2 W firmware ──> pan/tilt servos + laser
                                                        │
                        MQTT (status/commands) <────────┘  (via the Task 3 backend)
```

## Folder layout

| Folder      | Contents                                              |
|-------------|-------------------------------------------------------|
| `firmware/` | Raspberry Pi Pico 2 W code (servos, laser, serial protocol) |
| `pi/`       | Python controller running on the Raspberry Pi 5       |
| `config/`   | Example configuration (copy and adapt locally)        |
| `docs/`     | Design notes, experiments, measurements, results      |

## Hardware (laser stage)

- Raspberry Pi Pico 2 W microcontroller (from the team case)
- 2x Miuzei MS18 micro servo 9g (from the team case)
- Pan-tilt bracket
- Laser module, Class 1/2 (≤ 1 mW)
- 5 V for the servos: USB VBUS for first tests, separate supply (shared ground) later

## Safety

- The laser (Class 2, ≤ 1 mW) is used **indoors only** and never switched on outdoors or aimed at people.
- The firmware hard-limits tilt to ≥ 78° (servo angle); below that the servos collide and overheat.
- If the controller stops sending commands, a watchdog switches the laser off and parks the mount.

## Setup

- Firmware: `firmware/task6_pan_tilt/` (Arduino IDE 2, Pico core by Earle Philhower, board *Raspberry Pi Pico 2W*)
- Controller: `pip install -r pi/requirements.txt`
- Wiring and first lab test: see [docs/lab-session-prep.md](docs/lab-session-prep.md)
- Protocol: see [docs/serial-protocol.md](docs/serial-protocol.md)

## How to run

```bash
python pi/task6_cli.py --sim --selftest          # no hardware: simulator self-test
python pi/task6_cli.py --list                    # list serial ports
python pi/task6_cli.py --port COM5               # interactive console
python pi/task6_cli.py --port COM5 --selftest    # hardware self-test, log in docs/test-logs/
python pi/task6_cli.py --port COM5 --pattern     # aim the laser at a set of directions
python pi/task6_cli.py --port COM5 --pattern config/pattern-example.csv --dwell 3
```

## Status

- [ ] Hardware ordered
- [x] Firmware written: servo control, serial commands, laser on/off (compiles for Pico 2 W, not yet tested on hardware)
- [x] Safety in firmware: tilt limit + watchdog (not yet tested on hardware)
- [x] Controller console with simulator and self-test
- [ ] First hardware test in the lab
- [ ] Calibration and pointing-accuracy measurement
