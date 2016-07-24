"""Retrieve the data from [McConnell & Ma 2013]

See: http://adsabs.harvard.edu/abs/2013ApJ...764..184M
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

SOURCE_BIBCODE = "2013ApJ...764..184M"
SOURCE_URL = "http://adsabs.harvard.edu/abs/2013ApJ...764..184M"
DATA_URL = "http://blackhole.berkeley.edu/"
MORPH_DESC = ("Morphology of the host galaxy: Morphologies are  elliptical (E), "
              "lenticular (S0), spiral (S), and irregular (Irr). Inner photometric profiles "
              "are core (C), intermediate (I), and power-law (pl).")


def do_mcconnell_ma(catalog):
    """
    """
    log = catalog.log
    log.debug("do_mcconnell_ma()")
    task_str = catalog.get_current_task_str()
    task_name = catalog.current_task.name
    # Load data from URL or cached copy of it
    cached_path = SOURCE_BIBCODE + '.txt'
    html = catalog.load_url(DATA_URL, cached_path, fail=True)
    if not html:
        return

    soup = BeautifulSoup(html, 'html5lib')

    # The whole table is nested in a 'div'
    full_table = soup.find('div', id="psdgraphics-com-table")
    div_lines = full_table.find_all('div')
    num_div_lines = len(div_lines)

    # Go through each element of the tables
    interval = 16
    num = 0
    entries = 0
    while num < num_div_lines:
        div = div_lines[num]

        # Find each row of the table (starts with class='psdg-left')
        if ('class' in div.attrs) and ('psdg-left' in div['class']):
            entries += 1
            bh_name = _add_entry_for_data_lines(catalog, div_lines[num:num+interval])
            if bh_name is not None:
                log.debug("{}: added '{}'".format(task_name, bh_name))
                num += interval-1

        num += 1

    return


def _add_entry_for_data_lines(catalog, lines):
    """

    Columns:
    -------
    x    00: Galaxy
    x    01: M_BH (+,-) M_sun
    x    02: sigma (km/s) -- bulge velocity dispersion
    x    03: log(L_V) -- bulge luminosity [log of solar units]
    -    04: M_V -- v-band luminosity [magnitude] -- skip magnitude
    x    05: log(L_3.6) -- 3.6 micron bulge luminosity
    -    06: M_3.6
    x    07: M_bulge (M_sun)
    -    08: R_inf (arcsec)   -- derived from M/sigma^2 -- skip derived quantities
    x    09: R_eff (V-band, arcsec)
    x    10: R_eff (i-band, arcsec)
    x    11: R_eff (3.6um, arcsec)
    x    12: Distance (Mpc)
    x    13: Morph
    x    14: BH Mass Method
    x    15: BH Mass Reference

    Sample Entry:
    ------------
    00: <div class="psdg-left">
            <a href="http://ned.ipac.caltech.edu/.....">A1836-BCG</a> </div>
    01: <div class="psdg-bh">  3.9 (0.4,0.6) e9</div>
    02: <div class="psdg-bh">  288 &plusmn 14 </div>
    03: <div class="psdg-bh"> 11.26 &plusmn 0.06 </div>
    04: <div class="psdg-right"> -23.35 </div>
    05: <div class="psdg-bh"> -- </div>
    06: <div class="psdg-right"> -- </div>
    07: <div class="psdg-bh">--</div>
    08: <div class="psdg-right"> 0.27 </div>
    09: <div class="psdg-right"> -- </div>
    10: <div class="psdg-right">
            <a href="http://adsabs.harvard.edu/abs/2012MNRAS.419.2497B" \
                title="Reference: Beifiori 2012" >17.61</a> </div>
    11: <div class="psdg-right"> -- </div>
    12: <div class="psdg-right"> 157.5 </div>
    13: <div class="psdg-right"> E (C) </div>
    14: <div class="psdg-right"> gas </div>
    15: <div class="psdg-right"  style="width: 160px;">
            <a href="http://adsabs.harvard.edu/abs/2009ApJ...690..537D">Dalla Bonta 2009</a></div>

    """
    # Galaxy/BH Name
    # --------------
    # Remove footnotes
    data_name = lines[0].text.split('^')[0]
    # See if an alias is given in parenthesis e.g. 'N3379 (M105)'
    groups = re.search('(.*)[ ]*\((.*)\)', data_name)
    alias = None
    if groups is not None:
        groups = groups.groups()
        data_name = groups[0]
        alias = groups[1].strip()
    data_name = data_name.strip()
    # At the end of the table, there is a blank row, return None in that case
    if not len(data_name):
        return None
    name = catalog.add_entry(data_name)

    # Add this source
    source = catalog.entries[name].add_source(
        url=SOURCE_URL, bibcode=SOURCE_BIBCODE, secondary=True)
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
                    QUANTITY.E_LOWER_VALUE: err_lo, QUANTITY.E_UPPER_VALUE: err_hi}
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
