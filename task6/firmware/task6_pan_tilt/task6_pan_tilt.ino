/*
 * task6_pan_tilt.ino
 * Task 6 (Group 4, Cloud Computing WS2627): pan-tilt mount with laser, ESP32-C6.
 *
 * Board:     ESP32-C6 (Arduino-ESP32 core 3.x)
 * Libraries: none (servos driven directly with the LEDC peripheral)
 *
 * Serial protocol: plain text lines at 115200 baud, newline-terminated.
 *   PING                 -> PONG
 *   PAN <deg>            -> OK PAN <deg>            (clamped to limits)
 *   TILT <deg>           -> OK TILT <deg>           (clamped, never above TILT_MAX_DEG)
 *   MOVE <pan> <tilt>    -> OK MOVE <pan> <tilt>
 *   LASER ON|OFF         -> OK LASER ON|OFF
 *   PARK                 -> OK PARK                 (laser off, centre pan, park tilt)
 *   SWEEP                -> OK SWEEP                (demo sweep, laser stays off)
 *   STATUS               -> STATUS pan=.. tilt=.. laser=.. target_pan=.. target_tilt=..
 *   WD <ms>              -> OK WD <ms>              (watchdog timeout, 250..10000 ms)
 * Anything else          -> ERR <reason>
 *
 * Safety (never remove):
 *   - Laser is OFF at boot and on PARK / watchdog.
 *   - Tilt is clamped to TILT_MAX_DEG so the laser can never point upward.
 *   - Watchdog: while the laser is ON, no valid command for the watchdog timeout
 *     -> laser off and mount parks. The controller sends PING as a heartbeat.
 */

// ---------- Pins (check against your board's pinout before wiring) ----------
const int PIN_PAN   = 18;
const int PIN_TILT  = 19;
const int PIN_LASER = 20;   // drives the laser module (or an LED for testing)

// ---------- Servo signal ----------
const int SERVO_FREQ_HZ  = 50;     // standard hobby servo: 20 ms period
const int SERVO_RES_BITS = 14;     // 16384 steps per period
const int SERVO_MIN_US   = 500;    // pulse width at 0 deg   (tune per servo)
const int SERVO_MAX_US   = 2500;   // pulse width at 180 deg (tune per servo)

// ---------- Mechanical / safety limits (degrees) ----------
const float PAN_MIN_DEG   = 0.0;
const float PAN_MAX_DEG   = 180.0;
const float PAN_CENTER    = 90.0;
const float TILT_MIN_DEG  = 0.0;
const float TILT_MAX_DEG  = 60.0;  // SAFETY: laser must never point at the sky
const float TILT_PARK     = 20.0;

// ---------- Motion ----------
const float MAX_SPEED_DEG_PER_S = 180.0;  // slew-rate limit, avoids current spikes
const unsigned long CONTROL_PERIOD_MS = 20;

// ---------- Watchdog ----------
unsigned long watchdogMs = 1000;   // change at runtime with WD <ms>

float panDeg = PAN_CENTER, tiltDeg = TILT_PARK;        // current commanded position
float targetPan = PAN_CENTER, targetTilt = TILT_PARK;  // where we are heading
bool laserOn = false;
bool sweeping = false;

unsigned long lastCommandMs = 0;
unsigned long lastControlMs = 0;
String lineBuf;

// ---------------------------------------------------------------------------
float clampf(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

uint32_t degToDuty(float deg) {
  float us = SERVO_MIN_US + (deg / 180.0f) * (SERVO_MAX_US - SERVO_MIN_US);
  const float periodUs = 1000000.0f / SERVO_FREQ_HZ;
  return (uint32_t)(us / periodUs * ((1 << SERVO_RES_BITS) - 1));
}

void writeServos() {
  ledcWrite(PIN_PAN, degToDuty(panDeg));
  ledcWrite(PIN_TILT, degToDuty(tiltDeg));
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
}

void printStatus() {
  Serial.printf("STATUS pan=%.1f tilt=%.1f laser=%s target_pan=%.1f target_tilt=%.1f\n",
                panDeg, tiltDeg, laserOn ? "ON" : "OFF", targetPan, targetTilt);
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
    targetPan = clampf(tok[1].toFloat(), PAN_MIN_DEG, PAN_MAX_DEG);
    Serial.printf("OK PAN %.1f\n", targetPan);
  } else if (tok[0] == "TILT" && n == 2) {
    sweeping = false;
    targetTilt = clampf(tok[1].toFloat(), TILT_MIN_DEG, TILT_MAX_DEG);
    Serial.printf("OK TILT %.1f\n", targetTilt);
  } else if (tok[0] == "MOVE" && n == 3) {
    sweeping = false;
    targetPan  = clampf(tok[1].toFloat(), PAN_MIN_DEG, PAN_MAX_DEG);
    targetTilt = clampf(tok[2].toFloat(), TILT_MIN_DEG, TILT_MAX_DEG);
    Serial.printf("OK MOVE %.1f %.1f\n", targetPan, targetTilt);
  } else if (tok[0] == "LASER" && n == 2 && (tok[1] == "ON" || tok[1] == "OFF")) {
    setLaser(tok[1] == "ON");
    Serial.printf("OK LASER %s\n", laserOn ? "ON" : "OFF");
  } else if (tok[0] == "PARK") {
    park();
    Serial.println("OK PARK");
  } else if (tok[0] == "SWEEP") {
    setLaser(false);
    sweeping = true;
    Serial.println("OK SWEEP");
  } else if (tok[0] == "STATUS") {
    printStatus();
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
  ledcAttach(PIN_PAN, SERVO_FREQ_HZ, SERVO_RES_BITS);
  ledcAttach(PIN_TILT, SERVO_FREQ_HZ, SERVO_RES_BITS);
  writeServos();

  lastCommandMs = millis();
  delay(200);
  Serial.println("task6 pan-tilt ready. Commands: PING PAN TILT MOVE LASER PARK SWEEP STATUS");
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
      targetTilt = TILT_PARK;
      if (now - lastCommandMs > 30000) { park(); Serial.println("OK SWEEP done"); }
    }

    float maxStep = MAX_SPEED_DEG_PER_S * dt;
    panDeg  += clampf(targetPan  - panDeg,  -maxStep, maxStep);
    tiltDeg += clampf(targetTilt - tiltDeg, -maxStep, maxStep);
    tiltDeg  = clampf(tiltDeg, TILT_MIN_DEG, TILT_MAX_DEG);   // belt and braces
    writeServos();
  }
}
