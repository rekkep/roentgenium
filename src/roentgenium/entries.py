from subprocess import run as run_subprocess

from toml import load as load_toml


# ----------------------------
# Entry & Group Classes
# ----------------------------
class Group(object):
    """
    Represents a group of entries.

    Attributes:
        group_name: Name of the group
        group_description: Description of the group
        entries: List of Entry objects belonging to this group
    """

    def __init__(self, group):
        self.group_name = group["name"]
        self.group_description = group["description"]
        self.entries: list[Entry] = []

    def add_input_field(self, data):
        return InputField(data, self)

    def add_entries(self, entries):
        """
        Adds Entry objects to this group based on the entries.

        Handles:
            - If name_is_command=True: executes a shell command to generate entry names
            - If name is a list: uses the list as multiple entry names
            - If name is a string: wraps it in a list

        Raises:
            ValueError if the entry name type is invalid.
        """

        def get_entry_items(entry):
            if entry["name_is_command"]:
                # Run the shell command and split stdout lines into entries
                return self.run_command(entry["name"])

            elif isinstance(entry["name"], list):
                return entry["name"]

            elif isinstance(entry["name"], str):
                return [entry["name"]]

            else:
                raise ValueError("Invalid entry name type")

        entry_items = []

        # Generate list of entry names
        entry_items = get_entry_items(entries)

        # Create Entry objects for entry
        for entry_item in entry_items:
            new_entry = Entry(entry_item, entries["command"], _group=self)
            self.entries.append(new_entry)

    def run_command(self, command):
        """
        Executes a shell command and returns output lines as a list.

        Args:
            command: Shell command to run

        Returns:
            List of stripped stdout lines
        """
        return (
            run_subprocess(command, shell=True, capture_output=True, text=True)
            .stdout.strip()
            .split("\n")
        )


class Entry(object):
    """
    Represents a single command entry.

    Attributes:
        name: Name of the entry
        command: Command to execute (formatted with entry name)
        group: Reference to the parent Group object
    """

    def __init__(self, entry_name, entry_command, _group):
        self.name = entry_name
        # Format the command, injecting the entry name
        self.command = entry_command.format(name=self.name)
        self.group = _group

    def execute_command(self):
        """
        Executes the entry's command in the shell.

        Returns:
            subprocess.CompletedProcess object containing stdout, stderr, and returncode
        """
        return run_subprocess(self.command, shell=True, capture_output=True, text=True)


class InputField(object):
    """
    Represents a simpler input field with a command.

    Attributes:
        name: Name of the input field
        command: Command associated with the field
        group: Reference to parent group
    """

    def __init__(self, input_field, _group):
        self.name = input_field["name"]
        self.command = input_field["command"]
        self.display_text = input_field["display_text"]
        self.group = _group


# ----------------------------
# Utility function
# ----------------------------
def create_all_entries(file_path):
    """
    Parses a TOML file and creates all Entry objects from all groups.

    Args:
        file_path: Path to the TOML file

    Returns:
        List of all Entry objects in all groups
    """
    parsed_data = load_toml(file_path)
    all_entries = []
    input_field = None

    for group in parsed_data.get("group", []):
        new_group = Group(group)
        entries = group.get("entry", [])
        input_fields = group.get("input_field", [])
        input_field = new_group.add_input_field(input_fields)

        # Ensure entries_data is a list
        if not isinstance(entries, list):
            entries = [entries]

        # Add entries to group
        for entry in entries:
            new_group.add_entries(entry)

        # Collect all entries across groups
        all_entries.extend(new_group.entries)

    return all_entries, input_field
