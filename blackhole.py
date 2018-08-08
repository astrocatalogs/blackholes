"""
"""
import os

import pyastroschema as pas

import astrocats
from astrocats.catalog.entry import ENTRY, Entry
from astrocats.catalog import struct
from astrocats import blackholes
# from astrocats.catalog.key import KEY_TYPES, Key

# "...astrocats/blackholes/"
# temp = os.path.dirname(__file__)


PATH_BH_SCHEMA_INPUT = os.path.join(blackholes.PATH_SCHEMA, "input", "")
print("`PATH_BH_SCHEMA_INPUT` = '{}'".format(PATH_BH_SCHEMA_INPUT))

path_my_blackhole_schema = os.path.join(PATH_BH_SCHEMA_INPUT, "bh_blackhole.json")
path_astrocats_entry = os.path.join(astrocats._PATH_SCHEMA, "output", "entry.json")

'''
class BLACKHOLE(ENTRY):
    """KeyCollection for `Blackhole` keys.

    Attributes
    ----------
    MASS : NUMERIC
        Mass of the blackhole.  Use [Msol].
    DISTANCE
    RAD_INFL
    GALAXY_MASS_BULGE
    GALAXY_VEL_DISP
        Velocity dispersion of the host galaxy.  Use [km/s].
    GALAXY_MORPHOLOGY
        Morphological classification of the galaxy.

    """
    # Any Type
    # Numeric Types
    MASS = Key('mass', KEY_TYPES.NUMERIC)
    DISTANCE = Key('distance', KEY_TYPES.NUMERIC)
    # RAD_INFL = 'radius_influence'
    GALAXY_MASS_BULGE = Key('galaxy_bulge_mass', KEY_TYPES.NUMERIC)
    GALAXY_VEL_DISP_BULGE = Key('galaxy_bulge_vel_disp', KEY_TYPES.NUMERIC)
    GALAXY_LUMINOSITY_BULGE = Key('galaxy_bulge_luminosity', KEY_TYPES.NUMERIC)
    GALAXY_RAD_EFF_V = Key('galaxy_rad_eff_v-band', KEY_TYPES.NUMERIC)
    GALAXY_RAD_EFF_I = Key('galaxy_rad_eff_i-band', KEY_TYPES.NUMERIC)
    GALAXY_RAD_EFF_3p6 = Key('galaxy_rad_eff_3.6-micron', KEY_TYPES.NUMERIC)
    GALAXY_VEL_DISP = Key('galaxy_vel_disp', KEY_TYPES.NUMERIC)
    GALAXY_MASS_TO_LIGHT_RATIO = Key('mass_to_light', KEY_TYPES.NUMERIC)

    FWHM_HBETA = Key('fwhm_hbeta', KEY_TYPES.NUMERIC)
    FWHM_MGII = Key('fwhm_mgii', KEY_TYPES.NUMERIC)
    FWHM_CIV = Key('fwhm_civ', KEY_TYPES.NUMERIC)

    # Boolean Types
    # String Types
    ACTIVITY = Key('agn_activity', KEY_TYPES.STRING)
    GALAXY_MORPHOLOGY = Key('galaxy_morphology', KEY_TYPES.STRING, listable=True)
'''


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
