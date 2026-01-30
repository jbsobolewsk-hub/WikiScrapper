# utils/path_utils.py

import re


def safe_filename(name: str) -> str:
    """
    Converts a string to a safe filename by removing/escaping illegal characters.
    """

    name = name.strip().replace(" ", "_")
    name = re.sub(r'[^A-Za-z0-9_.-]', '', name)

    return name
