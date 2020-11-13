class Command:
    """
    This class represent a command from discord users
    """

    # ------ Constructor ------

    def __init__(self, command: str):
        """
        Construct and parse a new command from a string

        params :
            - command: str = The command string
        """

        # Assign attributes
        self.command_str: str = command
        self.name: str = ""
        self.arg: str = ""

        # Parse the command
        self.parse_command()

    # ----- Class methods -----

    def parse_command(self) -> None:
        """
        Parse the command string
        """

        # Split the command into two parts
        tmp_list: list = self.command_str.split(" ", 1)

        # Verify the command format
        if tmp_list[0][0] == "!":
            self.name = tmp_list[0]
            if len(tmp_list) == 2:
                self.arg = tmp_list[1]
