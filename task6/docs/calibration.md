# task6 – Mount calibration

The angles in the firmware (`PAN_*`, `TILT_*`) are **servo angles**, not real directions.
Each mount must be calibrated once so that the allowed range stays inside the mechanical
limits.

## Why this matters

A servo commanded past its mechanical end stop pushes against it continuously
("stall"). It buzzes, draws maximum current, gets hot and can be destroyed within minutes.

## Procedure (laser OFF, enforced by the firmware)

Serial Monitor at 115200, mount on the table.

1. `CAL ON`: laser locked off, full 0–180° range allowed.
2. **Tilt:** start with `TILT 90`, then go in **10° steps** both ways
   (`TILT 100`, `TILT 110`, ... then `TILT 80`, `TILT 70`, ...).
   - Servo **buzzes or stops moving** → end stop reached. Immediately go 10° back
     (or `RELAX`). Write down the last angle that moved freely.
   - Note the angle where the top plate is **horizontal**, and which direction is up.
3. **Pan:** same, starting at `PAN 90`. Note both end stops and the "straight ahead" angle.
4. `RELAX`, then `CAL OFF`.

Between tests, touch the servo: if it gets warm, `RELAX` and wait.

## Results (Adafruit mini pan-tilt kit, 2026-11-27)

| Axis | Allowed range (servo °) | Park / reference (°) | Notes |
|------|-------------------------|----------------------|-------|
| Pan  | 5 – 175                 | 103 = aligned with the kit's base plate | No collision; servo cannot rotate a full turn, so cables cannot wind up |
| Tilt | 78 – 165                | 78 = straight up (el 90), 165 = horizontal (el 0) | Below 78 the tilt servo hits the pan servo (stall, overheating). Above 165 it would aim at the floor |

### Direction mapping used by `AIM <az> <el>`

- tilt = 165 + el / 90 × (78 − 165)  → 87 servo degrees for 90 real degrees
- pan = 103 + PAN_DIR × az

Coverage: azimuth about −98° … +72° around "ahead" (asymmetric because 103 is not the
middle of the servo range), elevation 0° … 90°, i.e. the front half of the sky.

To do: check `PAN_DIR` (positive azimuth must turn right) and verify the pan scale with
`AIM 90 10` / `AIM -90 10` against a right angle.
