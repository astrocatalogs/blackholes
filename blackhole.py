"""
"""
import os

import pyastroschema as pas

import astrocats
from astrocats.catalog.entry import ENTRY, Entry
from astrocats.catalog import struct
from astrocats import blackholes


PATH_BH_SCHEMA_INPUT = os.path.join(blackholes.PATH_SCHEMA, "input", "")
print("`PATH_BH_SCHEMA_INPUT` = '{}'".format(PATH_BH_SCHEMA_INPUT))

path_my_blackhole_schema = os.path.join(PATH_BH_SCHEMA_INPUT, "bh_blackhole.json")
path_astrocats_entry = os.path.join(astrocats._PATH_SCHEMA, "output", "entry.json")


@pas.struct.set_struct_schema(path_astrocats_entry, extensions=[path_my_blackhole_schema])
class Blackhole(Entry):
    """Single entry in the Blackhole catalog, representing a single Blackhole.
    """

    def __init__(self, catalog, name, stub=False):
        name = catalog.clean_entry_name(name)
        super().__init__(catalog, name, stub=stub)
        return

    def add_self_source(self):
        return self.add_source(
            bibcode=self.catalog.OSC_BIBCODE,
            name=self.catalog.OSC_NAME,
            url=self.catalog.OSC_URL, secondary=True)

    @classmethod
    def get_filename(cls, name):
        fname = super().get_filename(name)
        fname = fname.replace(' ', '_')
        fname = fname.replace('-', '_')
        return fname


BLACKHOLE = Blackhole._KEYCHAIN
Blackhole._KEYS = BLACKHOLE

BLACKHOLE.DISCOVER_DATE = BLACKHOLE.DISCOVERDATE


class GALAXY_MORPHS:
    ELLIPTICAL = "elliptical"
    LENTICULAR = "lenticular"
    SPIRAL = "spiral"
    SPIRAL_BARRED = "spiral, barred"
    IRREGULAR = "irregular"


class BH_MASS_METHODS:
    DYN_MASERS = "dynamics (masers)"
    DYN_STARS = "dynamics (stars)"
    DYN_GAS = "dynamics (gas)"
    DYN_MODELS = "dynamics (three-integral models)"
    REVERB_MAP = "reverberation mapping"
    VIR_HBETA = "virial (H-Beta)"
    VIR_MGII = "virial (Mg-II)"
    VIR_CIV = "virial (C-IV)"
    VIR = "virial"
