#!/usr/bin/env python3
"""Encrypt (or decrypt) the My Day data. Same lock format as Sharma AR / P&L.

The live page only reads docs/day.enc.json. The plain day files live in private/
(in .gitignore, never commit or upload them), in the same layout the page used to have:

  private/data.json              today's route (stops, inspections, start ...)
  private/tasks.json             today's office tasks
  private/archive/<date>.json    {"data": ..., "tasks": ...} for each saved day
  private/archive/index.json     {"liveDate": ..., "days": [{date, dayLabel}, ...]}

  Decrypt for editing: python3 tools/encrypt.py --decrypt   (docs/day.enc.json -> private/)
  Encrypt (default):   python3 tools/encrypt.py             (private/ -> docs/day.enc.json)

The code comes from the SHARMA_PASSCODE environment variable, or a hidden prompt.
It is never written to disk, printed or logged.

Format: sharma-enc-v1. AES-GCM 256, key = PBKDF2-HMAC-SHA256(code, random 16-byte salt,
600,000+ iterations), random 12-byte IV, fresh salt and IV on every run.

Needs: pip install cryptography
"""
import argparse, base64, getpass, glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ITERATIONS = 600_000
FORMAT = "sharma-enc-v1"

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except ImportError:
    sys.exit("Missing package: pip install cryptography")


def die(msg):
    sys.exit("ERROR: " + msg)


def get_code(confirm):
    code = os.environ.get("SHARMA_PASSCODE")
    if code is None:
        if not sys.stdin.isatty():
            die("set SHARMA_PASSCODE or run in a terminal to be prompted")
        code = getpass.getpass("Code: ")
        if confirm and getpass.getpass("Code again: ") != code:
            die("codes did not match")
    code = code.strip()
    if not code:
        die("empty code")
    return code


def derive(code, salt, iterations):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations).derive(code.encode("utf-8"))


def b64(b):
    return base64.b64encode(b).decode("ascii")


def decrypt_env(env, code):
    if env.get("format") != FORMAT or env.get("kdf") != "PBKDF2-SHA256" or env.get("cipher") != "AES-GCM-256":
        die("not a %s file" % FORMAT)
    key = derive(code, base64.b64decode(env["salt"]), int(env["iterations"]))
    try:
        pt = AESGCM(key).decrypt(base64.b64decode(env["iv"]), base64.b64decode(env["ciphertext"]), None)
    except Exception:
        die("Wrong code (or the file is damaged)")
    return json.loads(pt.decode("utf-8"))


def load(path, default=None):
    if not os.path.exists(path):
        if default is not None:
            return default
        die("missing " + path)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")


def bundle(plain):
    data = load(os.path.join(plain, "data.json"))
    tasks = load(os.path.join(plain, "tasks.json"), {"date": data.get("date"), "tasks": []})
    index = load(os.path.join(plain, "archive", "index.json"), {"liveDate": data.get("date"), "days": []})
    days = {}
    for p in sorted(glob.glob(os.path.join(plain, "archive", "*.json"))):
        name = os.path.splitext(os.path.basename(p))[0]
        if name != "index":
            days[name] = load(p)
    return {"bundle": "sharma-my-day-v1", "live": {"data": data, "tasks": tasks}, "index": index, "days": days}


def unbundle(b, plain):
    dump(b["live"]["data"], os.path.join(plain, "data.json"))
    dump(b["live"].get("tasks") or {"tasks": []}, os.path.join(plain, "tasks.json"))
    dump(b.get("index") or {"days": []}, os.path.join(plain, "archive", "index.json"))
    for name, day in (b.get("days") or {}).items():
        dump(day, os.path.join(plain, "archive", name + ".json"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--decrypt", action="store_true", help="docs/day.enc.json -> plain files in private/")
    ap.add_argument("--plain", default=os.path.join(ROOT, "private"))
    ap.add_argument("--enc", default=os.path.join(ROOT, "docs", "day.enc.json"))
    ap.add_argument("--iterations", type=int, default=ITERATIONS)
    a = ap.parse_args()

    if a.decrypt:
        b = decrypt_env(load(a.enc), get_code(False))
        unbundle(b, a.plain)
        print("Wrote plain files to %s (local only; never commit them)." % a.plain)
        return

    if a.iterations < 600_000:
        die("iterations must be 600000 or more")
    data = bundle(a.plain)
    code = get_code(True)
    salt, iv = os.urandom(16), os.urandom(12)
    key = derive(code, salt, a.iterations)
    pt = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    env = {"format": FORMAT, "kdf": "PBKDF2-SHA256", "hash": "SHA-256", "iterations": a.iterations,
           "cipher": "AES-GCM-256", "salt": b64(salt), "iv": b64(iv), "ciphertext": b64(AESGCM(key).encrypt(iv, pt, None))}
    if decrypt_env(env, code) != data:
        die("round-trip check failed; nothing was written")
    dump(env, a.enc)
    print("Wrote %s (%d saved days). Commit only this file." % (a.enc, len(data["days"])))


if __name__ == "__main__":
    main()
