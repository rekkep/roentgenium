from pathlib import Path
from subprocess import run as run_subprocess

import tomllib


class Group(object):
    def __init__(self, group):
        self.name = group["name"]
        self.description = group["description"]
        self.entries: list[Entry] = self.add_entries(group["entry"])
        self.input_fields: list[InputField] = self.add_input_field(group["input_field"])

    def add_entries(self, entries):
        group_entries = []
        if not isinstance(entries, list):
            group_entries = [entries]

        for entry in entries:
            new_entry = Entry(entry)
            group_entries.append(new_entry)

        return group_entries

    def add_input_field(self, input_fields):
        group_input_fields = []
        if not isinstance(input_fields, list):
            input_fields = [input_fields]

        for input_field in input_fields:
            new_input_field = InputField(input_field)
            group_input_fields.append(new_input_field)

        return group_input_fields


# class AllGroups(list):
#     def __init__(self):
#         self.groups: list[Group] = []

#     def add_group(self, group: Group):
#         self.groups.append(group)

#     def get_all_entries(self):
#         all_entries: list[Entry] = []
#         for group in self.groups:
#             all_entries.extend(group.entries)
#         return all_entries


class AllGroups:
    def __init__(self):
        self.groups: dict[str, Group] = {}  # Use a dictionary to store groups

    def add_group(self, name: str, group: Group):
        self.groups[name] = group  # Add group with its name as the key

    def get_all_entries(self):
        all_entries: list[Entry] = []
        for group in self.groups.values():  # Iterate over the group values
            all_entries.extend(group.entries)
        return all_entries


class Entry(object):
    def __init__(self, entry) -> None:
        self.name = self.get_name(entry)
        # replace {name} entry_name
        self.command = entry["command"].format(name=self.name)

    def get_name(self, entry):
        if entry["name_is_command"]:
            self.execute_command(entry["name"]).stdout.strip()

        elif isinstance(entry["name"], str):
            return [entry["name"]]

        else:
            raise ValueError("Invalid entry name type")

    def execute_command(self, command):
        return run_subprocess(command, shell=True, capture_output=True, text=True)


class InputField(object):
    def __init__(self, input_field) -> None:
        self.name = input_field["name"]
        self.command = input_field["command"]
        self.display_text = input_field["display_text"]


# def create_all_groups(file_path: Path) -> list[Group]:
#     all_groups = AllGroups()

#     try:
#         with file_path.open("rb") as f:
#             parsed_data = tomllib.load(f)
#     except FileNotFoundError:
#         print(f"File '{file_path}' not found.")
#         return all_groups
#     except tomllib.TOMLDecodeError as e:
#         print(f"TOML decode error: {e}")
#         return all_groups

#     for group_data in parsed_data.get("group", []):
#         new_group = Group(group_data)
#         all_groups.add_group(new_group)

#     return all_groups.groups


def create_all_groups(file_path: Path) -> dict[str, Group]:
    all_groups = AllGroups()

    try:
        with file_path.open("rb") as f:
            parsed_data = tomllib.load(f)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return all_groups.groups
    except tomllib.TOMLDecodeError as e:
        print(f"TOML decode error: {e}")
        return all_groups.groups

    # Assuming each item in the list is a dictionary with a 'name' key for the group
    for group_data in parsed_data.get("group", []):
        group_name = group_data.get("name")  # Extract the group name
        if group_name:
            new_group = Group(group_data)  # Initialize new Group with the data
            all_groups.add_group(group_name, new_group)  # Add with name as key

    return all_groups.groups  # Return the dictionary of groups
