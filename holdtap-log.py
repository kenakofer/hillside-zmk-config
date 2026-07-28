#!/usr/bin/env python3
"""Capture ZMK hold-tap decisions from the keyboard's USB console.

Needs only pyserial. The Hillside exposes an ACL-granted /dev/ttyACM*, so no
sudo and no dialout membership required.

    ./holdtap-log.py                 # live, hold-tap lines only
    ./holdtap-log.py -a              # every log line
    ./holdtap-log.py -o timing.log   # also append raw lines to a file

Each hold-tap decision prints as:

    +112ms  pos 20  HOLD  (balanced / other-key-down)

where the delta is the gap since the previous key event -- the number to
compare against require-prior-idle-ms. A HOLD in the middle of a word you
meant to type straight through is a misfire, and "pos" names the exact key.
"""

import argparse
import glob
import re
import sys
import time

try:
    import serial
except ImportError:
    sys.exit("pyserial missing: pip install --user pyserial")

# strip the ANSI colour wrappers ZMK emits around each log line
ANSI = re.compile(r"\x1b\[[0-9;]*m")
TS = re.compile(r"^\[(\d+):(\d+):(\d+)\.(\d+)")
DECIDED = re.compile(r"decide_hold_tap: (\d+) decided (\S+) \((\S+) decision moment (\S+)\)")
PRESSED = re.compile(r"on_hold_tap_binding_pressed: (\d+) new undecided")
POSITION = re.compile(r"position: (\d+), pressed: (true|false)")


def stamp_ms(line):
    m = TS.match(line)
    if not m:
        return None
    h, mi, s, frac = m.groups()
    # ZMK prints microseconds with a comma separator; take the ms part
    return ((int(h) * 3600 + int(mi) * 60 + int(s)) * 1000) + int(frac[:3])


def find_port(explicit):
    if explicit:
        return explicit
    ports = sorted(glob.glob("/dev/ttyACM*"))
    if not ports:
        sys.exit("no /dev/ttyACM* found -- is the left half plugged in?")
    return ports[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", help="serial device (default: first ttyACM*)")
    ap.add_argument("-b", "--baud", type=int, default=115200)
    ap.add_argument("-a", "--all", action="store_true", help="show every log line")
    ap.add_argument("-o", "--out", help="append raw lines to this file")
    args = ap.parse_args()

    port = find_port(args.port)
    try:
        ser = serial.Serial(port, args.baud, timeout=1)
    except serial.SerialException as e:
        sys.exit(f"could not open {port}: {e}")

    sink = open(args.out, "a") if args.out else None
    print(f"# reading {port} -- Ctrl-C to stop", file=sys.stderr)

    last_key_ms = None
    holds = taps = 0
    try:
        while True:
            raw = ser.readline()
            if not raw:
                continue
            line = ANSI.sub("", raw.decode("utf-8", "replace")).rstrip()
            if not line:
                continue
            if sink:
                sink.write(line + "\n")
                sink.flush()
            if args.all:
                print(line)

            now = stamp_ms(line)

            # any physical key-down refreshes the "previous keystroke" clock
            pm = POSITION.search(line)
            if pm and pm.group(2) == "true" and now is not None:
                if not DECIDED.search(line):
                    last_key_ms = now

            d = DECIDED.search(line)
            if d and not args.all:
                pos, status, flavor, moment = d.groups()
                delta = ""
                if now is not None and last_key_ms is not None:
                    gap = now - last_key_ms
                    if 0 <= gap < 5000:
                        delta = f"+{gap:4d}ms"
                if status.startswith("hold"):
                    holds += 1
                    mark = "\033[31mHOLD\033[0m"
                else:
                    taps += 1
                    mark = "tap "
                print(f"{delta:>8}  pos {pos:>2}  {mark}  ({flavor} / {moment})")
    except KeyboardInterrupt:
        print(f"\n# {holds} hold, {taps} tap", file=sys.stderr)
    finally:
        if sink:
            sink.close()


if __name__ == "__main__":
    main()
