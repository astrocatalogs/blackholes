"""Blackhole Catalog: `Director` subclass
"""

from astrocats.catalog.production import director


class Blackhole_Director(director.Director):

    _SAVE_ENTRY_KEYS = ['distance', 'mass', 'galaxy_bulge_vel_disp', 'galaxy_bulge_mass']
    _DEL_QUANTITY_KEYS = ['description']
