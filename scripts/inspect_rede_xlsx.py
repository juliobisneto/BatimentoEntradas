#!/usr/bin/env python3
"""
Inspect the Rede Excel file: list sheets and columns.
Run from project root: python scripts/inspect_rede_xlsx.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.acquirer_parser import inspect_xlsx

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "AcqImports")
PATTERN = "Rede"
path = None
for f in os.listdir(DIR):
    if PATTERN in f and f.endswith(".xlsx"):
        path = os.path.join(DIR, f)
        break
if not path or not os.path.isfile(path):
    print(f"No Rede .xlsx found in {DIR}")
    sys.exit(1)

with open(path, "rb") as f:
    content = f.read()
info = inspect_xlsx(content)
print(json.dumps(info, indent=2, ensure_ascii=False, default=str))
