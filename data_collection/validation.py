from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional, Tuple


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]


def _is_non_empty_str(x: Any) -> bool:
    return isinstance(x, str) and x.strip() != ""


def _is_mmss_time(value: Any) -> bool:
    """Accepts 'MM:SS' format (e.g. '30:20'). Seconds must be 0-59."""
    if not isinstance(value, str):
        return False
    parts = value.strip().split(":")
    if len(parts) != 2:
        return False
    mm, ss = parts
    if not (mm.isdigit() and ss.isdigit()):
        return False
    return 0 <= int(ss) <= 59


def _parse_iso_time(value: Any) -> Optional[datetime]:
    """Accepts ISO-like strings: '2026-02-20 14:30:00' or '2026-02-20T14:30:00'."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                pass
    return None


def validate_row(row: Any) -> ValidationResult:
    """
    Validates a single dashboard row [name, time, tag].

    Rules:
      - name: non-empty string
      - time: 'MM:SS' game duration OR ISO datetime string
      - tag:  non-empty string
    """
    errors: List[str] = []

    if not isinstance(row, (list, tuple)) or len(row) < 3:
        return ValidationResult(is_valid=False, errors=["Row must be [name, time, tag]"])

    name, time_val, tag = row[0], row[1], row[2]

    if not _is_non_empty_str(name):
        errors.append("Missing or invalid name")

    if not _is_mmss_time(time_val) and _parse_iso_time(time_val) is None:
        errors.append("Invalid time format (expected MM:SS or ISO datetime)")

    if not _is_non_empty_str(tag):
        errors.append("Missing or invalid tag")

    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def split_valid_invalid_rows(
    rows: List[Any],
) -> Tuple[List[List[Any]], List[List[Any]]]:
    """
    Splits dashboard rows into valid and invalid lists.

    Input rows expected as: [name, time, tag]

    Returns:
      valid_rows:   [[name, time, tag], ...]
      invalid_rows: [[name, time, error_reason], ...]
    """
    valid: List[List[Any]] = []
    invalid: List[List[Any]] = []

    for row in rows:
        result = validate_row(row)

        if result.is_valid:
            valid.append([row[0], row[1], row[2]])
        else:
            safe_name = (
                row[0]
                if isinstance(row, (list, tuple)) and len(row) > 0 and _is_non_empty_str(row[0])
                else "Unknown"
            )

            safe_time = "Unknown"
            if isinstance(row, (list, tuple)) and len(row) > 1:
                if isinstance(row[1], datetime):
                    safe_time = row[1].isoformat(sep=" ")
                elif isinstance(row[1], str):
                    safe_time = row[1]

            invalid.append([safe_name, safe_time, "; ".join(result.errors)])

    return valid, invalid


def validate_after_export(rows: List[Any]) -> Tuple[List[List[Any]], List[List[Any]]]:
    """
    Called immediately after data export. Returns (valid, invalid) rows.
    valid_rows:   [[name, time, tag], ...]
    invalid_rows: [[name, time, error_reason], ...]
    """
    return split_valid_invalid_rows(rows)
