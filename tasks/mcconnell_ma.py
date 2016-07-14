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

from astrocats.blackholes.blackhole import BLACKHOLE

SOURCE_BIBCODE = "2013ApJ...764..184M"
SOURCE_URL = "http://adsabs.harvard.edu/abs/2013ApJ...764..184M"

PC = ap.constants.pc.cgs.value   # 1 pc in centimeters

'''
def do_ascii(catalog):
    """Process ASCII files that were extracted from datatables appearing in
    published works.
    """
    task_str = catalog.get_current_task_str()

    # 2006ApJ...645..841N
    file_path = os.path.join(
        catalog.get_current_task_repo(), '2006ApJ...645..841N-table3.csv')
    tsvin = list(csv.reader(open(file_path, 'r'), delimiter=','))
    for ri, row in enumerate(pbar(tsvin, task_str)):
        name = 'SNLS-' + row[0]
        name = catalog.add_entry(name)
        source = catalog.entries[name].add_source(
            bibcode='2006ApJ...645..841N')
        catalog.entries[name].add_quantity('alias', name, source)
        catalog.entries[name].add_quantity(
            'redshift', row[1], source, kind='spectroscopic')
        astrot = astrotime(float(row[4]) + 2450000., format='jd').datetime
        date_str = make_date_string(astrot.year, astrot.month, astrot.day)
        catalog.entries[name].add_quantity('discoverdate', date_str, source)
    catalog.journal_entries()
'''


'''
def do_asassn(catalog):
    task_str = catalog.get_current_task_str()
    asn_url = 'http://www.astronomy.ohio-state.edu/~assassin/sn_list.html'
    html = catalog.load_cached_url(asn_url, os.path.join(
        catalog.get_current_task_repo(), 'ASASSN/sn_list.html'))
    if not html:
        return
    bs = BeautifulSoup(html, 'html5lib')
    trs = bs.find('table').findAll('tr')
    for tri, tr in enumerate(pbar(trs, task_str)):
        name = ''
        ra = ''
        dec = ''
        redshift = ''
        hostoff = ''
        claimedtype = ''
        host = ''
        atellink = ''
        typelink = ''
        if tri == 0:
            continue
        tds = tr.findAll('td')
        for tdi, td in enumerate(tds):
            if tdi == 1:
                name = catalog.add_entry(td.text.strip())
                atellink = td.find('a')
                if atellink:
                    atellink = atellink['href']
                else:
                    atellink = ''
            if tdi == 2:
                discdate = td.text.replace('-', '/')
            if tdi == 3:
                ra = td.text
            if tdi == 4:
                dec = td.text
            if tdi == 5:
                redshift = td.text
            if tdi == 8:
                hostoff = td.text
            if tdi == 9:
                claimedtype = td.text
                typelink = td.find('a')
                if typelink:
                    typelink = typelink['href']
                else:
                    typelink = ''
            if tdi == 12:
                host = td.text

        sources = [catalog.entries[name].add_source(
            url=asn_url, name='ASAS-SN Supernovae')]
        typesources = sources[:]
        if atellink:
            sources.append(
                (catalog.entries[name]
                 .add_source(name='ATel ' +
                             atellink.split('=')[-1], url=atellink)))
        if typelink:
            typesources.append(
                (catalog.entries[name]
                 .add_source(name='ATel ' +
                             typelink.split('=')[-1], url=typelink)))
        sources = ','.join(sources)
        typesources = ','.join(typesources)
        catalog.entries[name].add_quantity('alias', name, sources)
        catalog.entries[name].add_quantity('discoverdate', discdate, sources)
        catalog.entries[name].add_quantity('ra', ra, sources,
                                           unit='floatdegrees')
        catalog.entries[name].add_quantity('dec', dec, sources,
                                           unit='floatdegrees')
        catalog.entries[name].add_quantity('redshift', redshift, sources)
        catalog.entries[name].add_quantity(
            'hostoffsetang', hostoff, sources, unit='arcseconds')
        for ct in claimedtype.split('/'):
            if ct != 'Unk':
                catalog.entries[name].add_quantity('claimedtype', ct,
                                                   typesources)
        if host != 'Uncatalogued':
            catalog.entries[name].add_quantity('host', host, sources)
    catalog.journal_entries()
    return

'''

