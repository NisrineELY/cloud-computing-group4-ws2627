/*
 * task6_pan_tilt.ino
 * Task 6 (Group 4, Cloud Computing WS2627): pan-tilt mount with laser, Pico 2 W.
 *
 * Board:     Raspberry Pi Pico 2 W (Arduino core "Raspberry Pi Pico/RP2040/RP2350"
 *            by Earle Philhower, board "Raspberry Pi Pico 2W")
 * Servos:    2x Miuzei MS18 micro servo 9g
 * Libraries: Servo (included in the Pico core)
 *
 * Serial protocol: plain text lines at 115200 baud, newline-terminated.
 *   PING                 -> PONG
 *   PAN <deg>            -> OK PAN <deg>            (clamped to limits)
 *   TILT <deg>           -> OK TILT <deg>           (clamped to TILT_MIN_DEG..TILT_MAX_DEG)
 *   MOVE <pan> <tilt>    -> OK MOVE <pan> <tilt>      (raw servo angles)
 *   AIM <az> <el>        -> OK AIM <az> <el> pan=<p> tilt=<t>
 *                           Point in real directions: az = azimuth in degrees,
 *                           0 = straight ahead; el = elevation, 0 = horizontal,
 *                           90 = straight up. Converted with the calibration below.
 *   LASER ON|OFF         -> OK LASER ON|OFF
 *   PARK                 -> OK PARK                 (laser off, centre pan, park tilt)
 *   SWEEP                -> OK SWEEP                (demo sweep, laser stays off)
 *   STATUS               -> STATUS pan=.. tilt=.. laser=.. target_pan=.. target_tilt=..
 *   WD <ms>              -> OK WD <ms>              (watchdog timeout, 250..10000 ms)
 *   RELAX                -> OK RELAX                (servos stop pulsing and go limp, laser off)
 *   CAL ON|OFF           -> OK CAL ON|OFF           (calibration mode, see below)
 *
 * Calibration mode (CAL ON): the laser is forced OFF and cannot be switched on,
 * and both axes accept the full servo range 0..180 so the mechanical limits of the
 * mount can be found. Move in small steps; if a servo buzzes, it is against its
 * end stop: go back immediately or send RELAX.
 *
 * Servos are NOT driven after boot (relaxed) until the first move command, so an
 * uncalibrated mount is never pushed into its end stops at power-up.
 * Anything else          -> ERR <reason>
 *
 * Safety (never remove):
 *   - Laser is OFF at boot and on PARK / watchdog / RELAX / CAL.
 *   - Servos stay relaxed after boot until the first move command.
 *   - Tilt is clamped to TILT_MIN_DEG (78) so the tilt servo can never hit the
 *     pan servo (mechanical crash -> stall -> overheating).
 *   - Watchdog: while the laser is ON, no valid command for the watchdog timeout
 *     -> laser off and mount parks. The controller sends PING as a heartbeat.
 */

#include <Servo.h>

// ---------- Pins (Pico GPxx numbers; physical pin in brackets) ----------
const int PIN_PAN   = 14;   // GP14 (pin 19)
const int PIN_TILT  = 15;   // GP15 (pin 20)
const int PIN_LASER = 16;   // GP16 (pin 21): LED for testing, laser via transistor later

// ---------- Servo signal ----------
const int SERVO_MIN_US   = 500;    // pulse width at 0 deg   (tune per servo)
const int SERVO_MAX_US   = 2500;   // pulse width at 180 deg (tune per servo)

Servo servoPan, servoTilt;

// ---------- Mechanical / safety limits (degrees) ----------
// Calibrated on the Adafruit mini pan-tilt kit (2026-11-27), see docs/calibration.md.
// Servo angles with SERVO_MIN_US/SERVO_MAX_US as above; changing those shifts everything.
const float PAN_MIN_DEG   = 5.0;    // 5 deg margin to the servo's internal end stops
const float PAN_MAX_DEG   = 175.0;
const float PAN_CENTER    = 103.0;  // aligned with the base plate of the kit
const float TILT_MIN_DEG  = 78.0;   // HARD LIMIT: pointing straight up; lower = crash into pan servo
const float TILT_MAX_DEG  = 165.0;  // laser exactly horizontal (never aims at the floor)
const float TILT_PARK     = 78.0;   // straight up, resting

