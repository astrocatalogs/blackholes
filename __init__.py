"""The Blackholes AstroCatalog.
"""
import os

_ROOT = os.path.join(os.path.dirname(__file__), "")

catalog_info = {
    "catalog_name": __name__,
    "catalog_class": {
        "name": "BlackholeCatalog",
        "file": "blackholecatalog",
        "path": "blackholes."
    },
    "schema_path": os.path.join(_ROOT, "schema", "")
}


import astrocats


class BH_Paths(astrocats.Paths):

    ROOT = _ROOT
    NAME = __name__
    FILE = __file__

    def __init__(self):
        super(BH_Paths, self).__init__()
        return


PATHS = BH_Paths()
