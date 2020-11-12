# This class contains all info about a playable sonf
class Song:

    # ----- Constructor -----

    def __init__(self, title: str):
        # Assign the attributes
        self.title: str = title

    # ----- Class methods -----

    def __str__(self) -> str:
        return self.title
