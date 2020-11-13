def parse_youtube_time(yt_time: str) -> str:
    """
    Parse the Youtube time format to the hh:mm:ss format

    params :
        - yt_time: str = The youtube time string
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
