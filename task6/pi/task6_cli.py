#!/usr/bin/env python3
"""
task6_cli.py - talk to the task6 pan-tilt firmware (Raspberry Pi Pico 2 W) over USB serial.

Runs on a laptop now, and later on the Raspberry Pi 5.

Usage:
  python task6_cli.py --list                     # show serial ports
  python task6_cli.py --port COM5                # interactive console
  python task6_cli.py --port COM5 --selftest     # scripted hardware check, saves a log
  python task6_cli.py --sim                      # interactive, no hardware (simulator)
  python task6_cli.py --sim --selftest           # test the whole flow without hardware
  python task6_cli.py --port COM5 --pattern      # aim the laser at a list of directions
  python task6_cli.py --port COM5 --pattern my_points.csv --dwell 2

Interactive commands are sent as-is (PING, PAN 103, MOVE 103 90, LASER ON, PARK, ...).
While the console is open, a heartbeat PING is sent every 300 ms so the firmware
watchdog does not switch the laser off. Type 'quit' to exit (sends PARK first).
"""
import argparse
import datetime
import pathlib
import threading
import time

HEARTBEAT_S = 0.3


# --------------------------------------------------------------------------- #
class SimDevice:
    """Minimal software stand-in for the firmware, same text protocol."""

    PAN_MIN, PAN_MAX, PAN_PARK = 5.0, 175.0, 103.0
    TILT_MIN, TILT_MAX, TILT_PARK = 78.0, 165.0, 78.0
    TILT_ZENITH, TILT_HORIZON, PAN_AHEAD, PAN_DIR = 78.0, 165.0, 103.0, 1.0

    def __init__(self):
        self.pan, self.tilt, self.laser = self.PAN_PARK, self.TILT_PARK, False
        self._out = []
        self._lock = threading.Lock()
        self._out.append("task6 pan-tilt ready (SIMULATOR)")

    def write(self, data: bytes):
        for line in data.decode().splitlines():
            self._handle(line.strip().upper())

    def _reply(self, s):
        with self._lock:
            self._out.append(s)

    def _handle(self, cmd):
        t = cmd.split()
        if not t:
            return
        clamp = lambda v, lo, hi: max(lo, min(hi, v))
        try:
            if t[0] == "PING":
                self._reply("PONG")
            elif t[0] == "PAN" and len(t) == 2:
                self.pan = clamp(float(t[1]), self.PAN_MIN, self.PAN_MAX); self._reply(f"OK PAN {self.pan:.1f}")
            elif t[0] == "TILT" and len(t) == 2:
                self.tilt = clamp(float(t[1]), self.TILT_MIN, self.TILT_MAX); self._reply(f"OK TILT {self.tilt:.1f}")
            elif t[0] == "MOVE" and len(t) == 3:
                self.pan = clamp(float(t[1]), self.PAN_MIN, self.PAN_MAX)
                self.tilt = clamp(float(t[2]), self.TILT_MIN, self.TILT_MAX)
                self._reply(f"OK MOVE {self.pan:.1f} {self.tilt:.1f}")
            elif t[0] == "AIM" and len(t) == 3:
                az, el = float(t[1]), max(0.0, min(90.0, float(t[2])))
                self.pan = clamp(self.PAN_AHEAD + self.PAN_DIR * az, self.PAN_MIN, self.PAN_MAX)
                self.tilt = clamp(self.TILT_HORIZON + el / 90 * (self.TILT_ZENITH - self.TILT_HORIZON),
                                  self.TILT_MIN, self.TILT_MAX)
                az = (self.pan - self.PAN_AHEAD) / self.PAN_DIR
                el = (self.tilt - self.TILT_HORIZON) / (self.TILT_ZENITH - self.TILT_HORIZON) * 90
                az, el = round(az, 1) + 0.0, round(el, 1) + 0.0   # no "-0.0"
                self._reply(f"OK AIM {az:.1f} {el:.1f} pan={self.pan:.1f} tilt={self.tilt:.1f}")
            elif t[0] == "LASER" and len(t) == 2 and t[1] in ("ON", "OFF"):
                self.laser = t[1] == "ON"; self._reply(f"OK LASER {t[1]}")
            elif t[0] == "PARK":
                self.laser, self.pan, self.tilt = False, self.PAN_PARK, self.TILT_PARK; self._reply("OK PARK")
            elif t[0] == "SWEEP":
                self.laser = False; self._reply("OK SWEEP")
            elif t[0] == "STATUS":
                self._reply(f"STATUS pan={self.pan:.1f} tilt={self.tilt:.1f} "
                            f"laser={'ON' if self.laser else 'OFF'} "
                            f"target_pan={self.pan:.1f} target_tilt={self.tilt:.1f}")
            elif t[0] == "WD" and len(t) == 2:
                self._reply(f"OK WD {max(250, min(10000, int(t[1])))}")
            else:
                self._reply(f"ERR unknown or malformed command: {cmd}")
        except ValueError:
            self._reply(f"ERR unknown or malformed command: {cmd}")

    def readline(self) -> bytes:
        time.sleep(0.01)
        with self._lock:
            if self._out:
                return (self._out.pop(0) + "\n").encode()
        return b""

    def close(self):
        pass


