"""Deduplicate contacts by name, keeping first occurrence."""


def deduplicate_contacts(contacts: list[dict]) -> list[dict]:
    """Return contacts with duplicates removed, keeping first occurrence per name."""
    seen: set[str] = set()
    result: list[dict] = []
    for c in contacts:
        name = c.get("name", "")
        if name not in seen:
            seen.add(name)
            result.append(c)
    return result