// ---------- Direction calibration (servo angle <-> real direction) ----------
const float TILT_ZENITH   = 78.0;   // servo angle for elevation 90 (straight up)
const float TILT_HORIZON  = 165.0;  // servo angle for elevation 0 (horizontal)
const float PAN_AHEAD     = 103.0;  // servo angle for azimuth 0 (straight ahead)
const float PAN_DIR       = 1.0;    // +1 or -1: set so that positive azimuth turns RIGHT
const float SWEEP_EL      = 30.0;   // elevation used by SWEEP
const unsigned long PARK_RELAX_MS = 1500;  // relax servos this long after reaching park
// NOTE: the limits above are servo angles, not real directions. They must be
// re-calibrated for each mount (use CAL ON) so that TILT_MIN..TILT_MAX only
// covers "horizontal and below" and stays inside the mechanical range.

// ---------- Motion ----------
const float MAX_SPEED_DEG_PER_S = 180.0;  // slew-rate limit, avoids current spikes
const unsigned long CONTROL_PERIOD_MS = 20;

// ---------- Watchdog ----------
unsigned long watchdogMs = 5000;   // laser stays on 5 s without commands; change with WD <ms>

float panDeg = PAN_CENTER, tiltDeg = TILT_PARK;        // current commanded position
float targetPan = PAN_CENTER, targetTilt = TILT_PARK;  // where we are heading
bool laserOn = false;
bool sweeping = false;
bool calMode = false;
bool servosAttached = false;
bool parking = false;            // heading to park, relax when there
unsigned long parkReachedMs = 0;

float panMin()  { return calMode ? 0.0f : PAN_MIN_DEG; }
float panMax()  { return calMode ? 180.0f : PAN_MAX_DEG; }
float tiltMin() { return calMode ? 0.0f : TILT_MIN_DEG; }
float tiltMax() { return calMode ? 180.0f : TILT_MAX_DEG; }

