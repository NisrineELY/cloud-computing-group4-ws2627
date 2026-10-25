# task6 – Lab session prep (first hardware test)

Goal: use the ~1 hour of lab time only for wiring and testing. Everything else is done before class.

## A. Before class (at home, no hardware needed)

1. **Arduino IDE 2** installed.
2. **ESP32 board support, version 3.x** (needed for the ESP32-C6):
   - File → Preferences → Additional boards manager URLs:
     `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
   - Tools → Board → Boards Manager → install **esp32 by Espressif Systems** (3.x).
3. Open `task6/firmware/task6_pan_tilt/task6_pan_tilt.ino`, select board **ESP32C6 Dev Module**, click **Verify** (compile only). It must compile without errors.
4. Python: `pip install -r task6/pi/requirements.txt`
5. Run the simulator self-test: `python task6/pi/task6_cli.py --sim --selftest` → must end with `ALL PASS`.
6. Find out what hardware will be available in class (servo type, pan-tilt bracket, laser module, power supply, ESP32-C6 board model). Adjust pins in the sketch if needed.
7. Optional: try the sketch in the Wokwi online simulator (ESP32-C6 + 2 servos + LED).

## B. Bring to class

- Laptop with everything from section A
- ESP32-C6 board + **data** USB cable (not a charge-only cable)
- Breadboard, jumper wires, 1 LED + 220 Ω resistor (laser stand-in for the first test)
- This checklist (printed or on the laptop)

## C. Wiring

| From                     | To                          | Note                                      |
|--------------------------|-----------------------------|-------------------------------------------|
| ESP32 GPIO 18            | Pan servo signal (orange/yellow) |                                       |
| ESP32 GPIO 19            | Tilt servo signal           |                                           |
| ESP32 GPIO 20            | LED (+220 Ω) or laser driver| Laser via NPN transistor/MOSFET, not directly |
| External 5 V supply +    | Both servo red wires        | **Never** power servos from the ESP32 pins |
| External 5 V supply –    | Both servo brown/black wires **and** ESP32 GND | Shared ground is required      |

Check the pin labels on the actual board before wiring. Avoid strapping and USB pins.

## D. In class (about 60 minutes)

| Time   | Step | Pass criterion |
|--------|------|----------------|
| 0–10   | Plug in the ESP32, upload the sketch, open Serial Monitor at 115200 | `task6 pan-tilt ready ...` appears |
| 10–15  | Type `PING`, `STATUS` | `PONG`, status line |
| 15–30  | Wire the servos (power off!), then `PAN 45`, `PAN 135`, `TILT 50`, `TILT 90` | Servos move; `TILT 90` is clamped to 60 |
| 30–40  | Wire the LED, `LASER ON`, wait 2 s | LED turns off by itself (watchdog) and `WARN watchdog` appears |
| 40–50  | Close Serial Monitor, run `python task6/pi/task6_cli.py --list`, then `--port COMx --selftest` | `ALL PASS`; log saved in `docs/test-logs/` |
| 50–60  | Photos of the setup, note problems, commit the test log | Pushed to the branch |

## E. If something goes wrong

- **No output in Serial Monitor:** check the baud rate (115200). On boards with two USB ports, try the other one, or set Tools → *USB CDC On Boot* → Enabled and re-upload.
- **Upload fails:** hold BOOT, press RESET, release BOOT, then upload again.
- **Servos jitter or the board resets:** servo power problem. Check the external supply and the shared ground.
- **Servo hits its end stop or buzzes:** tune `SERVO_MIN_US` / `SERVO_MAX_US` in the sketch.
