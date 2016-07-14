"""Supernovae specific catalog class.
"""
import os

from astrocats.catalog.catalog import Catalog

from .blackhole import BLACKHOLE, Blackhole


class BlackholeCatalog(Catalog):

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
