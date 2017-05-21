"""Load and process the data from [Tremaine+ 2002]

http://adsabs.harvard.edu/abs/2002ApJ...574..740T
Table 1, manually copied to file 'blackholes/input/internal/tremaine+2002.txt'.

"""
import logging
import os
import csv
import re
import bs4
from bs4 import BeautifulSoup
import astropy as ap
import astropy.constants
import tqdm

from astrocats.catalog import utils
from astrocats.catalog.source import SOURCE
from astrocats.catalog.quantity import QUANTITY
from astrocats.catalog.photometry import PHOTOMETRY
from astrocats.catalog.utils import dict_to_pretty_string

from astrocats.blackholes.blackhole import BLACKHOLE, GALAXY_MORPHS, BH_MASS_METHODS

SOURCE_BIBCODE = "2002ApJ...574..740T"
SOURCE_NAME = "Tremaine+2002"
SOURCE_URL = "http://adsabs.harvard.edu/abs/2002ApJ...574..740T"
MORPH_DESC = ("Galaxy morphologies are one of:"
              "{'SBbc', 'E5', 'E4', 'Sbc', 'E3', 'Sb', 'E1', 'S0', 'E2', 'E0', 'SB0'}.")
DATA_FILENAME = "tremaine+2002.txt"

METHOD_DICT = {
    "s": BH_MASS_METHODS.DYN_STARS,
    "p": BH_MASS_METHODS.DYN_STARS,
    "g": BH_MASS_METHODS.DYN_GAS,
    "m": BH_MASS_METHODS.DYN_MASERS,
    "a": BH_MASS_METHODS.DYN_MASERS,
    "3I": BH_MASS_METHODS.DYN_MODELS
}

FULL_METHOD_DICT = {
    's': "(s) stellar radial velocities",
    'p': "(p) stellar proper motions",
    'm': "(m) maser radial velocities",
    'a': "(a) maser accelerations",
    'g': "(g) rotating gas disk from emission-line observations",
    '3I': "(3I) axisymmetric dynamical models, including three integrals of motion",
}

REFS_NAMES = {
    '1': "Chakrabarty & Saha 2001",
    '2': "Verolme et al. 2002",
    '3': "Tremaine 1995",
    '4': "Kormendy & Bender 1999",
    '5': "Bacon et al. 2001",
    '6': "Gebhardt et al. 2002",
    '7': "Pinkney et al. 2003",
    '8': "Bower et al. 2001",
    '9': "Greenhill & Gwinn 1997",
    '10': "Sarzi et al. 2001",
    '11': "Kormendy et al. 1996a",
    '12': "Barth et al. 2001b",
    '13': "Kormendy et al. 1998",
    '14': "Gebhardt et al. 2000b",
    '15': "Herrnstein et al. 1999",
    '16': "Ferrarese, Ford, & Jaffe 1996",
    '17': "Cretton & van den Bosch 1999",
    '18': "Harms et al. 1994",
    '19': "Macchetto et al. 1997",
    '20': "M. E. Kaiser et al. 2002, in preparation",
    '21': "Ferrarese & Ford 1999",
    '22': "van der Marel & van den Bosch 1998",
    '23': "Cappellari et al. 2002"
}

REFS_BIBS = {
    '1': "2001AJ....122..232C",
    '2': "2002MNRAS.335..517V",
    '3': "1995AJ....110..628T",
    '4': "1999ApJ...522..772K",
    '5': "2001A%26A...371..409B",
    '6': "2003ApJ...583...92G",
    '7': "2003ApJ...596..903P",
    '8': "2001ApJ...550...75B",
    '9': "1997Ap%26SS.248..261G",
    '10': "2001ApJ...550...65S",
    '11': "1996ApJ...459L..57K",
    '12': "2001ApJ...555..685B",
    '13': "1998AJ....115.1823K",
    '14': "2000AJ....119.1157G",
    '15': "1999Natur.400..539H",
    '16': "1996ApJ...470..444F",
    '17': "1999ApJ...514..704C",
    '18': "1994ApJ...435L..35H",
    '19': "1997ApJ...489..579M",
    '20': None,
    '21': "1999ApJ...515..583F",
    '22': "1998AJ....116.2220V",
    '23': "2002ApJ...578..7872"
}

