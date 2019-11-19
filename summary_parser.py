# TODO: parse summaries and return useful stuff
import re


def get_date(summary):
    try:
        found = re.search("(?<=Date: )(.*)", summary).group(1).replace(" <br/>", "")
        return found
    except AttributeError:
        return "Error fetching date"


def get_time(summary):
    try:
        found = re.search("(?<=Time: )(.*)", summary).group(1).replace(" <br/>", "").replace("00:", "12:")
        return found
    except AttributeError:
        return "Error fetching time"


def get_datetime(summary):
    # This isn't really needed but it makes my job a lot easier
    try:
        found = f"{get_date(summary)}, {get_time(summary)}"
        return found
    except AttributeError:
        return "Error fetching datetime"


def get_duration(summary):
    try:
        found = re.search("(?<=Duration: )(.*)", summary).group(1).replace(" <br/>", "")
        return found
    except AttributeError:
        return "Error fetching duration"


def get_max_height(summary):
    try:
        found = re.search("(?<=Maximum Elevation: )(.*)", summary).group(1).replace(" <br/>", "")
        return found
    except AttributeError:
        return "Error fetching maximum elevation"


def get_appear(summary):
    try:
        found = re.search("(?<=Approach: )(.*)", summary).group(1).replace(" <br/>", "")
        return found
    except AttributeError:
        return "Error fetching appearance time"


def get_disappear(summary):
    try:
        found = re.search("(?<=Departure: )(.*)", summary).group(1).replace(" <br/>", "")
        return found
    except AttributeError:
        return "Error fetching maximum elevation"
