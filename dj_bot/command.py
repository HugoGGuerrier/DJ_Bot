# This class is a helper to parse and execute commands
class Command:

    # ------ Constructor ------

    def __init__(self, command: str):
        # Assign attributes
        self.command_str: str = command
        self.name: str = ""
        self.arg: str = ""

        # Parse the command
        self.parse_command()

    # ----- Class methods -----

    def parse_command(self):
        # Split the command into two parts
        tmp_list: list = self.command_str.split(" ", 1)

        # Verify the command format
        if tmp_list[0][0] == "!":
            self.name = tmp_list[0]
            if len(tmp_list) == 2:
                self.arg = tmp_list[1]
