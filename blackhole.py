"""
"""
from astrocats.catalog.entry import ENTRY, Entry
from astrocats.catalog.key import KEY_TYPES, Key, KeyCollection


class BLACKHOLE(KeyCollection):
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
    MASS = 'mass'
    DISTANCE = 'distance'
    RAD_INFL = 'radius_influence'
    GALAXY_MASS_BULGE = 'galaxy_bulge_mass'
    GALAXY_VEL_DISP = 'galaxy_vel_disp'

    # Boolean Types
    # String Types
    GALAXY_MORPHOLOGY = 'galaxy_morphology'


class Blackhole(Entry):
    """Single entry in the Blackhole catalog, representing a single Blackhole.
    """

    _KEYS = BLACKHOLE

    def __init__(self, catalog, name, stub=False):
        super().__init__(catalog, name, stub=stub)
        return

    def add_self_source(self):
        return self.add_source(
            bibcode=self.catalog.OSC_BIBCODE,
            name=self.catalog.OSC_NAME,
            url=self.catalog.OSC_URL, secondary=True)
