"""The Blackholes AstroCatalog.
"""
import os

catalog_class = {
    "name": "BlackholeCatalog",
    "file": "blackholecatalog",
    "import_path": "blackholes."
}


import astrocats


class BH_Paths(astrocats.Paths):

    ROOT = os.path.join(os.path.dirname(__file__), "")
    NAME = __name__
    FILE = __file__


PATHS = BH_Paths()
