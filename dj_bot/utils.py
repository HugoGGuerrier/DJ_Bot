import discord


def parse_youtube_time(yt_time: str) -> str:
    """
    Parse the Youtube time format to the hh:mm:ss format

    params :
        - yt_time: str = The youtube time string
    return -> str = The youtube time formatted in a cooler format
    """

    # Remove the PT at the start
    yt_time = yt_time[2:len(yt_time)]

    # Prepare the result
    hour: int = 0
    minute: int = 0
    second: int = 0

    # Extract time from the string
    buffer: str = ""
    for c in yt_time:
        if c == "H":
            hour = int(buffer)
            buffer = ""
        elif c == "M":
            minute = int(buffer)
            buffer = ""
        elif c == "S":
            second = int(buffer)
            buffer = ""
        else:
            buffer += c

    # Prepare the result
    res: str = ""

    if hour > 0:
        res += "{:02d}".format(hour) + ":"
    res += "{:02d}".format(minute) + ":"
    res += "{:02d}".format(second)

    # Return the string result
    return res


def get_user_fullname(user: discord.Member) -> str:
    """
    Get the full name of a discord user (i.e. MyName#0000)

    params :
        - user: discord.Member : The user you want to get the name from
    return -> str = The name of the user
    """

    return user.name + "#" + user.discriminator
