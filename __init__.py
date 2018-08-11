"""The Blackholes AstroCatalog.
"""
# flake8: noqa  --- ignore imported but unused flake8 warnings
import os
import glob

from . import main
# from . import production

_PATH_BLACKHOLES = os.path.join(os.path.dirname(__file__), "")
PATH_BH_SCHEMA = os.path.join(_PATH_BLACKHOLES, "schema", "")
