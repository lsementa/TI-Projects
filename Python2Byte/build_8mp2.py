"""Build a TI compiled Python module (.8mp2) plus a launcher .py.

Put the .py file in the input folder, set the two names below and
Run. The output folder gets:
    <NEW_MOD_NAME>.8mp2  the app compiled to MicroPython bytecode
    <NEW_PY_NAME>.py     a small launcher that imports the module
Send both to the calculator and run <NEW_PY_NAME> from the Python app.

Needs MicroPython 1.17's compiler (.mpy format version 5 with the
-mcache-lookup-bc option, which the calculator requires):
    pip install mpy-cross==1.17
"""
import os
import shutil
import struct
import subprocess
import sys
import tempfile

# ---- Edit these -----------------------------------------------------------

NEW_PY_NAME = "TEST"            # launcher name
NEW_MOD_NAME = "TESTM"          # module name
OPTIMIZE = True                 # True = compile with -O3: about 7% smaller and
                                # asserts removed, but errors on the calculator
                                # no longer show line numbers. Leave False while
                                # debugging.

# ---------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(HERE, "input")
OUTPUT_DIR = os.path.join(HERE, "output")

MAGIC = bytes.fromhex("1302d820")


def cbor_head(major, n):
    """CBOR item header (major type 0 = uint, 2 = bytes, 3 = text)."""
    m = major << 5
    if n < 24:
        return bytes([m | n])
    if n < 0x100:
        return bytes([m | 24, n])
    if n < 0x10000:
        return bytes([m | 25]) + struct.pack(">H", n)
    return bytes([m | 26]) + struct.pack(">I", n)


def cbor_text(s):
    b = s.encode()
    return cbor_head(3, len(b)) + b


def cbor_bytes(b):
    return cbor_head(2, len(b)) + b


def ti_name(name):
    """Calculator-side file name: a little-endian word per character,
    A-Z = 0xE800.., 0-9 = 0xE401.., then a 0 word."""
    out = b""
    for ch in name:
        w = 0xE800 + ord(ch) - 65 if ch.isalpha() else 0xE401 + ord(ch) - 48
        out += struct.pack("<H", w)
    return out + b"\x00\x00"


def evo_checksum(body):
    """XOR of the little-endian 16-bit words of the file, minus its last few
    bytes (same algorithm as PNG2Sprite; matches TI's own .8mp2 files)."""
    adjusted = len(body) - 3
    words = adjusted >> 1
    if adjusted & 1 and words > 0:
        words -= 1
    c = 0
    for i in range(words):
        c ^= body[2 * i] | (body[2 * i + 1] << 8)
    return c & 0xFFFF


def section(kind, body):
    return struct.pack("<HH", len(body), kind << 8) + body + b"\x00"


def build_payload(name, mpy, menu=b""):
    body = name.encode() + b"\x00" + section(1, menu) + section(2, mpy)
    total = 12 + len(body)
    return MAGIC + struct.pack("<II", total, len(name)) + body


def build_8mp2(name, mpy, menu=b""):
    payload = build_payload(name, mpy, menu)
    meta = (b"\xbf" + cbor_text("type") + cbor_head(0, 18)
            + cbor_text("version") + cbor_head(0, 1)
            + cbor_text("flags") + cbor_head(0, 1)
            + cbor_text("name") + cbor_bytes(ti_name(name)) + b"\xff")
    body = (b"\xbf" + cbor_text("metaData") + meta
            + cbor_text("version") + cbor_head(0, 1)
            + cbor_text("size") + cbor_head(0, len(payload))
            + cbor_text("data") + cbor_bytes(payload) + b"\xff")
    return body + evo_checksum(body).to_bytes(2, "big")


# .mpy header TI's modules use: 'M', version 5, flags 3 (map lookups cached
# in bytecode + unicode strings), 31-bit small ints.
MPY_HEADER = b"M\x05\x03\x1f"
MPY_FLAGS = ["-mcache-lookup-bc", "-msmall-int-bits=31"]


def find_mpy_cross():
    exe = shutil.which("mpy-cross")
    if exe:
        cmd = [exe]
    else:
        try:
            import mpy_cross  # noqa: F401
        except ImportError:
            sys.exit("mpy-cross not found. Install it with:\n"
                     "    pip install mpy-cross==1.17")
        cmd = [sys.executable, "-m", "mpy_cross"]
    ver = subprocess.run(cmd + ["--version"], capture_output=True, text=True)
    if "mpy v5" not in ver.stdout:
        sys.exit("Wrong mpy-cross version (%s). Install the right one with:\n"
                 "    pip install mpy-cross==1.17" % ver.stdout.strip())
    return cmd


def compile_mpy(src_path, module):
    """Compile src_path as <module>.py so the bytecode carries that name."""
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copyfile(src_path, os.path.join(tmp, module + ".py"))
        flags = MPY_FLAGS + (["-O3"] if OPTIMIZE else [])
        subprocess.run(find_mpy_cross() + flags + [module + ".py"],
                       cwd=tmp, check=True)
        with open(os.path.join(tmp, module + ".mpy"), "rb") as f:
            mpy = f.read()
    if mpy[:4] != MPY_HEADER:
        sys.exit(".mpy header is %s, the calculator needs %s"
                 % (mpy[:4].hex(" "), MPY_HEADER.hex(" ")))
    return mpy


def find_source():
    """The .py in input/: the only one, or the one named NEW_PY_NAME.py."""
    files = sorted(f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".py"))
    if not files:
        sys.exit("No .py file in " + INPUT_DIR)
    if len(files) == 1:
        return os.path.join(INPUT_DIR, files[0])
    for f in files:
        if f.lower() == NEW_PY_NAME.lower() + ".py":
            return os.path.join(INPUT_DIR, f)
    sys.exit("Several .py files in input (%s); keep one, or name the one to "
             "build %s.py" % (", ".join(files), NEW_PY_NAME))


LAUNCHER = '''try:
 import {mod}
except ImportError as e:
 if '{mod}' not in str(e):raise
 print("{mod}.8mp2 is missing.")
 print("Send it to the calculator.")
'''


def main():
    module = NEW_MOD_NAME.upper()
    if (not module.isascii() or not module.isalnum() or len(module) > 8
            or not module[0].isalpha()):
        sys.exit("NEW_MOD_NAME must be 1-8 characters A-Z/0-9, starting "
                 "with a letter: " + NEW_MOD_NAME)
    if module == NEW_PY_NAME.upper():
        sys.exit("NEW_PY_NAME and NEW_MOD_NAME must be different")

    src = find_source()
    print("Compiling", src, "as", module, "(-O3)" if OPTIMIZE else "")
    mpy = compile_mpy(src, module)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_8mp2 = os.path.join(OUTPUT_DIR, module + ".8mp2")
    with open(out_8mp2, "wb") as f:
        f.write(build_8mp2(module, mpy))
    out_py = os.path.join(OUTPUT_DIR, NEW_PY_NAME + ".py")
    with open(out_py, "w", newline="\n") as f:
        f.write(LAUNCHER.format(mod=module))
    print("Wrote", out_8mp2)
    print("Wrote", out_py)


if __name__ == "__main__":
    main()
