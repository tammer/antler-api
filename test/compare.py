"""
Find records from base_case.json that are not present in new.json (by hubspot_id).
"""
import json
import os


def load_base_case():
    """Load JSON from base_case.json in the current directory."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orig.json")
    with open(path) as f:
        return json.load(f)


def load_new():
    """Load JSON from new.json in the current directory."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "new.json")
    with open(path) as f:
        return json.load(f)


def _to_record_list(data):
    """Normalize JSON data to a list of record dicts."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("results", "data", "contacts", "records"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return list(data.values())[0] if data else []
    return []


def records_not_in_load_full():
    """
    Return all records from base_case.json whose hubspot_id is not
    present in new.json.
    """
    api_data = load_base_case()
    local_data = load_new()
    local_records = _to_record_list(local_data)

    api_records = _to_record_list(api_data)
    if not isinstance(api_records, list):
        api_records = [api_records]

    local_ids = {str(r.get("hubspot_id")) for r in local_records if isinstance(r, dict) and r.get("hubspot_id") is not None}

    return [r for r in api_records if isinstance(r, dict) and str(r.get("hubspot_id", "")) not in local_ids]


if __name__ == "__main__":
    missing = records_not_in_load_full()
    print(json.dumps(missing, indent=2))
    print(f"\nTotal: {len(missing)} record(s) in base_case.json not in new.json")
