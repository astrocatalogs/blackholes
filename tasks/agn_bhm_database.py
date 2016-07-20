"""Data from the AGN Blackhole Mass Database

http://www.astro.gsu.edu/AGNmass/
See: http://adsabs.harvard.edu/abs/2015PASP..127...67B
"""
import logging
import os
import csv
import re
import bs4
from bs4 import BeautifulSoup
import astropy as ap
import astropy.constants

from astrocats.catalog.utils import pbar
from astrocats.catalog.quantity import QUANTITY
from astrocats.catalog.photometry import PHOTOMETRY

from astrocats.blackholes.blackhole import BLACKHOLE

SOURCE_BIBCODE = "2015PASP..127...67B"
SOURCE_URL = "http://adsabs.harvard.edu/abs/2015PASP..127...67B"
DATA_URL = "http://www.astro.gsu.edu/AGNmass/"
DATA_SUBPAGE_URL = "http://www.astro.gsu.edu/AGNmass/details.php?varname={}"


def do_agn_bhm_database(catalog):
    """Load data from the 'AGN Blackhole Mass Database': 2015PASP..127...67B.
    """
    log = catalog.log
    log.debug("do_agn_bhm_database()")
    task_str = catalog.get_current_task_str()
    task_name = catalog.current_task.name
    # Load data from URL or cached copy of it
    cached_path = os.path.join(
        catalog.get_current_task_repo(), SOURCE_BIBCODE + '.txt')
    html = catalog.load_cached_url(DATA_URL, cached_path)
    if not html:
        catalog.log.error("{} Failed to load data from '{}'.".format(
            task_name, DATA_URL))
        return False

    # Get this line for description of mass calculation
    #    'M<sub>BH</sub> calculated using <i>&lt; f &gt;</i>&thinsp;=&thinsp; 2.8'
    mass_scale_factor = re.search("<i>&lt; f &gt;</i>&thinsp;=&thinsp; (.*)", html).groups()
    # If pattern matches expectations, store it
    if len(mass_scale_factor) == 1:
        mass_scale_factor = mass_scale_factor[0]
    # Otherwise, forget it
    else:
        err_msg = "Could not load `mass_scale_factor` from '{}'".format(mass_scale_factor)
        catalog.log.error(err_msg)
        return False

    soup = BeautifulSoup(html, 'html5lib')

    # The whole table is nested in a `<table class="hovertable">`
    full_table = soup.find('table', attrs={'class': 'hovertable'})
    # Each line in the file is separated with `'tr'`
    div_lines = full_table.find_all('tr')
    num_div_lines = len(div_lines)

    # Go through each element of the tables
    num = 0
    entries = 0
    while num < num_div_lines:
        div = div_lines[num]

        # Get the `varname` -- ID number for each row
        #    The first element of the `contents` contains an href with the 'varname'
        cell_text = str(div.contents[0])
        groups = re.search('varname=([0-9]*)', cell_text)
        # If no match is found, this is one of the header lines (not an entry line, skip)
        if groups is not None:
            varname = groups.groups()[0]
            name = _add_entry_for_data_line(catalog, div.text, varname, mass_scale_factor)
            if name is not None:
                entries += 1

        num += 1

    return True


