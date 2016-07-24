"""Supernovae specific catalog class.
"""
import os
import re

from astrocats.catalog.catalog import Catalog

from .blackhole import BLACKHOLE, Blackhole


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
        # Replace all spaces with underscores, do this last: specifics already handled
        # [r' ', r'_', None],
    ]

    class PATHS(Catalog.PATHS):

        PATH_BASE = os.path.abspath(os.path.dirname(__file__))

        def __init__(self, catalog):
            super().__init__(catalog)
            return

    class SCHEMA(Catalog.SCHEMA):
        pass

    def __init__(self, args, log):
        """
        """
        # Initialize super `astrocats.catalog.catalog.Catalog` object
        super().__init__(args, log)
        self.proto = Blackhole
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