float clampf(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

float elToTilt(float el) {
  el = clampf(el, 0.0f, 90.0f);
  return TILT_HORIZON + el / 90.0f * (TILT_ZENITH - TILT_HORIZON);
}
float azToPan(float az) { return PAN_AHEAD + PAN_DIR * az; }

unsigned long lastCommandMs = 0;
unsigned long lastControlMs = 0;
String lineBuf;

// ---------------------------------------------------------------------------

int degToUs(float deg) {
  return (int)(SERVO_MIN_US + (deg / 180.0f) * (SERVO_MAX_US - SERVO_MIN_US) + 0.5f);
}

void writeServos() {
  if (!servosAttached) return;
  servoPan.writeMicroseconds(degToUs(panDeg));
  servoTilt.writeMicroseconds(degToUs(tiltDeg));
}

// Start driving the servos. The position is unknown while relaxed, so jump
// straight to the target instead of slewing from a stale value.
void attachServos() {
  if (servosAttached) return;
  panDeg = targetPan;
  tiltDeg = targetTilt;
  servoPan.attach(PIN_PAN, SERVO_MIN_US, SERVO_MAX_US, degToUs(panDeg));
  servoTilt.attach(PIN_TILT, SERVO_MIN_US, SERVO_MAX_US, degToUs(tiltDeg));
  servosAttached = true;
}

void relaxServos() {
  servoPan.detach();
  servoTilt.detach();
  servosAttached = false;
}

void setLaser(bool on) {
  laserOn = on;
  digitalWrite(PIN_LASER, on ? HIGH : LOW);
}

void park() {
  setLaser(false);
  sweeping = false;
  targetPan = PAN_CENTER;
  targetTilt = TILT_PARK;
  if (!calMode) { attachServos(); parking = true; parkReachedMs = 0; }
}

void printStatus() {
  Serial.printf("STATUS pan=%.1f tilt=%.1f laser=%s target_pan=%.1f target_tilt=%.1f servos=%s cal=%s\n",
                panDeg, tiltDeg, laserOn ? "ON" : "OFF", targetPan, targetTilt,
                servosAttached ? "ON" : "RELAXED", calMode ? "ON" : "OFF");
}

// ---------------------------------------------------------------------------
void handleCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;
  cmd.toUpperCase();

  // Split into up to 3 tokens
  String tok[3];
  int n = 0, start = 0;
  while (n < 3 && start < (int)cmd.length()) {
    int sp = cmd.indexOf(' ', start);
    if (sp < 0) sp = cmd.length();
    if (sp > start) tok[n++] = cmd.substring(start, sp);
    start = sp + 1;
  }

  bool valid = true;

  if (tok[0] == "PING") {
    Serial.println("PONG");
  } else if (tok[0] == "PAN" && n == 2) {
    sweeping = false;
    targetPan = clampf(tok[1].toFloat(), panMin(), panMax());
    parking = false;
    attachServos();
    Serial.printf("OK PAN %.1f\n", targetPan);
  } else if (tok[0] == "TILT" && n == 2) {
    sweeping = false;
    targetTilt = clampf(tok[1].toFloat(), tiltMin(), tiltMax());
    parking = false;
    attachServos();
    Serial.printf("OK TILT %.1f\n", targetTilt);
  } else if (tok[0] == "MOVE" && n == 3) {
    sweeping = false;
    targetPan  = clampf(tok[1].toFloat(), panMin(), panMax());
    parking = false;
    targetTilt = clampf(tok[2].toFloat(), tiltMin(), tiltMax());
    attachServos();
    Serial.printf("OK MOVE %.1f %.1f\n", targetPan, targetTilt);
  } else if (tok[0] == "AIM" && n == 3 && calMode) {
    valid = false;
    Serial.println("ERR AIM is disabled in calibration mode (use PAN/TILT)");
  } else if (tok[0] == "AIM" && n == 3) {
    sweeping = false;
    parking = false;
    targetPan  = clampf(azToPan(tok[1].toFloat()), panMin(), panMax());
    targetTilt = clampf(elToTilt(tok[2].toFloat()), tiltMin(), tiltMax());
    attachServos();
    // report the direction actually reached (after clamping)
    float az = (targetPan - PAN_AHEAD) / PAN_DIR;
    float el = (targetTilt - TILT_HORIZON) / (TILT_ZENITH - TILT_HORIZON) * 90.0f;
    if (fabsf(az) < 0.05f) az = 0.0f;   // avoid printing "-0.0"
    if (fabsf(el) < 0.05f) el = 0.0f;
    Serial.printf("OK AIM %.1f %.1f pan=%.1f tilt=%.1f\n", az, el, targetPan, targetTilt);
  } else if (tok[0] == "LASER" && n == 2 && tok[1] == "ON" && calMode) {
    valid = false;
    Serial.println("ERR laser is locked OFF in calibration mode (CAL OFF first)");
  } else if (tok[0] == "LASER" && n == 2 && (tok[1] == "ON" || tok[1] == "OFF")) {
    setLaser(tok[1] == "ON");
    Serial.printf("OK LASER %s\n", laserOn ? "ON" : "OFF");
  } else if (tok[0] == "PARK") {
    park();
    Serial.println("OK PARK");
  } else if (tok[0] == "SWEEP" && calMode) {
    valid = false;
    Serial.println("ERR SWEEP is disabled in calibration mode");
  } else if (tok[0] == "SWEEP") {
    setLaser(false);
    sweeping = true;
    parking = false;
    attachServos();
    Serial.println("OK SWEEP");
  } else if (tok[0] == "STATUS") {
    printStatus();
  } else if (tok[0] == "RELAX") {
    setLaser(false);
    sweeping = false;
    relaxServos();
    Serial.println("OK RELAX");
  } else if (tok[0] == "CAL" && n == 2 && (tok[1] == "ON" || tok[1] == "OFF")) {
    setLaser(false);
    sweeping = false;
    if (tok[1] == "ON") {
      calMode = true;
      Serial.println("OK CAL ON (laser locked off, full range 0..180, move in small steps)");
    } else {
      calMode = false;
      relaxServos();
      targetPan  = clampf(targetPan,  PAN_MIN_DEG,  PAN_MAX_DEG);
      targetTilt = clampf(targetTilt, TILT_MIN_DEG, TILT_MAX_DEG);
      Serial.println("OK CAL OFF (servos relaxed, normal limits)");
    }
  } else if (tok[0] == "WD" && n == 2) {
    long ms = tok[1].toInt();
    if (ms < 250) ms = 250;
    if (ms > 10000) ms = 10000;
    watchdogMs = (unsigned long)ms;
    Serial.printf("OK WD %lu\n", watchdogMs);
  } else {
    valid = false;
    Serial.printf("ERR unknown or malformed command: %s\n", cmd.c_str());
  }

  if (valid) lastCommandMs = millis();
}