def do_mcconnell_ma(catalog):
    """
    """

    DATA_URL = "http://blackhole.berkeley.edu/"

    log = catalog.log
    log.debug("do_mcconnell_ma()")
    task_str = catalog.get_current_task_str()
    task_name = catalog.current_task.name
    # Load data from URL or cached copy of it
    cached_path = os.path.join(
        catalog.get_current_task_repo(), SOURCE_BIBCODE + '.txt')
    html = catalog.load_cached_url(DATA_URL, cached_path)
    if not html:
        self.log("{} Failed to load data from '{}'.".format(task_name, DATA_URL), level=logging.WARNING)
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


    print("entries = ", entries)

    return

    # columns = []
    # # Go over each line in the file
    # html = html.splitlines()
    # for num, line in enumerate(html):
    #     if 'psdg-left' in line:
    #         print(html[num+1])
    #     continue
    #
    # return

    #
    #     # Check the first line to make sure things look right (contains updated date).
    #     if num == 0:
    #         updated = line.split('This ASCII file was last updated on ')
    #         if len(updated) != 2 or updated[-1] != 'June 26, 2013.':
    #             log.error("{} DATA HAS CHANGED!".format(task_name))
    #             return None
    #         updated = updated[-1]
    #
    #     line = line.strip()
    #     # Skip the first three lines and any blank lines
    #     if num < 3 or len(line) == 0:
    #         continue
    #
    #     # Next series of lines are column speciications
    #     # Store these, stripping off the initial
    #     if line.startswith('Col.'):
    #         # Try to parse line appropriately, return `None` on errors
    #         try:
    #             col_desc = re.split("Col. [0-9]{0,2}: ", line)[1]
    #         except Exception as err:
    #             log.error("{}: Failed to parse line {}: '{}'.".format(task_name, num, line))
    #             log.error("\t{}".format(str(err)))
    #             return None
    #
    #         columns.append(col_desc)
    #     # Get actual data from table
    #     else:
    #         data = line.split()
    #         # Make sure all of the lines of data match that of columns, and thus eachother
    #         if len(data) != len(columns):
    #             log.error(("{}: Length of columns does not match that of split data."
    #                       "\nColumns: '{}'\nData: '{}'.").format(task_name, columns, data))
    #             return None
    #
    #         # Add entry for each line of table, into catalog
    #         bh_name = _add_entry_for_data_line(catalog, data)
    #         log.debug("{}: added '{}'".format(task_name, bh_name))
    #
    # return


def do_mcconnell_ma_ascii(catalog):
    """

    Data is given in tab-deliminted ascii form with 3 lines of header, column specifications,
    and then a table of data --- with a line for each MBH entry.
    """

    DATA_URL = "http://blackhole.berkeley.edu/current_ascii.txt"

    log = catalog.log
    log.debug("do_mcconnell_ma()")
    task_str = catalog.get_current_task_str()
    task_name = catalog.current_task.name
    # Load data from URL or cached copy of it
    cached_path = os.path.join(
        catalog.get_current_task_repo(), SOURCE_BIBCODE + '.txt')
    html = catalog.load_cached_url(DATA_URL, cached_path)
    if not html:
        self.log("{} Failed to load data.".format(task_name), level=logging.WARNING)
        return

    columns = []
    # Go over each line in the file
    for num, line in enumerate(html.splitlines()):
        # Check the first line to make sure things look right (contains updated date).
        if num == 0:
            updated = line.split('This ASCII file was last updated on ')
            if len(updated) != 2 or updated[-1] != 'June 26, 2013.':
                log.error("{} DATA HAS CHANGED!".format(task_name))
                return None
            updated = updated[-1]

        line = line.strip()
        # Skip the first three lines and any blank lines
        if num < 3 or len(line) == 0:
            continue

        # Next series of lines are column speciications
        # Store these, stripping off the initial
        if line.startswith('Col.'):
            # Try to parse line appropriately, return `None` on errors
            try:
                col_desc = re.split("Col. [0-9]{0,2}: ", line)[1]
            except Exception as err:
                log.error("{}: Failed to parse line {}: '{}'.".format(task_name, num, line))
                log.error("\t{}".format(str(err)))
                return None

            columns.append(col_desc)
        # Get actual data from table
        else:
            data = line.split()
            # Make sure all of the lines of data match that of columns, and thus eachother
            if len(data) != len(columns):
                log.error(("{}: Length of columns does not match that of split data."
                          "\nColumns: '{}'\nData: '{}'.").format(task_name, columns, data))
                return None

            # Add entry for each line of table, into catalog
            bh_name = _add_entry_for_data_line(catalog, data)
            log.debug("{}: added '{}'".format(task_name, bh_name))

    return


