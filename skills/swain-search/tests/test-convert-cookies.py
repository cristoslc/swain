#!/usr/bin/env python3
"""Tests for convert-cookies.py — cookie format conversion."""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONVERT = (SCRIPT_DIR / "../scripts/convert-cookies.py").resolve()
PASS = 0
FAIL = 0


def assert_conversion(label: str, input_json: str, expected_lines: list[str]) -> None:
    global PASS, FAIL
    result = subprocess.run(
        ["python3", str(CONVERT)],
        input=input_json,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        FAIL += 1
        print(f"  FAIL: {label} — exit code {result.returncode}: {result.stderr.strip()}")
        return
    output_lines = [l for l in result.stdout.strip().split("\n") if l and not l.startswith("#")]
    for expected in expected_lines:
        if expected in output_lines:
            PASS += 1
            print(f"  PASS: {label} — found: {expected}")
        else:
            FAIL += 1
            print(f"  FAIL: {label} — expected line not in output: {expected}")


def assert_no_secrets(label: str, input_json: str) -> None:
    global PASS, FAIL
    result = subprocess.run(
        ["python3", str(CONVERT)],
        input=input_json,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        FAIL += 1
        print(f"  FAIL: {label} — exit code {result.returncode}")
        return
    # Cookie secret values are decoded, not percent-encoded, in output
    output = result.stdout
    if "%7B" in output or "%22" in output or "%3A" in output:
        FAIL += 1
        print(f"  FAIL: {label} — percent-encoded values retained in output")
    else:
        PASS += 1
        print(f"  PASS: {label} — values are URL-decoded")


def assert_host_only_flag(label: str, input_json: str, expected_flag_is_true: bool) -> None:
    global PASS, FAIL
    result = subprocess.run(
        ["python3", str(CONVERT)],
        input=input_json,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        FAIL += 1
        print(f"  FAIL: {label} — exit code {result.returncode}")
        return
    # Netscape flag column is index 1 (0-based). TRUE means subdomain matching allowed.
    for line in result.stdout.strip().split("\n"):
        if line.startswith("#") or not line.strip():
            continue
        fields = line.split("\t")
        flag = fields[1]
        if (expected_flag_is_true and flag == "TRUE") or (not expected_flag_is_true and flag == "FALSE"):
            PASS += 1
            print(f"  PASS: {label} — flag is {'TRUE' if expected_flag_is_true else 'FALSE'}")
        else:
            FAIL += 1
            print(f"  FAIL: {label} — expected {'TRUE' if expected_flag_is_true else 'FALSE'}, got {flag}")
        break


def assert_secure_flag(label: str, input_json: str, expected_is_secure: bool) -> None:
    global PASS, FAIL
    result = subprocess.run(
        ["python3", str(CONVERT)],
        input=input_json,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        FAIL += 1
        print(f"  FAIL: {label} — exit code {result.returncode}")
        return
    for line in result.stdout.strip().split("\n"):
        if line.startswith("#") or not line.strip():
            continue
        fields = line.split("\t")
        secure = fields[3]
        if (expected_is_secure and secure == "TRUE") or (not expected_is_secure and secure == "FALSE"):
            PASS += 1
            print(f"  PASS: {label} — secure is {'TRUE' if expected_is_secure else 'FALSE'}")
        else:
            FAIL += 1
            print(f"  FAIL: {label} — expected {'TRUE' if expected_is_secure else 'FALSE'}, got {secure}")
        break


print("=== convert-cookies.py Tests ===")
print(f"Script: {CONVERT}")
print()

# AC1: Standard cookie with percent-encoded value is URL-decoded
print("--- AC1: Percent-encoded values are URL-decoded ---")
assert_no_secrets(
    "AC1: decode",
    """[{"Host raw":"https://www.example.com/","Name raw":"session","Path raw":"/","Content raw":"%7B%22key%22%3A%22value%22%7D","Expires raw":"1800000000","Send for raw":"true","This domain only raw":"true"}]""",
)

assert_conversion(
    "AC1: decoded value in output",
    """[{"Host raw":"https://www.example.com/","Name raw":"session","Path raw":"/","Content raw":"%7B%22key%22%3A%22value%22%7D","Expires raw":"1800000000","Send for raw":"true","This domain only raw":"true"}]""",
    ['www.example.com\tFALSE\t/\tTRUE\t1800000000\tsession\t{"key":"value"}'],
)

# AC2: Host-only flag maps correctly
print("--- AC2: Host-only cookie gets FALSE flag, subdomain cookie gets TRUE flag ---")
assert_host_only_flag(
    "AC2: host-only (This domain only raw=true)",
    """[{"Host raw":"https://www.example.com/","Name raw":"test","Path raw":"/","Content raw":"val","Expires raw":"0","Send for raw":"true","This domain only raw":"true"}]""",
    expected_flag_is_true=False,
)

assert_host_only_flag(
    "AC2: subdomain (This domain only raw=false)",
    """[{"Host raw":"https://www.example.com/","Name raw":"test","Path raw":"/","Content raw":"val","Expires raw":"0","Send for raw":"true","This domain only raw":"false"}]""",
    expected_flag_is_true=True,
)

# AC3: Secure flag maps correctly
print("--- AC3: Send for raw=true maps to secure TRUE ---")
assert_secure_flag(
    "AC3: secure",
    """[{"Host raw":"https://www.example.com/","Name raw":"test","Path raw":"/","Content raw":"val","Expires raw":"0","Send for raw":"true","This domain only raw":"true"}]""",
    expected_is_secure=True,
)

assert_secure_flag(
    "AC3: not secure",
    """[{"Host raw":"http://www.example.com/","Name raw":"test","Path raw":"/","Content raw":"val","Expires raw":"0","Send for raw":"false","This domain only raw":"true"}]""",
    expected_is_secure=False,
)

# AC4: Multiple cookies produce multiple output lines
print("--- AC4: Multiple cookies produce multiple lines ---")
result = subprocess.run(
    ["python3", str(CONVERT)],
    input="""[
        {"Host raw":"https://www.example.com/","Name raw":"a","Path raw":"/","Content raw":"1","Expires raw":"0","Send for raw":"true","This domain only raw":"true"},
        {"Host raw":"https://www.example.com/","Name raw":"b","Path raw":"/some","Content raw":"2","Expires raw":"100","Send for raw":"false","This domain only raw":"true"}
    ]""",
    capture_output=True,
    text=True,
)
cookie_lines = [l for l in result.stdout.strip().split("\n") if l and not l.startswith("#")]
if len(cookie_lines) == 2:
    PASS += 1
    print("  PASS: AC4: 2 cookie lines in output")
else:
    FAIL += 1
    print(f"  FAIL: AC4: expected 2 lines, got {len(cookie_lines)}")

# AC5: Protocol prefix is stripped from domain
print("--- AC5: Protocol prefix stripped from host ---")
result = subprocess.run(
    ["python3", str(CONVERT)],
    input="""[{"Host raw":"https://sub.example.com/","Name raw":"t","Path raw":"/","Content raw":"v","Expires raw":"0","Send for raw":"true","This domain only raw":"true"}]""",
    capture_output=True,
    text=True,
)
if "https://" not in result.stdout:
    PASS += 1
    print("  PASS: AC5: no https:// in domain field")
else:
    FAIL += 1
    print(f"  FAIL: AC5: protocol prefix present in output")

# AC6: Subdomain cookie gets leading dot
print("--- AC6: Non-host-only cookie gets leading dot ---")
result = subprocess.run(
    ["python3", str(CONVERT)],
    input="""[{"Host raw":"https://www.example.com/","Name raw":"t","Path raw":"/","Content raw":"v","Expires raw":"0","Send for raw":"true","This domain only raw":"false"}]""",
    capture_output=True,
    text=True,
)
for line in result.stdout.strip().split("\n"):
    if line.startswith("#") or not line.strip():
        continue
    domain = line.split("\t")[0]
    if domain == ".www.example.com":
        PASS += 1
        print("  PASS: AC6: domain has leading dot: .www.example.com")
    else:
        FAIL += 1
        print(f"  FAIL: AC6: expected .www.example.com, got {domain}")
    break

print()
print(f"=== Results: {PASS} passed, {FAIL} failed ===")
sys.exit(0 if FAIL == 0 else 1)
