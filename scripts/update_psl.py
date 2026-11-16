#!/usr/bin/env python3
"""
scripts/update_psl.py — Tool to parse Mozilla Public Suffix List and update psl.nox.

Downloads `public_suffix_list.dat` from https://publicsuffix.org/list/public_suffix_list.dat,
extracts exact, wildcard (`*.X`), and exception (`!Y`) rules, and updates `_PSL_DATA`,
`_PSL_WILDCARDS`, and `_PSL_EXCEPTIONS` in `psl.nox`.
"""

import sys
import urllib.request
import re

PSL_URL = "https://publicsuffix.org/list/public_suffix_list.dat"

def fetch_psl_data() -> str:
    print(f"Fetching latest Public Suffix List from {PSL_URL}...")
    req = urllib.request.Request(PSL_URL, headers={"User-Agent": "Nova-PSL-Updater/1.1"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")

def _to_ascii_lower(domain: str) -> str:
    try:
        return domain.encode("idna").decode("ascii").lower()
    except Exception:
        return domain.lower()

def parse_rules(raw_text: str) -> tuple[list[str], list[str], list[str]]:
    exact = set()
    wildcards = set()
    exceptions = set()

    for line in raw_text.splitlines():
        line = line.strip()
        if not line or line.startswith("//"):
            continue
        if line.startswith("!"):
            ascii_exc = _to_ascii_lower(line[1:].strip())
            if ascii_exc:
                exceptions.add(ascii_exc)
        elif line.startswith("*."):
            ascii_wild = _to_ascii_lower(line[2:].strip())
            if ascii_wild:
                wildcards.add(ascii_wild)
        else:
            ascii_entry = _to_ascii_lower(line)
            if "." in ascii_entry:
                exact.add(ascii_entry)

    return sorted(exact), sorted(wildcards), sorted(exceptions)

def main():
    apply_mode = "--apply" in sys.argv
    try:
        raw = fetch_psl_data()
    except Exception as e:
        print(f"Warning: Could not fetch from network ({e}).", file=sys.stderr)
        return

    exact, wildcards, exceptions = parse_rules(raw)
    print(f"Parsed {len(exact)} exact, {len(wildcards)} wildcard, and {len(exceptions)} exception PSL rules.")

    exact_str = " " + " ".join(exact) + " "
    wild_str = " " + " ".join(wildcards) + " "
    exc_str = " " + " ".join(exceptions) + " "
    print(f"Total sizes: exact={len(exact_str)}B, wildcards={len(wild_str)}B, exceptions={len(exc_str)}B.")

    if apply_mode:
        psl_nox_path = "psl.nox"
        with open(psl_nox_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(r'_PSL_DATA: str = "[^"]*"', lambda _m: f'_PSL_DATA: str = "{exact_str}"', content, count=1)
        content = re.sub(r'_PSL_WILDCARDS: str = "[^"]*"', lambda _m: f'_PSL_WILDCARDS: str = "{wild_str}"', content, count=1)
        content = re.sub(r'_PSL_EXCEPTIONS: str = "[^"]*"', lambda _m: f'_PSL_EXCEPTIONS: str = "{exc_str}"', content, count=1)

        with open(psl_nox_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Successfully updated {psl_nox_path} with full Mozilla Public Suffix List (exact + wildcard + exception)!")

if __name__ == "__main__":
    main()
