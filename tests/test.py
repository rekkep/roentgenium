from pathlib import Path

import tomllib


def load_entries_from_toml(file_path):
    """Load entries from the specified TOML file."""
    try:
        with open(file_path, "rb") as f:  # MUST be binary
            data = tomllib.load(f)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return []
    except tomllib.TOMLDecodeError as e:
        print(f"TOML decode error: {e}")
        return []

    entries = []
    for group in data.get("group", []):
        print(group)
        entries.extend(group.get("entry", []))

    return entries


# Example usage
config_file_path = Path("entries.toml")
entries = load_entries_from_toml(config_file_path)

# Print the extracted entries
for entry in entries:
    print(f"Name: {entry['name']}")
    print(f"Name is Command: {entry['name_is_command']}")
    print(f"Command: {entry['command']}")
    print("-----")
