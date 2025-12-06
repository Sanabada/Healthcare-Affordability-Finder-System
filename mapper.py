#!/usr/bin/env python
"""
Healthcare charge master cleaning mapper for Hadoop Streaming.

Reads raw hospital charge CSVs from stdin and writes cleaned rows to stdout.
Each output row has exactly 12 columns in this order:

  1. description
  2. code_1
  3. code_1_type
  4. code_2
  5. code_2_type
  6. code_3
  7. setting
  8. standard_charge_gross
  9. standard_charge_discounted_cash
 10. payer_name
 11. plan_name
 12. hospital_name

This script is designed to be used as a Hadoop Streaming mapper:
  -mapper healthcare_clean_mapper.py -reducer NONE
"""

from __future__ import print_function

import sys
import os
import csv
import re


# Get the current input filename from Hadoop Streaming environment
INPUT_FILE = (
    os.environ.get("map_input_file")
    or os.environ.get("mapreduce_map_input_file")
    or ""
)
SOURCE_NAME = os.path.splitext(os.path.basename(INPUT_FILE))[0] if INPUT_FILE else "unknown"


def clean_money(x):
    """Normalize money-like fields: strip $, commas, and common NA markers."""
    if x is None:
        return ""
    x = x.strip().replace("$", "").replace(",", "")
    if x.lower() in ("na", "n/a", "null", "nan", ""):
        return ""
    return x


def clean_code(x):
    """Normalize codes: trim, remove spaces, and uppercase."""
    if x is None:
        return ""
    x = re.sub(r"\s+", "", x.strip())
    return x.upper()


def clean_text(x):
    """Normalize free text: trim and collapse internal whitespace."""
    if x is None:
        return ""
    return re.sub(r"\s+", " ", x.strip())


def main():
    reader = csv.reader(sys.stdin)
    writer = csv.writer(sys.stdout, lineterminator="\n")

    for row in reader:
        # Skip fully empty rows
        if not row or all((c or "").strip() == "" for c in row):
            continue

        full_line = ",".join(row)
        low_full = full_line.lower()

        # Skip file-level metadata / disclaimer lines
        if "hospital_name,last_updated_on" in low_full:
            continue
        if "to the best of its knowledge" in low_full:
            continue
        if "license_number|ma" in low_full:
            continue

        # Skip header lines (first column is "description")
        first = (row[0] or "").strip().lower()
        if first == "description":
            continue

        # Ensure exactly 12 columns by padding or truncating
        if len(row) < 12:
            row = row + [""] * (12 - len(row))
        elif len(row) > 12:
            row = row[:12]

        # Positional mapping to the canonical 12-column schema
        (
            description,
            code_1,
            code_1_type,
            code_2,
            code_2_type,
            code_3,
            setting,
            standard_charge_gross,
            standard_charge_discounted_cash,
            payer_name,
            plan_name,
            hospital_name,
        ) = [(c if c is not None else "") for c in row]

        # Core cleaning logic
        description = clean_text(description)
        code_1 = clean_code(code_1)
        code_1_type = clean_text(code_1_type)
        code_2 = clean_code(code_2)
        code_2_type = clean_text(code_2_type)
        code_3 = clean_code(code_3)
        setting = clean_text(setting).upper()

        standard_charge_gross = clean_money(standard_charge_gross)
        standard_charge_discounted_cash = clean_money(standard_charge_discounted_cash)

        payer_name = clean_text(payer_name)
        plan_name = clean_text(plan_name)
        hospital_name = clean_text(hospital_name)

        # If hospital_name is missing or looks like a unit, fall back to file name
        if not hospital_name or hospital_name.upper() in {"ML", "UN", "UNIT", "EA", "EACH"}:
            hospital_name = SOURCE_NAME

        # Drop rows with no description or no price info
        if not description:
            continue
        if not standard_charge_gross and not standard_charge_discounted_cash:
            continue

        out_row = [
            description,
            code_1,
            code_1_type,
            code_2,
            code_2_type,
            code_3,
            setting,
            standard_charge_gross,
            standard_charge_discounted_cash,
            payer_name,
            plan_name,
            hospital_name,
        ]
        writer.writerow(out_row)


if __name__ == "__main__":
    main()
