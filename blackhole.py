"""
"""
from astrocats.catalog.entry import ENTRY, Entry
from astrocats.catalog.key import KEY_TYPES, Key, KeyCollection


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

    # Boolean Types
    # String Types
    ACTIVITY = Key('agn_activity', KEY_TYPES.STRING)
    GALAXY_MORPHOLOGY = Key('galaxy_morphology', KEY_TYPES.STRING, listable=True)


class Blackhole(Entry):
    """Single entry in the Blackhole catalog, representing a single Blackhole.
    """

    _KEYS = BLACKHOLE

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