def _add_entry_for_data_lines(catalog, lines):
    """

    Columns:
    -------
    00: Galaxy
    01: M_BH (+,-) M_sun
    02: sigma (km/s) -- bulge velocity dispersion
    03: log(L_V)
    04: M_V
    05: log(L_3.6)
    06: M_3.6
    07: M_bulge (M_sun)
    08: R_inf (arcsec)
    09: R_eff (V-band, arcsec)
    10: R_eff (i-band, arcsec)
    11: R_eff (3.6um, arcsec)
    12: Distance (Mpc)
    13: Morph
    14: BH Mass Method
    15: BH Mass Reference

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
    # At the end of the table, there is a blank row, return None
    if not len(data_name):
        return None
    name = catalog.add_entry(data_name)
    # Add this source
    source = catalog.entries[name].add_source(url=SOURCE_URL, bibcode=SOURCE_BIBCODE)
    # Add alias, if one was found
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
    quant_kwargs = {QUANTITY.UNIT: 'Msol', QUANTITY.DESC: mass_desc,
                    QUANTITY.ERROR_LOWER: err_lo, QUANTITY.ERROR_UPPER: err_hi}
    catalog.entries[name].add_quantity(BLACKHOLE.MASS, bh_mass, use_sources, **quant_kwargs)
    return name


    # Distance [Mpc]
    quant_kwargs = {QUANTITY.UNIT: 'Mpc'}
    catalog.entries[name].add_quantity(BLACKHOLE.DISTANCE, data[1], source, **quant_kwargs)


    # Galaxy velocity dispersion 'sigma', lower and upper 68% bounds [km/s]
    sigma_desc = "Host velocity dispersion with 68%% confidence bounds."
    quant_kwargs = {QUANTITY.UNIT: 'km/s', QUANTITY.DESC: sigma_desc,
                    QUANTITY.ERROR_LOWER: data[7], QUANTITY.ERROR_UPPER: data[8]}
    catalog.entries[name].add_quantity(BLACKHOLE.GALAXY_VEL_DISP, data[6], source, **quant_kwargs)

    # Galaxy Luminosity
    # V-Band ['log(LV/Lsun)']
    lum_v = data[9]
    lum_v_err = data[10]
    # Spitzer [log(L_3.6/Lsun)] -- Spitzer 3.6 um, from Sani et al. 2011
    lum_36 = data[11]
    lum_36_err = data[12]
    # Bulge Mass [Msol]
    mass_bulge = data[13]
    # Radius of influence [arcsec]
    rad_infl = data[14]
    # Galaxy morphology {(E)lliptical, S0, (S)piral}
    galaxy_morph = data[15]
    # Galaxy profile {(P)ower-law, (I)ntermediate, (C)ore, (U)ndetermined, N/A}
    galaxy_prof = data[16]
    # Effective radii
    #    Reff (V-band, arcsec)
    rad_eff_v = data[17]
    #    Reff (i-band, arcsec) -- SDSS DR7, from Beifiori et al. 2012
    rad_eff_i = data[18]
    #    Reff (3.6 um, arcsec) -- from Sani et al. 2011
    rad_eff_36 = data[19]

    # print("galaxy: {}, distance: {}, mass: {}, method: {}".format(galaxy, distance, mass, mass_method))
    return name


def _add_entry_for_data_line(catalog, data):
    """
    """
    # Create entry, store data for each MBH
    # -------------------------------------
    # Create new entry using Name of the Galaxy
    data_name = data[0]
    # Replace Some Names manually
    if data_name == 'MW':
        data_name = 'MilkyWay'
    elif data_name == 'Circ':
        data_name = 'Circinus'
    name = catalog.add_entry(data[0])
    print("Added name: {}".format(name))
    # Add this source
    source = catalog.entries[name].add_source(url=SOURCE_URL, bibcode=SOURCE_BIBCODE)
    print("Added source: {}".format(source))

    # Distance [Mpc]
    quant_kwargs = {QUANTITY.UNIT: 'Mpc'}
    catalog.entries[name].add_quantity(BLACKHOLE.DISTANCE, data[1], source, **quant_kwargs)

    # BH Mass
    #    `data[5]` includes the 'method' of mass determination
    mass_desc = "BH Mass with 68%% confidence bounds.  Method: '{}'".format(data[5])
    quant_kwargs = {QUANTITY.UNIT: 'Msol', QUANTITY.DESC: mass_desc,
                    QUANTITY.ERROR_LOWER: data[3], QUANTITY.ERROR_UPPER: data[4]}
    catalog.entries[name].add_quantity(BLACKHOLE.MASS, data[2], source, **quant_kwargs)

    # Galaxy velocity dispersion 'sigma', lower and upper 68% bounds [km/s]
    sigma_desc = "Host velocity dispersion with 68%% confidence bounds."
    quant_kwargs = {QUANTITY.UNIT: 'km/s', QUANTITY.DESC: sigma_desc,
                    QUANTITY.ERROR_LOWER: data[7], QUANTITY.ERROR_UPPER: data[8]}
    catalog.entries[name].add_quantity(BLACKHOLE.GALAXY_VEL_DISP, data[6], source, **quant_kwargs)

    # Galaxy Luminosity
    # V-Band ['log(LV/Lsun)']
    lum_v = data[9]
    lum_v_err = data[10]
    # Spitzer [log(L_3.6/Lsun)] -- Spitzer 3.6 um, from Sani et al. 2011
    lum_36 = data[11]
    lum_36_err = data[12]
    # Bulge Mass [Msol]
    mass_bulge = data[13]
    # Radius of influence [arcsec]
    rad_infl = data[14]
    # Galaxy morphology {(E)lliptical, S0, (S)piral}
    galaxy_morph = data[15]
    # Galaxy profile {(P)ower-law, (I)ntermediate, (C)ore, (U)ndetermined, N/A}
    galaxy_prof = data[16]
    # Effective radii
    #    Reff (V-band, arcsec)
    rad_eff_v = data[17]
    #    Reff (i-band, arcsec) -- SDSS DR7, from Beifiori et al. 2012
    rad_eff_i = data[18]
    #    Reff (3.6 um, arcsec) -- from Sani et al. 2011
    rad_eff_36 = data[19]

    # print("galaxy: {}, distance: {}, mass: {}, method: {}".format(galaxy, distance, mass, mass_method))
    return name