// ---------------------------------------------------------------------------
void setup() {
  pinMode(PIN_LASER, OUTPUT);
  setLaser(false);                       // SAFETY: laser off before anything else

  Serial.begin(115200);
  // Servos stay relaxed until the first move command (see attachServos()).

  lastCommandMs = millis();
  delay(1500);   // give the USB serial port time to appear on the PC
  Serial.println("task6 pan-tilt ready (servos relaxed). Commands: PING PAN TILT MOVE AIM LASER PARK SWEEP STATUS WD RELAX CAL");
}

void loop() {
  // 1. Read serial lines
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (lineBuf.length() > 0) handleCommand(lineBuf);
      lineBuf = "";
    } else if (lineBuf.length() < 64) {
      lineBuf += c;
    }
  }

  unsigned long now = millis();

  // 2. Watchdog: laser on but no valid command recently -> laser off and park
  if (laserOn && now - lastCommandMs > watchdogMs) {
    park();
    Serial.println("WARN watchdog timeout: laser off, parking");
  }

  // 3. Control loop at fixed rate with slew-rate limit
  if (now - lastControlMs >= CONTROL_PERIOD_MS) {
    float dt = (now - lastControlMs) / 1000.0f;
    lastControlMs = now;

    if (sweeping) {
      // Simple back-and-forth demo on pan, fixed safe tilt
      static float dir = 1.0f;
      if (fabsf(targetPan - panDeg) < 0.5f) {
        dir = -dir;
        targetPan = dir > 0 ? PAN_MAX_DEG - 10 : PAN_MIN_DEG + 10;
      }
      targetTilt = elToTilt(SWEEP_EL);
      if (now - lastCommandMs > 30000) { park(); Serial.println("OK SWEEP done"); }
    }

    // Once parked, stop holding position: the mount is balanced pointing up, and an
    // idle servo that keeps pushing only gets warm.
    if (parking && fabsf(panDeg - targetPan) < 0.1f && fabsf(tiltDeg - targetTilt) < 0.1f) {
      if (parkReachedMs == 0) parkReachedMs = now;
      if (now - parkReachedMs > PARK_RELAX_MS) { relaxServos(); parking = false; }
    }

    float maxStep = MAX_SPEED_DEG_PER_S * dt;
    panDeg  += clampf(targetPan  - panDeg,  -maxStep, maxStep);
    tiltDeg += clampf(targetTilt - tiltDeg, -maxStep, maxStep);
    tiltDeg  = clampf(tiltDeg, tiltMin(), tiltMax());   // belt and braces
    writeServos();
  }
}
