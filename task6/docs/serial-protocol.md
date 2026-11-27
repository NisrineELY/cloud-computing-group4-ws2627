# task6 serial protocol (v1)

Plain-text lines at 115200 baud, newline-terminated, case-insensitive. Used between the
controller (laptop now, Raspberry Pi 5 later) and the Raspberry Pi Pico 2 W firmware.

| Command            | Reply                               | Notes |
|--------------------|-------------------------------------|-------|
| `PING`             | `PONG`                              | Also used as heartbeat |
| `PAN <deg>`        | `OK PAN <deg>`                      | Clamped to 5–175 |
| `TILT <deg>`       | `OK TILT <deg>`                     | Clamped to 78–165; 78 = straight up, 165 = horizontal, below 78 the servos collide |
| `MOVE <pan> <tilt>`| `OK MOVE <pan> <tilt>`              | Raw servo angles, both clamped |
| `AIM <az> <el>`    | `OK AIM <az> <el> pan=<p> tilt=<t>` | Real direction: az 0 = ahead (+ = right), el 0 = horizontal, 90 = up. Reply shows the direction actually reached after clamping |
| `LASER ON` / `OFF` | `OK LASER ON` / `OK LASER OFF`      | Laser is OFF at boot |
| `PARK`             | `OK PARK`                           | Laser off, pan 103, tilt 78 (straight up); servos relax 1.5 s after arriving |
| `SWEEP`            | `OK SWEEP`                          | Demo sweep, laser off, ends after 30 s |
| `STATUS`           | `STATUS pan=.. tilt=.. laser=.. target_pan=.. target_tilt=..` | |
| `WD <ms>`          | `OK WD <ms>`                        | Watchdog timeout, 250–10000 ms |
| `RELAX`            | `OK RELAX`                          | Servos stop holding position (limp), laser off |
| `CAL ON` / `OFF`   | `OK CAL ON` / `OK CAL OFF`          | Calibration mode: laser locked off, full 0–180 range |
| anything else      | `ERR <reason>`                      | |

Unsolicited messages from the firmware:

- `task6 pan-tilt ready (servos relaxed) ...` after boot. Servos are not driven until the
  first move command, so an uncalibrated mount is never pushed into its end stops.
- `WARN watchdog timeout: laser off, parking`: the laser was on and no valid command
  arrived within the watchdog timeout (default 5000 ms)

Motion is slew-rate limited (180 °/s) to avoid current spikes. Planned for v2: checksums and
binary framing once the protocol is driven by the tracking loop instead of a human.
