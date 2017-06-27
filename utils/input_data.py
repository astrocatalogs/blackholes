"""Functions for processing input files and data sources.
"""


def load_cached_or_download(url, fname, log, refresh=False, write=True):
    """Load a cached/saved version of a file, or download a new copy.
    """

    # Download a new copy if it doesn't exist
    _refresh = False
    if not os.path.exists(fname):
        log.debug("Path '{}' does not exist.".format(fname))
        _refresh = True

    #
    if refresh or _refresh:


def request_url_text(url, log=None, protect=True, timeout=120, raise_errors=[500, 307, 404]):
    """Load text from given URL.
    """
    url_text = None
    # Try to download text from URL
    try:
        import requests
        session = requests.Session()
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        # Look for errors
        for xx in response.history:
            xx.raise_for_status()
            if xx.status_code in raise_errors:
                raise
        # Load text from response
        url_text = response.text
    # Break on keyboard interrupts
    except (KeyboardInterrupt, SystemExit):
        raise
    # Catch exceptions
    except Exception as err:
        # If we want to `protect` against exceptions, log an error if log is given, return 'None'
        if protect:
            if log is not None:
                log.error("Error on url '{}': '{}'.".format(url, str(err)))
            return None
        # If we are not protecting... raise the error
        else:
            raise

    return url_text
