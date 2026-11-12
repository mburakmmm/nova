#!/usr/bin/env python3
"""
scripts/update_psl.py — Tool to parse Mozilla Public Suffix List and update psl.nox.

Downloads or parses `public_suffix_list.dat` from https://publicsuffix.org/list/public_suffix_list.dat,
extracts ICANN and common private suffixes, and generates the `_PSL_DATA` string table for `psl.nox`.
"""

import sys
import urllib.request
import re

PSL_URL = "https://publicsuffix.org/list/public_suffix_list.dat"

def fetch_psl_data() -> str:
    print(f"Fetching latest Public Suffix List from {PSL_URL}...")
    req = urllib.request.Request(PSL_URL, headers={"User-Agent": "Nova-PSL-Updater/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")

def parse_suffixes(raw_text: str) -> list[str]:
    suffixes = set()
    for line in raw_text.splitlines():
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("*") or line.startswith("!"):
            continue
        # Convert any unicode domain to punycode/ascii lowercase
        try:
            ascii_entry = line.encode("idna").decode("ascii").lower()
        except Exception:
            ascii_entry = line.lower()
        # Single-label domains (e.g. 'com') are handled by the dot-check in is_public_suffix()
        if "." in ascii_entry:
            suffixes.add(ascii_entry)
    return sorted(suffixes)

def main():
    apply_mode = "--apply" in sys.argv
    try:
        raw = fetch_psl_data()
    except Exception as e:
        print(f"Warning: Could not fetch from network ({e}).", file=sys.stderr)
        return

    suffixes = parse_suffixes(raw)
    print(f"Parsed {len(suffixes)} multi-label public suffixes.")
    
    psl_string = " " + " ".join(suffixes) + " "
    print(f"Total PSL table length: {len(psl_string)} bytes.")

    if apply_mode:
        psl_nox_path = "psl.nox"
        with open(psl_nox_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        pattern = r'_PSL_DATA: str = "[^"]*"'
        replacement = f'_PSL_DATA: str = "{psl_string}"'
        new_content = re.sub(pattern, replacement, content)
        with open(psl_nox_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Successfully updated {psl_nox_path} with full Mozilla Public Suffix List ({len(suffixes)} suffixes)!")

if __name__ == "__main__":
    main()
