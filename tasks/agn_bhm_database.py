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


def do_agn_bhm_database(catalog):
    """
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
        self.log("{} Failed to load data from '{}'.".format(
            task_name, DATA_URL), level=logging.WARNING)
        return

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
            print("\t", varname, "\t", div.text)

            name = _add_entry_for_data_line(catalog, div.text, varname)
            if name is not None:
                entries += 1

        num += 1


    return


def _add_entry_for_data_line(catalog, line, varname):
    """

    Columns:
    -------
    [ ] 00 - object name
    [ ] 01 - mass log(Mbh/Msol)
    [ ] 02 - RA (hh:mm:ss.s)
    [ ] 03 - Dec (dd:mm:ss)
    [ ] 04 - redshift z
    [ ] 05 - Alternate names (whitespace delimiated strings)

    Sample Entry:
    ------------
    Mrk335 7.230 (+0.042/-0.044) 00:06:19.5 +20:12:10 0.02579 PG0003+199
    Mrk382 ... 07:55:25.3 +39:11:10 0.03369

    """
    cells = [ll.strip() for ll in line.split()]
    if not len(cells):
        return None

    # Galaxy/BH Name
    # --------------
    # Remove footnotes
    data_name = line[0].replace(' ', '_')
    # See if an alias is given in parenthesis e.g. 'N3379 (M105)'
    groups = re.search('(.*)[ ]*\((.*)\)', data_name)
    alias = None
    if groups is not None:
        groups = groups.groups()
        data_name = groups[0]
        alias = groups[1].strip()
    data_name = data_name.strip()
    # If name matches pattern 'IC ####', remove space
    if re.search('IC [0-9]{4}', data_name) is not None:
        data_name = data_name.replace('IC ', 'IC')
    # At the end of the table, there is a blank row, return None in that case
    if not len(data_name):
        return None
    name = catalog.add_entry(data_name)

    # Add this source
    source = catalog.entries[name].add_source(url=SOURCE_URL, bibcode=SOURCE_BIBCODE)
    # Add alias of name, if one was found
    if alias is not None:
        catalog.entries[name].add_quantity('alias', name, source)

    # BH Mass, looks like "  3.9 (0.4,0.6) e9"
    # ----------------------------------------
    mass_line = lines[1].text.strip()
    bh_mass, error, exp = re.search('(.*) \((.*)\) e([0-9])', mass_line).groups()
    exp = 'e' + exp
    bh_mass += exp
    err_lo, err_hi = error.split(',')
    err_lo += exp
    err_hi += exp
    # Line '15' has the reference[s] for the mass
    refs = [rr['href'] for rr in lines[15].contents if isinstance(rr, bs4.element.Tag)]
    # If references are found, add them to this paper (McConnell & Ma)
    use_sources = [source]
    if len(refs):
        for rr in refs:
            new_src = catalog.entries[name].add_source(url=rr)
            use_sources.append(new_src)
    # Multiple sources should be comma-delimited string of integers e.g. '1, 3, 4'
    use_sources = ",".join(str(src) for src in use_sources)

    # Line '14' includes the 'method' of mass determination
    mass_desc = "BH Mass with one-sigma errors.  Method: '{}'".format(lines[14].text.strip())
    quant_kwargs = {QUANTITY.U_VALUE: 'Msol', QUANTITY.DESC: mass_desc,
                    QUANTITY.E_LOWER_VALUE: err_lo, QUANTITY.E_LOWER_VALUE: err_hi}
    catalog.entries[name].add_quantity(BLACKHOLE.MASS, bh_mass, use_sources, **quant_kwargs)

    # Add cells with similar data in the same way
    # -------------------------------------------
    cell_data = [
        # Quantity-Key               line-num, unit,        desc
        [BLACKHOLE.GALAXY_VEL_DISP_BULGE, 2, 'km/s', "Host, bulge velocity dispersion"],
        [BLACKHOLE.GALAXY_MASS_BULGE, 7, 'Msol', "Mass of the host's bulge"],
        [BLACKHOLE.GALAXY_RAD_EFF_V, 9, 'arcsec', None],
        [BLACKHOLE.GALAXY_RAD_EFF_I, 10, 'arcsec', None],
        [BLACKHOLE.GALAXY_RAD_EFF_3p6, 11, 'arcsec', None],
        [BLACKHOLE.DISTANCE, 12, 'Mpc', None],
        [BLACKHOLE.GALAXY_MORPHOLOGY, 13, None, MORPH_DESC],
    ]
    for key, num, unit, desc in cell_data:
        val, err = _get_value_and_error(lines[num].text)
        if val is not None:
            quant_kwargs = {QUANTITY.U_VALUE: unit, QUANTITY.DESC: desc}
            catalog.entries[name].add_quantity(key, val, source, **quant_kwargs)

    # Bulge Luminosity v-band
    val, err = _get_value_and_error(lines[3].text, cast=float)
    if val is not None:
        photo_kwargs = {
            PHOTOMETRY.LUMINOSITY: val, PHOTOMETRY.SOURCE: source, PHOTOMETRY.HOST: True,
            PHOTOMETRY.U_LUMINOSITY: 'Log(Lsun)', PHOTOMETRY.DESC: 'Bulge v-band Luminosoity',
            PHOTOMETRY.BAND: 'v'
        }
        if err is not None:
            photo_kwargs[PHOTOMETRY.E_LUMINOSITY] = err
        catalog.entries[name].add_photometry(**photo_kwargs)

    # Bulge Luminosity 3.6micron
    val, err = _get_value_and_error(lines[5].text, cast=float)
    if val is not None:
        photo_kwargs = {
            PHOTOMETRY.LUMINOSITY: val, PHOTOMETRY.SOURCE: source, PHOTOMETRY.HOST: True,
            PHOTOMETRY.U_LUMINOSITY: 'Log(Lsun)', PHOTOMETRY.DESC: 'Bulge v-band Luminosoity',
            PHOTOMETRY.WAVELENGTH: 3.6, PHOTOMETRY.U_WAVELENGTH: 'micron'
        }
        if err is not None:
            photo_kwargs[PHOTOMETRY.E_LUMINOSITY] = err
        catalog.entries[name].add_photometry(**photo_kwargs)

    return name


def _get_value_and_error(line, cast=None):
    val = None
    err = None

    line = line.strip()
    if line == '-' or line == '--':
        return None, None

    line = [ll.strip() for ll in line.split('±')]
    if len(line) == 2:
        val, err = line
    elif len(line) == 1 and len(line[0]):
        val = line[0]
    else:
        return None, None

    # Cast to certain `type`
    if cast is not None:
        if val is not None:
            val = cast(val)
        if err is not None:
            err = cast(err)

    return val, err


def _add_quantity_from_line(catalog, name, key, src, line, unit=None, desc=None):
    """Given an input `line`, try to parse a value and error and store to the appropriate entry.

    Arguments
    ---------
    catalog
    name : str
        Name of the entry to which to add quantity
    key : str
        Name of the quantity itself that is being stored
    src : str
        The source alias that this data comes from
    line : `bs4.element.NavigableString` object
        From which data is parsed
    unit : str
        Unit of measurement for this quantity
    desc : str
        Description of this quantity

    """
    # If the line contains a URL for an additional source, extract that
    # -----------------------------------------------------------------
    refs = [rr['href'] for rr in line.contents if isinstance(rr, bs4.element.Tag)]
    # If references are found, add them to this paper
    use_sources = [src]
    if len(refs):
        for rr in refs:
            print("{} - {}: found url '{}'.".format(name, key, rr))
            new_src = catalog.entries[name].add_source(url=rr)
            use_sources.append(new_src)
    # Multiple sources should be comma-delimited string of integers e.g. '1, 3, 4'
    use_sources = ",".join(str(src) for src in use_sources)

    # Try to get a value and an error from the input line's text
    # ----------------------------------------------------------
    val, err = _get_value_and_error(line.text)
    # If a value is given, add it
    if val is not None:
        kwargs = {}
        # Include units of measure
        if unit is not None:
            kwargs[QUANTITY.U_VALUE] = unit
        # Include an error (uncertainty) if one was found
        if err is not None:
            if desc is not None:
                desc += " with one-sigma error."
            kwargs[QUANTITY.ERROR] = err
        # Include a description if one is given
        if desc is not None:
            kwargs[QUANTITY.DESC] = desc

        # Add quantity with source
        catalog.entries[name].add_quantity(key, val, use_sources, **kwargs)

    return
