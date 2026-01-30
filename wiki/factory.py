# wiki/factory.py

from wiki.bulbapedia import *


def get_wiki_client(wiki: str = "bulbapedia"):
    if wiki == "bulbapedia":
        return BulbapediaClient()
    else:
        raise ValueError("Wiki client not supported")
