"""Retrieve the data from [McConnell & Ma 2013]

http://blackhole.berkeley.edu/
See: http://adsabs.harvard.edu/abs/2013ApJ...764..184M

Data exists in a single online table.  That data is cached locally in
    'blackholes/input/external/2013ApJ...764..184M.txt'

"""
import re
import bs4
import tqdm
import sys

from astrocats.catalog import utils
from astrocats.catalog.source import SOURCE
from astrocats.catalog.quantity import QUANTITY
from astrocats.catalog.photometry import PHOTOMETRY

from astrocats.blackholes.blackhole import BLACKHOLE, GALAXY_MORPHS, BH_MASS_METHODS

SOURCE_BIBCODE = "2013ApJ...764..184M"
SOURCE_NAME = "McConnell & Ma 2013"
SOURCE_URL = "http://adsabs.harvard.edu/abs/2013ApJ...764..184M"
DATA_URL = "http://blackhole.berkeley.edu/"
# MORPH_DESC = ("Morphology of the host galaxy: Morphologies are  elliptical (E), "
#               "lenticular (S0), spiral (S), and irregular (Irr). Inner photometric profiles "
#               "are core (C), intermediate (I), and power-law (pl).")

GAL_MORPH_DICT = {
    "E": GALAXY_MORPHS.ELLIPTICAL,
    "S0": GALAXY_MORPHS.LENTICULAR,
    "S": GALAXY_MORPHS.SPIRAL,
    "Sb": GALAXY_MORPHS.SPIRAL_BARRED,
    "Irr": GALAXY_MORPHS.IRREGULAR,
}

INNER_MORPH_DICT = {
    "C": "core",
    "I": "intermediate",
    "pl": "power-law"
}

METHOD_DICT = {
    "masers": BH_MASS_METHODS.DYN_MASERS,
    "stars": BH_MASS_METHODS.DYN_STARS,
    "gas": BH_MASS_METHODS.DYN_GAS,
}

EXPECTED_ENTRIES = 97


def do_mcconnell_ma(catalog):
    """
    """
    log = catalog.log
    log.debug("do_mcconnell_ma()")
    # Load data from URL or cached copy of it
    cached_path = SOURCE_BIBCODE + '.txt'
    html = catalog.load_url(DATA_URL, cached_path, fail=True)
    if not html:
        log.raise_error("Failed to load html!")
        return

    try:
        parse_old_webpage(catalog, html)
        return
    except Exception as err:
        log.warning("Failed on `parse_old_webpage()`; trying old cached file")

        # This is a manually added backup file of the old webpage.
        cached_path = "_" + SOURCE_BIBCODE + '.txt'
        html = catalog.load_url(None, cached_path, fail=True)
        parse_old_webpage(catalog, html)

    return


def parse_old_webpage(catalog, data):
    log = catalog.log
    task_str = catalog.get_current_task_str()
    task_name = catalog.current_task.name

    soup = bs4.BeautifulSoup(data, 'html5lib')

    # The whole table is nested in a 'div'
    full_table = soup.find('div', id="psdgraphics-com-table")
    if full_table is None:
        # print(soup)
        log.raise_error("Failed to identify `div`!")

    div_lines = full_table.find_all('div')
    num_div_lines = len(div_lines)

    # Go through each element of the tables
    interval = 16
    num = 0
    table_entries = 0
    added = 0

    with tqdm.tqdm(desc=task_str, total=EXPECTED_ENTRIES, dynamic_ncols=True) as pbar:

        while num < num_div_lines:
            div = div_lines[num]

            # Find each row of the table (starts with class='psdg-left')
            if ('class' in div.attrs) and ('psdg-left' in div['class']):
                table_entries += 1
                bh_name = _add_entry_for_data_lines(catalog, div_lines[num:num+interval])
                if bh_name is not None:
                    log.debug("{}: added '{}'".format(task_name, bh_name))
                    num += interval-1
                    pbar.update(1)
                    added += 1

                    if catalog.args.travis and (added > catalog.TRAVIS_QUERY_LIMIT):
                        log.warning("Exiting on travis limit")
                        break

            num += 1
            # pbar.update(1)

    log.info("Added {} ({} table) entries".format(added, table_entries))
    if added != EXPECTED_ENTRIES:
        log.warning("Found {} entries, expected {}!".format(added, EXPECTED_ENTRIES))
    return


