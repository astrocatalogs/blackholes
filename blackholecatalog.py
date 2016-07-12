"""Supernovae specific catalog class.
"""
import os

from astrocats.catalog.catalog import Catalog

from .blackhole import BLACKHOLE, Blackhole


class BlackholeCatalog(Catalog):

    class PATHS(Catalog.PATHS):

        PATH_BASE = os.path.abspath(os.path.dirname(__file__))

        def __init__(self, catalog):
            print("HELLO")
            super().__init__(catalog)
            self.catalog.log.warning("self.PATH_BASE = '{}'".format(self.PATH_BASE))
            self.catalog.log.warning("self.PATH_OUTPUT = '{}'".format(self.PATH_OUTPUT))
            self.catalog.log.warning("self.REPOS = '{}'".format(self.REPOS))
            return

        def get_repo_output_file_list(self, normal=True, bones=True):
            output_file_types = ('.json')
            output_files = []
            # Walk through the output directories, store all matching files
            for root, dirs, files in os.walk(self.PATH_OUTPUT):
                output_files += [os.path.join(root, fil) for fil in files
                                 if fil.startswith(output_file_types)]
            return output_files

    class SCHEMA(Catalog.SCHEMA):
        pass

    def __init__(self, args, log):
        """
        """
        self.proto = Blackhole
        # Initialize super `astrocats.catalog.catalog.Catalog` object
        super().__init__(args, log)
        return

    def clone_repos(self):
        # Currently no internal repos to clone
        all_repos = []
        super()._clone_repos(all_repos)
        return
