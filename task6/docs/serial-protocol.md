# task6 serial protocol (v1)

Plain-text lines at 115200 baud, newline-terminated, case-insensitive. Used between the
controller (laptop now, Raspberry Pi 5 later) and the ESP32-C6 firmware.

| Command            | Reply                               | Notes |
|--------------------|-------------------------------------|-------|
| `PING`             | `PONG`                              | Also used as heartbeat |
| `PAN <deg>`        | `OK PAN <deg>`                      | Clamped to 0–180 |
| `TILT <deg>`       | `OK TILT <deg>`                     | Clamped to 0–60 (safety) |
| `MOVE <pan> <tilt>`| `OK MOVE <pan> <tilt>`              | Both clamped |
| `LASER ON` / `OFF` | `OK LASER ON` / `OK LASER OFF`      | Laser is OFF at boot |
| `PARK`             | `OK PARK`                           | Laser off, pan 90, tilt 20 |
| `SWEEP`            | `OK SWEEP`                          | Demo sweep, laser off, ends after 30 s |
| `STATUS`           | `STATUS pan=.. tilt=.. laser=.. target_pan=.. target_tilt=..` | |
| `WD <ms>`          | `OK WD <ms>`                        | Watchdog timeout, 250–10000 ms |
| anything else      | `ERR <reason>`                      | |

Unsolicited messages from the firmware:

- `task6 pan-tilt ready ...` after boot
- `WARN watchdog timeout: laser off, parking`: the laser was on and no valid command
  arrived within the watchdog timeout (default 1000 ms)

Motion is slew-rate limited (180 °/s) to avoid current spikes. Planned for v2: checksums and
binary framing once the protocol is driven by the tracking loop instead of a human.