def _add_entry_for_data_lines(catalog, lines):
    """

    Columns:
    -------
    x    00: Galaxy
    x    01: M_BH (+,-) M_sun
    x    02: sigma (km/s) -- bulge velocity dispersion
    x    03: log(L_V) -- bulge luminosity [log of solar units]
    x    04: M_V -- v-band luminosity [magnitude]
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
        url=SOURCE_URL, bibcode=SOURCE_BIBCODE, name=SOURCE_NAME,
        secondary=True, derive_parameters=False)

    task_name = catalog.current_task.name
    catalog.entries[name].add_data(BLACKHOLE.TASKS, task_name)

    # Add alias of name, if one was found
    if alias is not None:
        catalog.entries[name].add_quantity('alias', name, source)

    # BH Mass, looks like "  3.9 (0.4,0.6) e9"
    # ----------------------------------------
    mass_line = lines[1].text.strip()
    bh_mass, error, exp = re.search('(.*) \((.*)\) e([0-9]*)', mass_line).groups()
    exp = 'e' + exp
    bh_mass += exp
    err_lo, err_hi = error.split(',')
    err_lo += exp
    err_hi += exp
    # Convert from normal values/errors to log-space, preserve sig-figs
    bh_mass, (err_lo, err_hi) = utils.convert_lin_to_log(bh_mass, [err_lo, err_hi])

    # Line '15' has the reference[s] for the mass
    # refs = [rr['href'] for rr in lines[15].contents if isinstance(rr, bs4.element.Tag)]
    urls = []
    names = []
    for ll in lines[15].contents:
        if isinstance(ll, bs4.element.Tag):
            urls.append(ll['href'])
            names.append(ll.text.strip())
    # If references are found, add them to this paper (McConnell & Ma)
    # use_sources = [source]
    use_sources = []
    if len(urls):
        for uu, nn in zip(urls, names):
            src_kw = {SOURCE.URL: uu, SOURCE.NAME: nn}
            # Try to get a bibcode from the URL
            try:
                bibcode = uu.split('/abs/')[1]
                src_kw[SOURCE.BIBCODE] = bibcode
            except:
                pass

            new_src = catalog.entries[name].add_source(**src_kw)
            use_sources.append(new_src)
    if len(use_sources) == 0:
        use_sources.append(source)

    # Multiple sources should be comma-delimited string of integers e.g. '1, 3, 4'
    use_sources = ",".join(str(src) for src in use_sources)

    # Line '14' includes the 'method' of mass determination
    method = lines[14].text.strip()
    mass_desc = "BH Mass with one-sigma errors.  Method: '{}'".format(method)
    method = _parse_method(method)
    quant_kwargs = {QUANTITY.U_VALUE: 'log(M/Msol)', QUANTITY.DESCRIPTION: mass_desc,
                    QUANTITY.E_LOWER_VALUE: err_lo, QUANTITY.E_UPPER_VALUE: err_hi,
                    QUANTITY.KIND: method}
    catalog.entries[name].add_quantity(BLACKHOLE.MASS, bh_mass, use_sources, **quant_kwargs)

    # Add cells with similar data in the same way
    # -------------------------------------------
    cell_data = [
        # Quantity-Key               line-num, unit,        desc
        [BLACKHOLE.GALAXY_VEL_DISP_BULGE, 2, 'km/s'],
        [BLACKHOLE.GALAXY_MASS_BULGE, 7, 'log(Msol)'],
        [BLACKHOLE.GALAXY_RAD_EFF_V, 9, 'arcsec'],
        [BLACKHOLE.GALAXY_RAD_EFF_I, 10, 'arcsec'],
        [BLACKHOLE.GALAXY_RAD_EFF_3p6, 11, 'arcsec'],
        [BLACKHOLE.DISTANCE, 12, 'Mpc'],
    ]
    for key, num, unit in cell_data:
        val, err, src_kw = _get_value_and_error(lines[num])
        if val is not None:
            # Convert to log(Msol)
            if key == BLACKHOLE.GALAXY_MASS_BULGE:
                old_val = val
                val = utils.convert_lin_to_log(val)
                if err is not None:
                    err = utils.convert_lin_to_log(err)
                    sys.exit(3543)
            quant_kwargs = {QUANTITY.U_VALUE: unit}
            if err is not None:
                quant_kwargs[QUANTITY.E_VALUE] = err
            # Add source if one is found
            if src_kw is not None:
                new_src = catalog.entries[name].add_source(**src_kw)
            else:
                new_src = source

            catalog.entries[name].add_quantity(key, val, new_src, **quant_kwargs)

    # Galaxy morphology
    val, err, src_kw = _get_value_and_error(lines[13])
    if src_kw is not None:
        catalog.log.error_raise("ERROR")
    if val is None:
        raise RuntimeError("Could not get morphology from column 13: '{}'".format(lines[13].text))
    morph, desc = _parse_morphology(val)
    if morph is None:
        raise ValueError("Unrecognized morphology type '{}' ('{}')".format(val, lines[13].text))
    quant_kwargs = {}
    if desc is not None:
        quant_kwargs = {QUANTITY.DESCRIPTION: desc}
    catalog.entries[name].add_quantity(BLACKHOLE.GALAXY_MORPHOLOGY, morph, source, **quant_kwargs)

    # [3] Bulge Luminosity v-band
    val, err, src_kw = _get_value_and_error(lines[3], cast=float)
    if src_kw is not None:
        catalog.log.error_raise("ERROR")
    if val is not None:
        photo_kwargs = {
            PHOTOMETRY.LUMINOSITY: val, PHOTOMETRY.SOURCE: source, PHOTOMETRY.HOST: True,
            PHOTOMETRY.U_LUMINOSITY: 'Log(L/Lsol)',
            PHOTOMETRY.DESCRIPTION: 'Bulge v-band Luminosity',
            PHOTOMETRY.BAND: 'v'
        }
        if err is not None:
            photo_kwargs[PHOTOMETRY.E_LUMINOSITY] = err
        catalog.entries[name].add_photometry(**photo_kwargs)

    # [4] Bulge Magnitude v-band
    val, err, src_kw = _get_value_and_error(lines[4], cast=float)
    if src_kw is not None:
        catalog.log.error_raise("ERROR")
    if val is not None:
        photo_kwargs = {
            PHOTOMETRY.MAGNITUDE: val, PHOTOMETRY.SOURCE: source, PHOTOMETRY.HOST: True,
            PHOTOMETRY.U_LUMINOSITY: 'Magnitude',
            PHOTOMETRY.DESCRIPTION: 'Bulge v-band Magnitude',
            PHOTOMETRY.BAND: 'v'
        }
        if err is not None:
            photo_kwargs[PHOTOMETRY.E_LUMINOSITY] = err
        catalog.entries[name].add_photometry(**photo_kwargs)

    # [5] Bulge Luminosity 3.6 micron
    val, err, src_kw = _get_value_and_error(lines[5], cast=float)
    if src_kw is not None:
        catalog.log.error_raise("ERROR")
    if val is not None:
        photo_kwargs = {
            PHOTOMETRY.LUMINOSITY: val, PHOTOMETRY.SOURCE: source, PHOTOMETRY.HOST: True,
            PHOTOMETRY.U_LUMINOSITY: 'Log(L/Lsol)',
            PHOTOMETRY.DESCRIPTION: 'Bulge 3.6 micron Luminosity',
            PHOTOMETRY.WAVELENGTH: 3.6, PHOTOMETRY.U_WAVELENGTH: 'micron'
        }
        if err is not None:
            photo_kwargs[PHOTOMETRY.E_LUMINOSITY] = err
        catalog.entries[name].add_photometry(**photo_kwargs)

    # [6] Bulge Magnitude 3.6 micron
    val, err, src_kw = _get_value_and_error(lines[6], cast=float)
    if src_kw is not None:
        catalog.log.error_raise("ERROR")
    if val is not None:
        photo_kwargs = {
            PHOTOMETRY.MAGNITUDE: val, PHOTOMETRY.SOURCE: source, PHOTOMETRY.HOST: True,
            PHOTOMETRY.U_LUMINOSITY: 'Magnitude',
            PHOTOMETRY.DESCRIPTION: 'Bulge 3.6 micron Magnitude',
            PHOTOMETRY.WAVELENGTH: 3.6, PHOTOMETRY.U_WAVELENGTH: 'micron'
        }
        if err is not None:
            photo_kwargs[PHOTOMETRY.E_LUMINOSITY] = err
        catalog.entries[name].add_photometry(**photo_kwargs)

    return name


def _get_value_and_error(line_tag, cast=None):
    """From a line of the BH table, extract the value given and an error and/or reference if given.

    Returns
    -------
    value : str
    err : str or None
    src_kw : dict or None

    """
    val = None
    err = None

    line_text = line_tag.text.strip()
    if line_text == '-' or line_text == '--':
        return None, None, None

    line_text = [ll.strip() for ll in line_text.split('±')]
    if len(line_text) == 2:
        val, err = line_text
    elif len(line_text) == 1 and len(line_text[0]):
        val = line_text[0]
    else:
        return None, None, None

    # Cast to certain `type`
    if cast is not None:
        if val is not None:
            val = cast(val)
        if err is not None:
            err = cast(err)

    # Extract source if one is included
    # ---------------------------------
    src_kw = None
    for child in line_tag.children:
        if not isinstance(child, bs4.element.Tag):
            continue

        if child.name != 'a':
            continue

        url = child.attrs['href']
        name = child.attrs['title'].split('Reference: ')[-1]
        src_kw = {SOURCE.URL: url, SOURCE.NAME: name}
        # Try to get a bibcode from the URL
        try:
            bibcode = url.split('/abs/')[1]
            src_kw[SOURCE.BIBCODE] = bibcode
        except:
            pass

    return val, err, src_kw


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
            kwargs[QUANTITY.DESCRIPTION] = desc

        # Add quantity with source
        catalog.entries[name].add_quantity(key, val, use_sources, **kwargs)

    return


def _parse_morphology(val):
    vals = [vv.strip(' ()') for vv in val.split()]
    # Entires may be things like "E/S0", record both
    morph = [GAL_MORPH_DICT[vv] for vv in vals[0].split('/')]
    morph = "/".join(morph)
    # Inner photometric profiles might also be given
    desc = None
    if len(vals) == 2:
        desc = "inner photometric profile: {}".format(INNER_MORPH_DICT[vals[1]])
    return morph, desc


def _parse_method(val):
    vals = [vv.strip() for vv in val.split(',')]
    method = [METHOD_DICT[vv] for vv in vals]
    method = ", ".join(method)
    return method