# --------------------------------------------------------------------------- #
class Link:
    """Serial link with a reader thread, a response queue and a heartbeat."""

    def __init__(self, dev, echo=True):
        self.dev = dev
        self.echo = echo
        self.lines = []
        self.lock = threading.Lock()
        self.write_lock = threading.Lock()
        self.running = True
        self.heartbeat_on = True
        threading.Thread(target=self._reader, daemon=True).start()
        threading.Thread(target=self._heartbeat, daemon=True).start()

    def _reader(self):
        while self.running:
            raw = self.dev.readline()
            if not raw:
                continue
            line = raw.decode(errors="replace").strip()
            if not line:
                continue
            with self.lock:
                self.lines.append(line)
                del self.lines[:-200]          # keep the buffer bounded
            if self.echo and line != "PONG":
                print(f"  <- {line}")

    def _heartbeat(self):
        while self.running:
            if self.heartbeat_on:
                self.send("PING", quiet=True)
            time.sleep(HEARTBEAT_S)

    def send(self, cmd, quiet=False):
        if not quiet and self.echo:
            print(f"  -> {cmd}")
        with self.write_lock:
            self.dev.write((cmd + "\n").encode())

    def ask(self, cmd, expect_prefix, timeout=1.0):
        """Send a command and wait for a reply starting with expect_prefix."""
        with self.lock:
            self.lines = [l for l in self.lines if l == "PONG"]  # drop stale replies
        t0 = time.time()
        self.send(cmd)
        while time.time() - t0 < timeout:
            with self.lock:
                for i, l in enumerate(self.lines):
                    if l.startswith(expect_prefix) or l.startswith("ERR"):
                        self.lines.pop(i)
                        return l, (time.time() - t0) * 1000
            time.sleep(0.005)
        return None, timeout * 1000

    def close(self):
        try:
            self.send("PARK")
            time.sleep(0.2)
        finally:
            self.running = False
            time.sleep(0.05)
            self.dev.close()


# --------------------------------------------------------------------------- #
def selftest(link, is_sim):
    """Scripted check for the lab session. Returns (passed, log_lines)."""
    steps = [
        ("PING",          "PONG",        "board answers"),
        ("STATUS",        "STATUS",      "status report"),
        ("WD 1000",       "OK WD 1000",  "watchdog set to 1 s"),
        ("MOVE 103 78",   "OK MOVE",     "park position (straight up)"),
        ("PAN 60",        "OK PAN 60",   "pan one way"),
        ("PAN 140",       "OK PAN 140",  "pan other way"),
        ("TILT 95",       "OK TILT 95",  "tilt forward within limit"),
        ("TILT 30",       "OK TILT 78",  "SAFETY: tilt 30 must be clamped to 78"),
        ("TILT 179",      "OK TILT 165", "SAFETY: tilt 179 clamped to 165 (horizontal)"),
        ("AIM 0 0",       "OK AIM 0.0 0.0 pan=103.0 tilt=165.0", "aim straight ahead, horizontal"),
        ("AIM 0 90",      "OK AIM 0.0 90.0 pan=103.0 tilt=78.0", "aim straight up"),
        ("AIM 20 -10",    "OK AIM 20.0 0.0",                     "SAFETY: negative elevation clamped to 0"),
        ("LASER ON",      "OK LASER ON", "laser on"),
        ("LASER OFF",     "OK LASER OFF","laser off"),
        ("FOO",           "ERR",         "bad command is rejected"),
        ("PARK",          "OK PARK",     "park"),
        ("WD 5000",       "OK WD 5000",  "restore 5 s watchdog"),
    ]
    log, ok_all = [], True
    print("\n=== task6 self-test ===")
    for cmd, expect, desc in steps:
        reply, ms = link.ask(cmd, expect.split()[0] if expect != "PONG" else "PONG")
        ok = reply is not None and reply.startswith(expect)
        ok_all &= ok
        row = f"{'PASS' if ok else 'FAIL'}  {cmd:<11} {desc:<40} reply={reply!r}  {ms:.0f} ms"
        print(row)
        log.append(row)
        time.sleep(0.6 if not is_sim else 0.05)   # give servos time to move

    # Watchdog test: laser on, stop heartbeat, laser must go off
    if not is_sim:
        print("Watchdog test: laser ON, heartbeat paused for 2 s ...")
        link.ask("LASER ON", "OK LASER")
        link.heartbeat_on = False
        time.sleep(2.0)
        with link.lock:
            fired = any(l.startswith("WARN watchdog") for l in link.lines)
        link.heartbeat_on = True
        row = f"{'PASS' if fired else 'FAIL'}  watchdog    laser switched off without heartbeat"
        print(row)
        log.append(row)
        ok_all &= fired

    print("=== RESULT:", "ALL PASS" if ok_all else "SOME FAILED", "===\n")
    return ok_all, log


