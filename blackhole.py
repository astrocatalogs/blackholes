"""
"""
import os

import pyastroschema as pas

import astrocats
from astrocats.catalog.struct import ENTRY, Entry
from astrocats.catalog import struct, utils
from astrocats import blackholes


PATH_BH_SCHEMA_INPUT = os.path.join(blackholes.PATH_BH_SCHEMA, "")
# print("`PATH_BH_SCHEMA_INPUT` = '{}'".format(PATH_BH_SCHEMA_INPUT))

path_my_blackhole_schema = os.path.join(PATH_BH_SCHEMA_INPUT, "bh_blackhole.json")
path_entry = os.path.join(astrocats._PATH_SCHEMA, "input", "entry.json")
path_astrocats_entry = os.path.join(astrocats._PATH_SCHEMA, "input", "astrocats_entry.json")


@pas.struct.set_struct_schema(
    path_entry, extensions=[path_astrocats_entry, path_my_blackhole_schema])
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

    def _get_save_path(self, bury=False):
        """Return the path that this Entry should be saved to."""
        filename = utils.get_filename(self[self._KEYS.NAME])

        # Put objects that shouldn't belong in this catalog in the boneyard
        if bury:
            outdir = self.catalog.get_repo_boneyard()

        # Get normal repository save directory
        else:
            repo_folders = self.catalog.PATHS.get_repo_output_folders()
            # If no repo folders exist, raise an error -- cannot save
            if not len(repo_folders):
                err_str = (
                    "No output data repositories found. Cannot save.\n"
                    "Make sure that repo names are correctly configured "
                    "in the `input/repos.json` file, and either manually or "
                    "automatically (using `astrocats CATALOG git-clone`) "
                    "clone the appropriate data repositories.")
                self.catalog.log.error(err_str)
                raise RuntimeError(err_str)

            outdir = repo_folders[-1]

        return outdir, filename


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
