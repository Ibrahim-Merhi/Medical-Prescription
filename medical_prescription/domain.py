"""Pure, framework-independent rules traced to the active exports.

The 24 cells represent selectable nursing slots, not automatic dose orders.
No calculation here recommends a medicine or dose.
"""
import re
from copy import deepcopy

YES = (1, "1", True, "Yes", "yes", "true", "True")
HOURS = tuple(range(10, 24)) + tuple(range(10))
TIMES = tuple(f"{h:02}:00:00" for h in HOURS)
DOSAGE = {"OD": "1-0-0", "BID": "1-0-1", "TID": "1-1-1", "QID": "1-1-1-1",
          "QOD": "1-0-0", "Once": "1-0-0", "STAT": "1-0-0", "Continuous": "1-0-0"}


def yes(value):
    return value in YES


def period_days(value):
    """Match legacy integer/day/week parsing; invalid periods return zero."""
    parts = str(value or "").strip().split()
    try:
        count = int(parts[0])
    except (IndexError, ValueError):
        return 0
    return count * 7 if len(parts) > 1 and parts[1].lower() in ("week", "weeks") else count


def frequency_interval(value):
    value = re.sub(r"\s", "", str(value or "").lower())
    match = re.fullmatch(r"q(\d+)h", value)
    if match:
        return int(match[1])
    return {"od":24,"once":24,"stat":24,"qod":24,"bid":12,"tid":8,"qid":6,
            "continuous":1,"3x/week":24,"2x/week":24,"1x/week":24}.get(value, 0)


def spacing_allowed(time_a, time_b, interval):
    a, b = int(str(time_a).split(":")[0]), int(str(time_b).split(":")[0])
    distance = abs(a-b)
    return distance == 0 or not interval or min(distance, 24-distance) >= interval


def build_grid(items, existing, prescription_date):
    """Retain historical rows verbatim; never overwrite signed data on rebuild.

    Unlike the export, history for removed/stopped medicines is not deleted.
    Keys are item-specific, preventing two orders of one drug from merging.
    """
    result = deepcopy(existing)
    by_key = {}
    for row in result:
        key = row.get("schedule_unique_key")
        if not key or key in by_key:
            raise ValueError("Ambiguous legacy schedule keys require migration reconciliation")
        by_key[key] = row
    seen = set()
    for item in items:
        key = item.get("item_unique_key")
        if not key or key in seen:
            raise ValueError("Each medication order requires a distinct stable key")
        seen.add(key)
        if yes(item.get("stop_change")) or yes(item.get("is_stopped")):
            continue
        if yes(item.get("is_phone_order")) and not yes(item.get("phone_order_approved")):
            continue
        for time in TIMES:
            slot = key + "||" + time
            if slot in by_key:
                continue
            result.append({"item_unique_key":key, "medication":item.get("medication") or item.get("drug_name"),
                           "drug_name":item.get("drug_name") or item.get("medication"),
                           "scheduled_time":time,"scheduled_date":str(prescription_date),
                           "schedule_unique_key":slot,
                           "dosage":item.get("dosage") or DOSAGE.get(item.get("frequency"), "1-0-0"),
                           "double_signature_required":int(yes(item.get("double_signature_required")))})
    return result


def duplication_outcome(item, fully_administered):
    """Return (history status, remaining days), following active duplicate API."""
    if yes(item.get("is_phone_order")) and not yes(item.get("phone_order_approved")):
        return "Pending Phone Order", 0
    if any(yes(item.get(k)) for k in ("is_stopped", "stop_change", "stop_locked")) or item.get("stopped_on"):
        return "Stopped", 0
    once = (str(item.get("frequency") or "").lower().strip() in ("once", "stat")
            or str(item.get("custom_time") or "").lower().strip() in ("over", "once", "stat")
            or str(item.get("dosage") or "").lower().strip() in ("once only", "once", "stat")
            or item.get("allow_duplicate_next_day") in (0, "0"))
    if once:
        return "One-Time Completed", 0
    remaining = period_days(item.get("remaining_period") or item.get("period"))
    remaining -= int(fully_administered)
    return ("Course Completed", 0) if remaining <= 0 else (None, remaining)

