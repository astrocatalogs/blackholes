"""Blackhole specific catalog class.
"""
import os
import re

from astrocats.catalog.catalog import Catalog
from astrocats.catalog import utils
from .blackhole import Blackhole, BLACKHOLE
from . production import blackhole_director


class BlackholeCatalog(Catalog):
    """
    """

    _NAME_REPLACEMENT_REGEX = [
        # 'IC ####'    --> 'IC####'
        [r'IC ([0-9]{4})', r'IC\1', None],
        # [Cygnus]' A' --> [Cygnus]'-A'
        [r'[ ]([A-Z])$',  r'-\1',  None],
        # Make whole words fully lowercase
        # e.g. 'Milky WaY' --> 'milky way'
        [r'^[ a-zA-Z]*$', lambda m: m.group(0).lower(), None],
        # Replace "N####" or "N ####" with "NGC####"
        [r'N([0-9]{4})', r'NGC\1', None],
        # Remove all spaces, do this last: specifics already handled
        [r' ', r'', None],
    ]

    TRAVIS_QUERY_LIMIT = 10
    # Set behavior for when adding a quantity (photometry, source, etc) fails
    #    Options are 'IGNORE', 'WARN', 'RAISE' (see `utils.imports`)
    ADDITION_FAILURE_BEHAVIOR = utils.ADD_FAIL_ACTION.RAISE

    _EVENT_HTML_COLUMNS_CUSTOM = {
        BLACKHOLE.MASS: ["Mass [log(<em>M</em><sub>&#9737;</sub>)] [kind]", 1.1],
        BLACKHOLE.ACTIVITY: ["AGN Activity", 1.2],
        BLACKHOLE.GALAXY_MORPHOLOGY: ["Gal. Type", 102],
        BLACKHOLE.GALAXY_MASS_BULGE: ["Gal. Bulge Mass [log(<em>M</em><sub>&#9737;</sub>)]", 103],
        BLACKHOLE.GALAXY_LUMINOSITY_BULGE: ["Gal. Bulge Lum [log(<em>L</em><sub>&#9737;</sub>)]", 104],
        BLACKHOLE.GALAXY_VEL_DISP_BULGE: ["Gal. Vel. Disp. [km/s]", 105],
        BLACKHOLE.FWHM_HBETA: ["FWHM H-Beta [km/s]", 106],
        BLACKHOLE.FWHM_MGII: ["FWHM Mg-II [km/s]", 107],
        BLACKHOLE.FWHM_CIV: ["FWHM C-IV [km/s]", 108],
    }

    class PATHS(Catalog.PATHS):
        PATH_BASE = os.path.abspath(os.path.dirname(__file__))

    class SCHEMA(Catalog.SCHEMA):
        pass

    def __init__(self, args, log):
        """
        """
        log.debug("BlackholeCatalog.__init__()")
        # Initialize super `astrocats.catalog.catalog.Catalog` object
        super().__init__(args, log)
        self.proto = Blackhole
        self.Director = blackhole_director.Blackhole_Director
        return

    def clone_repos(self):
        # Currently no internal repos to clone
        all_repos = self.PATHS.get_repo_input_folders()
        all_repos += self.PATHS.get_repo_output_folders()
        super()._clone_repos(all_repos)
        return

    def clean_entry_name(self, name):
        """
        """
        for find, replace, flags in self._NAME_REPLACEMENT_REGEX:
            if flags is None:
                use_flags = 0
            else:
                use_flags = flags
            name = re.sub(find, replace, name, flags=use_flags)

        return name