REFS_URLS = {
    '1': "http://adsabs.harvard.edu/abs/2001AJ....122..232C",
    '2': "http://adsabs.harvard.edu/abs/2002MNRAS.335..517V",
    '3': "http://adsabs.harvard.edu/abs/1995AJ....110..628T",
    '4': "http://adsabs.harvard.edu/abs/1999ApJ...522..772K",
    '5': "http://adsabs.harvard.edu/abs/2001A%26A...371..409B",
    '6': "http://adsabs.harvard.edu/abs/2003ApJ...583...92G",
    '7': "http://adsabs.harvard.edu/abs/2003ApJ...596..903P",
    '8': "http://adsabs.harvard.edu/abs/2001ApJ...550...75B",
    '9': "http://adsabs.harvard.edu/abs/1997Ap%26SS.248..261G",
    '10': "http://adsabs.harvard.edu/abs/2001ApJ...550...65S",
    '11': "http://adsabs.harvard.edu/abs/1996ApJ...459L..57K",
    '12': "http://adsabs.harvard.edu/abs/2001ApJ...555..685B",
    '13': "http://adsabs.harvard.edu/abs/1998AJ....115.1823K",
    '14': "http://adsabs.harvard.edu/abs/2000AJ....119.1157G",
    '15': "http://adsabs.harvard.edu/abs/1999Natur.400..539H",
    '16': "http://adsabs.harvard.edu/abs/1996ApJ...470..444F",
    '17': "http://adsabs.harvard.edu/abs/1999ApJ...514..704C",
    '18': "http://adsabs.harvard.edu/abs/1994ApJ...435L..35H",
    '19': "http://adsabs.harvard.edu/abs/1997ApJ...489..579M",
    '20': None,
    '21': "http://adsabs.harvard.edu/abs/1999ApJ...515..583F",
    '22': "http://adsabs.harvard.edu/abs/1998AJ....116.2220V",
    '23': "http://adsabs.harvard.edu/abs/2002ApJ...578..787C"
}


TONRY_ETAL_2001 = {
    "name": "Tonry et al. 2001",
    "bibcode": "2001ApJ...546..681T",
    "url": "http://adsabs.harvard.edu/abs/2001ApJ...546..681T",
}


def do_tremaine_2002(catalog):
    """
    """
    log = catalog.log
    log.debug("do_mcconnell_ma()")
    task_str = catalog.get_current_task_str()
    task_name = catalog.current_task.name
    task_dir = catalog.get_current_task_repo()

    # Go through each element of the tables
    interval = 16
    num = 0
    entries = 0

    data_fname = os.path.join(task_dir, DATA_FILENAME)
    log.info("Input filename '{}'".format(data_fname))
    if not os.path.exists(data_fname):
        utils.log_raise(log, "File not found '{}'".format(data_fname), IOError)

    with tqdm.tqdm(desc=task_str, total=31, dynamic_ncols=True) as pbar:

        with open(data_fname, 'r') as data:
            spamreader = csv.reader(data, delimiter=' ')
            for row in spamreader:
                if len(row) <= 1 or row[0].startswith('#'):
                    continue

                bh_name = _add_entry_for_data_line(catalog, row)
                if bh_name is not None:
                    log.debug("{}: added '{}'".format(task_name, bh_name))
                    num += 1

                pbar.update(1)

    log.info("Added {} entries".format(num))
    return