DEFAULT_PATTERN = [  # (azimuth, elevation) in degrees; 0/0 = straight ahead, horizontal
    (0, 10), (-30, 10), (-30, 30), (0, 30), (30, 30), (30, 10), (0, 10), (0, 45),
]


def load_pattern(path):
    """CSV lines 'az,el' (header and # comments allowed)."""
    points = []
    for line in pathlib.Path(path).read_text().splitlines():
        line = line.split("#")[0].strip()
        if not line or line[0].isalpha():
            continue
        az, el = (float(v) for v in line.replace(";", ",").split(",")[:2])
        points.append((az, el))
    return points


def run_pattern(link, points, dwell, is_sim):
    """Aim at each direction, laser on while dwelling there, laser off while moving."""
    print(f"\n=== task6 pattern: {len(points)} points, {dwell:.1f} s each ===")
    log = []
    for i, (az, el) in enumerate(points, 1):
        link.ask("LASER OFF", "OK LASER")
        reply, ms = link.ask(f"AIM {az:g} {el:g}", "OK AIM")
        time.sleep(0.05 if is_sim else 0.8)          # let the servos arrive
        link.ask("LASER ON", "OK LASER")
        row = f"{i:>2}/{len(points)}  az={az:6.1f} el={el:5.1f}  -> {reply}"
        print(row)
        log.append(row)
        time.sleep(0.05 if is_sim else dwell)
    link.ask("LASER OFF", "OK LASER")
    link.ask("PARK", "OK PARK")
    print("=== pattern done, parked ===\n")
    return log


def save_log(log, ok_all, is_sim):
    out_dir = pathlib.Path(__file__).resolve().parent.parent / "docs" / "test-logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = out_dir / f"selftest-{'sim' if is_sim else 'hw'}-{stamp}.txt"
    path.write_text(f"task6 self-test {stamp} ({'simulator' if is_sim else 'hardware'})\n"
                    f"result: {'ALL PASS' if ok_all else 'SOME FAILED'}\n\n" + "\n".join(log) + "\n")
    print(f"Log saved to {path}")


def main():
    ap = argparse.ArgumentParser(description="task6 pan-tilt serial console")
    ap.add_argument("--port", help="serial port, e.g. COM5 or /dev/ttyACM0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--sim", action="store_true", help="use the software simulator")
    ap.add_argument("--selftest", action="store_true", help="run the scripted check")
    ap.add_argument("--list", action="store_true", help="list serial ports")
    ap.add_argument("--pattern", nargs="?", const="default", metavar="CSV",
                    help="aim at a list of az,el points (default pattern if no file given)")
    ap.add_argument("--dwell", type=float, default=2.0, help="seconds per pattern point")
    args = ap.parse_args()

    if args.list:
        from serial.tools import list_ports
        for p in list_ports.comports():
            print(f"{p.device:<14} {p.description}")
        return

    if args.sim:
        dev = SimDevice()
    elif args.port:
        import serial
        dev = serial.Serial(args.port, args.baud, timeout=0.1)
        time.sleep(1.5)            # board may reset when the port opens
        dev.reset_input_buffer()
    else:
        ap.error("give --port PORT, --sim or --list")

    link = Link(dev)
    try:
        if args.pattern:
            pts = DEFAULT_PATTERN if args.pattern == "default" else load_pattern(args.pattern)
            run_pattern(link, pts, args.dwell, args.sim)
            return
        if args.selftest:
            ok_all, log = selftest(link, args.sim)
            save_log(log, ok_all, args.sim)
            return
        print("Connected. Type commands (PING, MOVE 103 90, LASER ON, PARK, ...), 'quit' to exit.")
        while True:
            cmd = input("> ").strip()
            if cmd.lower() in ("quit", "exit"):
                break
            if cmd:
                link.send(cmd)
                time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        link.close()


if __name__ == "__main__":
    main()
