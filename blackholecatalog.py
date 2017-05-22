"""Blackhole specific catalog class.
"""
import os
import re

from astrocats.catalog.catalog import Catalog
from .blackhole import Blackhole
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
    RAISE_ERROR_ON_ADDITION_FAILURE = True

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
