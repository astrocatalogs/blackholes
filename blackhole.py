"""
"""
from astrocats.catalog.entry import ENTRY, Entry
from astrocats.catalog.key import KEY_TYPES, Key, KeyCollection


_NAME_REPLACEMENT_REGEX = [
    [r'IC ([0-9]{4})', r'IC\1']
]


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
    MASS = 'mass'
    DISTANCE = 'distance'
    # RAD_INFL = 'radius_influence'
    GALAXY_MASS_BULGE = 'galaxy_bulge_mass'
    GALAXY_VEL_DISP_BULGE = 'galaxy_bulge_vel_disp'
    GALAXY_LUMINOSITY_BULGE = 'galaxy_bulge_luminosity'
    GALAXY_RAD_EFF_V = 'galaxy_rad_eff_v-band'
    GALAXY_RAD_EFF_I = 'galaxy_rad_eff_i-band'
    GALAXY_RAD_EFF_3p6 = 'galaxy_rad_eff_3.6-micron'

    # Boolean Types
    # String Types
    GALAXY_MORPHOLOGY = 'galaxy_morphology'


class Blackhole(Entry):
    """Single entry in the Blackhole catalog, representing a single Blackhole.
    """

    _KEYS = BLACKHOLE

    def __init__(self, catalog, name, stub=False):
        name = self._name_clean(name)
        super().__init__(catalog, name, stub=stub)
        return

    def add_self_source(self):
        return self.add_source(
            bibcode=self.catalog.OSC_BIBCODE,
            name=self.catalog.OSC_NAME,
            url=self.catalog.OSC_URL, secondary=True)

    def _name_clean(self, dirty):
        """
        """
        clean = str(dirty)

        return clean


    @classmethod
    def get_filename(cls, name):
        fname = super().get_filename(name)
        fname = fname.replace(' ', '_')
        fname = fname.replace('-', '_')
        return fname
