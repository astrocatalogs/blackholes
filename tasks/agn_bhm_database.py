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
import numpy as np
import astropy as ap
import astropy.constants
import sys

from astrocats.catalog.utils import pbar
from astrocats.catalog.photometry import PHOTOMETRY
from astrocats.catalog.quantity import QUANTITY
from astrocats.catalog.source import SOURCE, Source

from astrocats.blackholes.blackhole import BLACKHOLE

SOURCE_BIBCODE = "2015PASP..127...67B"
SOURCE_URL = "http://adsabs.harvard.edu/abs/2015PASP..127...67B"
DATA_URL = "http://www.astro.gsu.edu/AGNmass/"
DATA_SUBPAGE_URL = "http://www.astro.gsu.edu/AGNmass/details.php?varname={}"

DESC_AGN_LUM = "Spectroscopic, monochromatic luminosities at 5100 angstrom."


def do_agn_bhm_database(catalog):
    """Load data from the 'AGN Blackhole Mass Database': 2015PASP..127...67B.

    FIX: Add archiving flags!
    """
    log = catalog.log
    log.debug("do_agn_bhm_database()")
    task_str = catalog.get_current_task_str()
    task_name = catalog.current_task.name
    # Load data from URL or cached copy of it
    cached_path = SOURCE_BIBCODE + '.txt'
    html = catalog.load_url(DATA_URL, cached_path, fail=True)
    if html is None:
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
    entries = 0
    for div in pbar(div_lines, task_str):
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

    return True


def _add_entry_for_data_line(catalog, line, varname, mass_scale_factor):
    """

    Columns:
    -------
    00 - object name
    01 - mass (+###/-###)   [ log(Mbh/Msol) ]
    02 - RA (hh:mm:ss.s)
    03 - Dec (dd:mm:ss)
    04 - redshift z
    05 - Alternate names    [whitespace delimiated strings]

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

    # Get data from blackhole-specific subpage
    # ----------------------------------------
    all_sources = [source]
    source_names, source_urls, source_codes = _load_blackhole_subpage_data(
        catalog, name, varname, source)
    # Warn on failure, but assume the entry is still okay.
    if not len(source_names):
        _warn(catalog, "Failed to load subpage for varname '{}'.".format(varname), line, name)
    # Add additional sources from sub-page
    else:
        for sn, su, sb in zip(source_names, source_urls, source_codes):
            src_kwargs = {SOURCE.NAME: sn, SOURCE.URL: su}
            if sb is not None:
                src_kwargs[SOURCE.BIBCODE] = sb
            src = catalog.entries[name].add_source(**src_kwargs)
            all_sources.append(src)

    # Join source-aliases into single string
    all_sources = ",".join(src for src in all_sources)

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
            quant_kwargs = {QUANTITY.U_VALUE: 'log(Msol)', QUANTITY.DESC: mass_desc,
                            QUANTITY.E_LOWER_VALUE: err_lo, QUANTITY.E_UPPER_VALUE: err_hi}
            catalog.entries[name].add_quantity(
                BLACKHOLE.MASS, bh_mass, all_sources, **quant_kwargs)

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

    return name


def _load_blackhole_subpage_data(catalog, name, varname, source):
    """Load data from this entry's dedicated subpage.

    Returns
    -------
    source_names : list of str
    source_urls : list of str
    source_codes : list of (str or 'None')
    """
    # Construct URL and load HTML data
    data_url = DATA_SUBPAGE_URL.format(varname)
    cached_path = "{:s}_{:s}.txt".format(SOURCE_BIBCODE, name)
    html = catalog.load_url(data_url, cached_path, fail=True)
    if html is None:
        return [], [], []

    # Extract the 'activity' of the BH
    # --------------------------------
    activ = re.search("<b>Activity:</b>(.*)</td><td>", html).groups()
    if len(activ) == 1:
        activ = activ[0].strip()
        if len(activ):
            catalog.entries[name].add_quantity(BLACKHOLE.ACTIVITY, activ, source)

    # Extract Luminosities and citations from the table
    # -------------------------------------------------
    soup = BeautifulSoup(html, 'html5lib')
    # The whole table is nested in a `<table class="body">`
    full_table = soup.find('table', attrs={'class': 'body'})
    source_names = []
    source_urls = []
    source_codes = []
    # Go through each line of table
    for table_line in full_table.find_all('tr'):
        childs = list(table_line.children)
        # Valid, normal lines have 11 cells in them (i.e. besides header and filler)
        if len(childs) == 11:
            for ii in [3, 8]:
                src_name, src_url, src_code = _source_url_name_from_cell(childs[ii])
                if src_name is not None and src_url is not None:
                    source_names.append(src_name)
                    source_urls.append(src_url)
                    source_codes.append(src_code)
            # Get AGN Luminosity
            lum_cell = childs[9].text.strip().split('+/-')
            # Blank lines have ellipses, valid lines have '+/-' uncertainty
            if len(lum_cell) == 2:
                lum_cell = [re.sub(r'[ ()]', r'', lc) for lc in lum_cell]
                val, err = lum_cell
                # The '10'th cell has the luminosity citation
                src_name, src_url, src_code = _source_url_name_from_cell(childs[10])
                if src_name is not None and src_url is not None:
                    # Add source for luminosity
                    src_kwargs = {SOURCE.NAME: src_name, SOURCE.URL: src_url}
                    if src_code is not None:
                        src_kwargs[SOURCE.BIBCODE] = src_code
                    lum_src = catalog.entries[name].add_source(**src_kwargs)
                    # List source as both primary and secondary sources
                    lum_src = ",".join([source, lum_src])
                    photo_kwargs = {
                        PHOTOMETRY.LUMINOSITY: val, PHOTOMETRY.SOURCE: lum_src,
                        PHOTOMETRY.HOST: True, PHOTOMETRY.E_LUMINOSITY: err,
                        PHOTOMETRY.U_LUMINOSITY: 'log(erg/s)', PHOTOMETRY.DESC: DESC_AGN_LUM,
                        PHOTOMETRY.WAVELENGTH: '5100', PHOTOMETRY.U_WAVELENGTH: 'angrstrom'
                    }
                    catalog.entries[name].add_photometry(**photo_kwargs)

            elif childs[9].text.strip() != '...':
                raise ValueError("Unexpected value in `childs[9]` = '{}'.".format(chils[9]))

    # Cut down to unique sources
    source_urls, inds = np.unique(source_urls, return_index=True)
    source_names = [source_names[ii] for ii in inds]
    source_codes = [source_codes[ii] for ii in inds]

    return source_names, source_urls, source_codes


def _source_url_name_from_cell(cell):
    """Given a table cell (`bs4.element.NavigableString`) try to get citation name and url.

    Returns 'None' values if either is missing or empty.

    Returns
    -------
    name : str
    url : str
    bibcode : str

    """
    # soup = BeautifulSoup(html, 'html5lib')
    source_cell = cell.find('a', href=True)
    try:
        name = source_cell.text.strip()
        url = source_cell['href'].strip()
    except AttributeError:
        return None, None, None

    if not len(name) or not len(url):
        return None, None, None

    bibcode = Source.bibcode_from_url(url)

    return name, url, bibcode


def _warn(catalog, msg, line=None, name=None):
    err_msg = msg
    if line is not None:
        err_msg += "\nLine: '{}'".format(line)
    if name is not None:
        err_msg = "'{}' : ".format(name) + err_msg
    catalog.log.error(err_msg)
    return
