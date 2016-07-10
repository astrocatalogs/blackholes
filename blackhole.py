"""
"""
from astrocats.catalog.entry import ENTRY, Entry


class BLACKHOLE(ENTRY):
    """KeyCollection for `Blackhole` keys.
    """
    pass


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