def _add_entry_for_data_line(catalog, line):
    """

    Sample Entry:
    ------------
    ```MilkyWay SBbc 17.65 1.8e6(1.5,2.2) s,p 103 0.008 1.0,K 1```

    Columns:
    -------
    0 - Galaxy Name
    1 - Galaxy Type
    2 - M_B(B-band magnitude)
    3 - M_BH(Low, High) in solar masses
    4 - Method (for mass determination; see above)
    5 - sigma_1 (km/s) - (see above)
    6 - Distance (Mpc)
    7 - M/L,Band  (mass to light-ratio in the given band
    8 - references for BH masses (see above)

    """
    log = catalog.log
    log.debug("tremaine2002._add_entry_for_data_line()")
    if len(line) != 9:
        log.warning("length of line: '{}', expected 9!  '{}'".format(len(line), line))
        return None

    # [0] Galaxy/BH Name and Aliases
    # ------------------------------
    #    Alias may be given as "name=alias"
    data_name = line[0].strip()
    # Use full 'NGC' instead of just N
    data_name = data_name.replace('N', 'NGC')
    alias = None
    if '=' in data_name:
        data_name, alias = data_name.split('=')

    name = catalog.add_entry(data_name)
    # Add this source
    source = catalog.entries[name].add_source(
        url=SOURCE_URL, bibcode=SOURCE_BIBCODE, name=SOURCE_NAME, secondary=True)

    # Add alias of name, if one was found
    if alias is not None:
        # log.warning("Adding alias '{}' to name '{}'".format(alias, name))
        catalog.entries[name].add_quantity('alias', alias, source)

    # [1] Galaxy Morphology
    # ---------------------
    morph = _parse_morphology(line[1].strip())
    catalog.entries[name].add_quantity(BLACKHOLE.GALAXY_MORPHOLOGY, morph, source)

    # [2] B-Band Magnitude
    # --------------------
    magn_b = line[2].strip()
    photo_kwargs = {
        PHOTOMETRY.MAGNITUDE: magn_b, PHOTOMETRY.SOURCE: source, PHOTOMETRY.HOST: True,
        PHOTOMETRY.U_LUMINOSITY: 'Magnitude',
        PHOTOMETRY.DESCRIPTION: 'B-Band Magnitude ("Galaxy hot component")',
        PHOTOMETRY.BAND: 'B'
    }
    catalog.entries[name].add_photometry(**photo_kwargs)

    # [8] Mass Determination References
    # ---------------------------------
    refs = _parse_refs(line[8])
    # If references are found, add them to this paper
    use_sources = [source]
    for rr in refs:
        ref_name, ref_bib, ref_url = rr
        bib_kw = {'name': ref_name}
        if ref_bib is not None:
            bib_kw['bibcode'] = ref_bib
            bib_kw['url'] = ref_url
        new_src = catalog.entries[name].add_source(**bib_kw)
        use_sources.append(new_src)
    # Multiple sources should be comma-delimited string of integers e.g. '1, 3, 4'
    use_sources = ",".join(str(src) for src in use_sources)

    # [3] BH Mass (and method [4])
    # ----------------------------
    bhm, bhm_lo, bhm_hi = _get_mass_value_and_error(line[3])
    mass_method, method_desc = _parse_mass_method(line[4])
    mass_desc = "BH Mass with one-sigma errors.  Method(s): '{}'".format(method_desc)
    quant_kwargs = {QUANTITY.U_VALUE: 'Msol', QUANTITY.DESCRIPTION: mass_desc,
                    QUANTITY.E_LOWER_VALUE: bhm_lo, QUANTITY.E_UPPER_VALUE: bhm_hi,
                    QUANTITY.KIND: mass_method}
    catalog.entries[name].add_quantity(BLACKHOLE.MASS, bhm, use_sources, **quant_kwargs)

    # [5] Velocity Dispersion
    # -----------------------
    sigma_1 = line[5].strip()
    sigma_desc = "RMS dispersion within a slit aperture of length 2 r_e"
    quant_kwargs = {QUANTITY.U_VALUE: 'km/s', QUANTITY.DESCRIPTION: sigma_desc}
    catalog.entries[name].add_quantity(
        BLACKHOLE.GALAXY_VEL_DISP, sigma_1, source, **quant_kwargs)

    # [6] Distance
    # ------------
    dist = line[6].strip()
    #    This is the source used for distances (when possible)
    dist_src = catalog.entries[name].add_source(**TONRY_ETAL_2001)
    quant_kwargs = {QUANTITY.U_VALUE: 'Mpc'}
    catalog.entries[name].add_quantity(
        BLACKHOLE.DISTANCE, dist, dist_src, **quant_kwargs)

    # [7] Mass-to-Light Ratio
    # -----------------------
    ratio_band = _parse_mass_to_light(line[6].strip())
    if ratio_band is not None:
        ratio, band = ratio_band
        quant_kwargs = {QUANTITY.DESCRIPTION: "In band: '{}'".format(band)}
        catalog.entries[name].add_quantity(
            BLACKHOLE.GALAXY_MASS_TO_LIGHT_RATIO, ratio, source, **quant_kwargs)

    return name


def _parse_morphology(val):
    """

    Morphologies are one of:
        {'SBbc', 'E5', 'E4', 'Sbc', 'E3', 'Sb', 'E1', 'S0', 'E2', 'E0', 'SB0'}
    Output morphs are from `GALAXY_MORPHS` dict, given specification added in parenthesis,
        e.g. "Elliptical (E3)"

    """
    if val.startswith('SB'):
        morph = GALAXY_MORPHS.SPIRAL_BARRED
    elif val.startswith('S'):
        morph = GALAXY_MORPHS.SPIRAL
    elif val.startswith('E'):
        morph = GALAXY_MORPHS.ELLIPTICAL
    else:
        raise ValueError("Unrecognized morphology '{}'".format(val))

    morph += " ({})".format(val)
    return morph


def _parse_mass_method(val):
    vals = [vv.strip() for vv in val.split(',')]
    method = [METHOD_DICT[vv] for vv in vals]
    desc = [FULL_METHOD_DICT[vv] for vv in vals]
    method = ", ".join(method)
    desc = ", ".join(desc)
    return method, desc


def _get_mass_value_and_error(raw):
    """Entries look like "1.8e6(1.5,2.2)"
    """
    val, err = raw.split('(')
    err_lo, err_hi = err.split(',')
    err_hi.strip(')')
    exp = "e" + val.split('e')[-1]
    err_lo += exp
    err_hi += exp
    return val, err_lo, err_hi


def _parse_refs(val):

    def _get_refs_from_dict(val):
        name = REFS_NAMES[val]
        bib = REFS_BIBS[val]
        url = REFS_URLS[val]
        return name, bib, url

    vals = [vv.strip() for vv in val.split(',')]
    refs = [_get_refs_from_dict(vv) for vv in vals]
    return refs


def _parse_mass_to_light(val):
    """Empty values should be '-', otherwise looks like "1.85,I"
    """
    try:
        ratio, band = val.split(',')
    except ValueError:
        return None

    return ratio, band
