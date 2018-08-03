"""Blackhole Catalog: `Director` subclass
"""

from astrocats.catalog.production import director, html_pro
from astrocats.catalog.utils import dict_to_pretty_string
from astrocats.catalog.struct import QUANTITY
from .. blackhole import BLACKHOLE


class Blackhole_Director(director.Director):

    _SAVE_ENTRY_KEYS = ['distance', 'mass', 'galaxy_bulge_vel_disp', 'galaxy_bulge_mass',
                        'agn_activity', 'tasks']
    # _DEL_QUANTITY_KEYS = ['description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.HTML_Pro = BH_HTML_Pro
        return

    # def update(self, fname, event_name, event_data):
    #     # print(dict_to_pretty_string(event_data))
    #     super().update(fname, event_name, event_data)


class BH_HTML_Pro(html_pro.HTML_Pro):

    def _meta_data_entry_kind(self, key, row):
        """Retrieve an additional 'kind' parameter to add to a Meta-Data value cell.
        """
        if key == BLACKHOLE.MASS and QUANTITY.KIND in row:
            return row[QUANTITY.KIND]

        return
