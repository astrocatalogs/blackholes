"""Blackhole Catalog: `Director` subclass
"""

from astrocats.catalog.production import director
from astrocats.catalog.utils import dict_to_pretty_string


class Blackhole_Director(director.Director):

    _SAVE_ENTRY_KEYS = ['distance', 'mass', 'galaxy_bulge_vel_disp', 'galaxy_bulge_mass',
                        'agn_activity', 'tasks']
    # _DEL_QUANTITY_KEYS = ['description']

    def update(self, fname, event_name, event_data):
        # print(dict_to_pretty_string(event_data))
        super().update(fname, event_name, event_data)
