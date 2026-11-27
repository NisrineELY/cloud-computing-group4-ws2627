# CLAUDE.md – Task 6 context

## Project
Team project (Group 4) for the Cloud Computing course WS2627 at Frankfurt UAS: an edge system that
detects, classifies and tracks drones with multiple cameras, plus a Raspberry Pi backend cluster.
This folder is **Task 6: Automatic Camera Control and Object Tracking**, owned by Noam.

## Scope of this folder
- Only work inside `task6/` unless explicitly asked otherwise. Other folders belong to teammates.
- Always refer to this component as **task6** (folder, branch names, commit prefixes, docs).

## Current stage
Laser stage: a pan-tilt mount with a low-power laser (LED for now), driven by a Raspberry Pi
Pico 2 W over USB serial,
controlled by Python on a Raspberry Pi 5 (developed on a laptop first).
Later: tracking camera on the mount, closed-loop visual tracking, optional ping-pong launcher.

## Tech
- Firmware: Raspberry Pi Pico 2 W, Arduino IDE with the Earle Philhower Pico core, Servo library.
- Servos: 2x Miuzei MS18 micro servo 9g. Pins: pan GP14, tilt GP15, laser/LED GP16.
- Serial protocol: see docs/serial-protocol.md. Simulator + self-test: pi/task6_cli.py.
- Controller: Python 3 on Raspberry Pi 5 (pyserial; MQTT later via the Task 3 broker).
- Overview cameras: Logitech office webcams (likely Brio 500), fixed, not moving.

## Hard safety rules (never remove or weaken)
- Tilt is hard-limited to >= 78 (servo angle): lower values crash the tilt servo into the pan
  servo and stall/overheat it. Never lower TILT_MIN_DEG.
- Laser is used indoors only (Class 2, <= 1 mW). The mount rests pointing straight up.
- Watchdog: if no valid command arrives within a timeout, laser OFF and mount parks.
- Laser defaults to OFF at boot and on any error.

## Team conventions (from the repo README)
- Branches: `feature/task6-...` or `docs/task6-...`. Never commit directly to `main`.
- Commit messages: small commits, prefixed `task6:`.
- PRs need a short review meeting with Leo or Tomer before merging into `main`.
- No secrets, datasets, videos or large model files in Git. Provide `*.example` configs only.
- Document as you go: purpose, setup, dependencies, configuration, how to run, results.
- Save measurements in `task6/docs/` for the final evaluation.
