"""Entry point for the Blackhole Catalog
"""
from datetime import datetime


def main(args, clargs, log):
    log.debug("blackholes.main.main()")
    from .blackholecatalog import BlackholeCatalog
    from astrocats.catalog.argshandler import ArgsHandler

    # Create an `ArgsHandler` instance with the appropriate argparse machinery
    args_handler = ArgsHandler(log)
    # Parse the arguments to get the configuration settings
    args = args_handler.load_args(args=args, clargs=clargs)
    # Returns 'None' if no subcommand is given
    if args is None:
        log.warning("No `args` given.")
        return

    # Create the appropriate type of catalog
    log.info("Creating `BlackholeCatalog`")
    catalog = BlackholeCatalog(args, log)

    # Run the subcommand given in `args`
    log.info("Running subcommand")
    args_handler.run_subcommand(args, catalog)

    return