def _add_entry_for_data_line(catalog, line, varname, mass_scale_factor):
    """

    Columns:
    -------
    [ ] 00 - object name
    [ ] 01 - mass (+###/-###)   [ log(Mbh/Msol) ]
    [ ] 02 - RA (hh:mm:ss.s)
    [ ] 03 - Dec (dd:mm:ss)
    [ ] 04 - redshift z
    [ ] 05 - Alternate names    [whitespace delimiated strings]

    Sample Entry:
    ------------
    Mrk335 7.230 (+0.042/-0.044) 00:06:19.5 +20:12:10 0.02579 PG0003+199
    Mrk382 ... 07:55:25.3 +39:11:10 0.03369

    """
    cells = [ll.strip() for ll in line.split('  ') if len(ll.strip())]
    # print(cells, varname)
    if not len(cells):
        return None

    mass_desc = ("BH Mass with one-sigma errors, calculated w/ reverberation "
                 "mapping using a scale-factor of <f> = {}".format(mass_scale_factor))

    # Galaxy/BH Name
    # --------------
    name = cells.pop(0)
    name = catalog.add_entry(name)
    # Add this source
    source = catalog.entries[name].add_source(
        url=SOURCE_URL, bibcode=SOURCE_BIBCODE, secondary=True)

    # Mass and Uncertainties
    # ----------------------
    # This is either no entry '...' or something like:
    #    '8.638 \u2002 (+0.040/-0.046)'
    bh_mass = cells.pop(0)
    # Avoid no mass given
    if bh_mass != '...':
        bh_mass = bh_mass.split('\u2002')
        # If the mass is not what we expect, log error, but continue
        if len(bh_mass) != 2:
            _warn(catalog, "Mass cannot be parsed.", line, name)
        else:
            # Remove spaces, paranthesis, and signs
            bh_mass, err = [re.sub(r'[ ()+-]', r'', mm) for mm in bh_mass]
            # Split into higher and lower errors
            err_hi, err_lo = err.split('/')

            # FIX: add additional sources from the sub-pages
            use_sources = source
            quant_kwargs = {QUANTITY.U_VALUE: 'log(Msol)', QUANTITY.DESC: mass_desc,
                            QUANTITY.E_LOWER_VALUE: err_lo, QUANTITY.E_UPPER_VALUE: err_hi}
            catalog.entries[name].add_quantity(BLACKHOLE.MASS, bh_mass, use_sources, **quant_kwargs)

    # RA/Dec
    # ------
    # Exists for all entries
    ra = cells.pop(0)
    dec = cells.pop(0)
    # Make sure ra and dec look right
    if len(ra.split(':')) == 3 and len(dec.split(':')) == 3:
        catalog.entries[name].add_quantity(BLACKHOLE.RA, ra, source)
        catalog.entries[name].add_quantity(BLACKHOLE.DEC, dec, source)
    else:
        _warn(catalog, "RA/Dec cannot be parsed: '{}'/'{}'".format(ra, dec), line, name)

    # Redshift
    # --------
    # Exists for all entries
    redz = cells.pop(0)
    catalog.entries[name].add_quantity(BLACKHOLE.REDSHIFT, redz, source)

    # Add alias of name, if given
    # ---------------------------
    # Sometimes none, sometimes multiple (separated by '\u2003')
    if len(cells):
        in_aliases = cells.pop(0)
        in_aliases = [cc.strip() for cc in in_aliases.split('\u2003')]
        aliases = [catalog.entries[name].add_alias(cc, source) for cc in in_aliases]

        if len(cells):
            _warn(catalog, "`cells` still not empty! '{}'".format(cells), line, name)

    # Get data from blackhole-specific subpage
    # ----------------------------------------
    retval = _load_blackhole_subpage_data(catalog, name, varname, source)
    # Warn on failure, but assume the entry is still okay.
    if not retval:
        _warn(catalog, "Failed to load subpage for varname '{}'.".format(varname), line, name)

    return name


def _load_blackhole_subpage_data(catalog, name, varname, source):
    """Load data from this entry's dedicated subpage.
    """
    # Construct URL and load HTML data
    data_url = DATA_SUBPAGE_URL.format(varname)
    cached_path = os.path.join(
        catalog.get_current_task_repo(), SOURCE_BIBCODE + '.txt')
    html = catalog.load_cached_url(data_url, cached_path)
    if not html:
        catalog.log.error("{} Failed to load data from '{}'.".format(
            task_name, DATA_URL))
        return False

    # Extract the 'activity' of the BH
    # --------------------------------
    activ = re.search("<b>Activity:</b>(.*)</td><td>", html).groups()
    print(activ)
    if len(activ) == 1:
        catalog.entries[name].add_quantity(BLACKHOLE.ACTIVITY, bh_mass, use_sources, **quant_kwargs)


    # print(html)

    return True


def _warn(catalog, msg, line=None, name=None):
    err_msg = msg
    if line is not None:
        err_msg += "\nLine: '{}'".format(line)
    if name is not None:
        err_msg = "'{}' : ".format(name) + err_msg
    catalog.log.error(err_msg)
    return
