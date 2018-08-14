"""Load and process the data from [Shen+ 2008]

http://adsabs.harvard.edu/abs/2008ApJ...680..169S
Data from Shen+2008 catalog, downloaded from:
    VizieR (http://vizier.cfa.harvard.edu/viz-bin/VizieR?-source=J/ApJ/680/169)
To:
    'blackholes/input/internal/shen+2008.tsv'
Description in paper Table 1, copied below:


TABLE 1
Catalog Format
Column Format Description

 0 ......................  A18    SDSS DR5 designation hhmmss.ss+ddmmss.s (J2000.0)


[*1]: K-corrected to z = 2, following Richards et al. 2006a;

Notes:
(1) Objects in this table are in the same order as in the DR5 quasar catalog (Schneider+2007);

"""
import os
import csv
import tqdm

from astrocats import utils
from astrocats.structures.quantity import QUANTITY
from astrocats.structures.photometry import PHOTOMETRY

from astrocats.blackholes.blackhole import BLACKHOLE, BH_MASS_METHODS

SOURCE_BIBCODE = "2008ApJ...680..169S"
SOURCE_NAME = "Shen+2008"
SOURCE_URL = "http://adsabs.harvard.edu/abs/2008ApJ...680..169S"

DATA_FILENAME = "wevers_1706.08965_table-3.tex"
# EXPECTED_TOTAL = 77429
# Note that the VizieR table has 3 additional columns at the end relative to Table 1 descriptions
# NUM_COLUMNS = 30
JOURNAL_INTERNAL = 1000


def do_wevers_2017(catalog=None):
    """
    """
    if catalog is None:
        import logging
        log = utils.get_logger(stream_level=logging.DEBUG)
        task_str = "Wevers+2017"
        task_name = task_str
        task_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.pardir))
        task_dir = os.path.join(task_dir, "input", "internal", "")
        log.warning("Running task '{}' directly".format(task_str))
    else:
        log = catalog.log
        log.debug("shen_2008.do_shen_2008()")
        task_str = catalog.get_current_task_str()
        task_name = catalog.current_task.name
        task_dir = catalog.get_current_task_repo()

    # Go through each element of the tables
    num = 0
    line_num = 0
    count = 0

    data_fname = os.path.join(task_dir, DATA_FILENAME)
    log.info("Input filename '{}'".format(data_fname))
    if not os.path.exists(data_fname):
        log.raise_error("File not found '{}'".format(data_fname), IOError)

    import astropy as ap
    # with open(data_fname, 'r') as indata:
    #     data = indata.read()
    #
    # print(data)
    # data = ap.table.Table.read(data.encode('unicode-escape'), format='ascii.latex')
    # print(data)

    data = ap.table.Table.read(data_fname)  # , format='ascii.latex')
    print(data)

    return data

    with tqdm.tqdm(desc=task_str, total=EXPECTED_TOTAL, dynamic_ncols=True) as pbar:

        with open(data_fname, 'r') as data:
            spamreader = csv.reader(data, delimiter='|')
            for row in spamreader:
                line_num += 1
                if len(row) == 0 or row[0].startswith('#'):
                    continue
                else:
                    count += 1
                    if count < 4:
                        continue

                bh_name = _add_entry_for_data_line(catalog, row)
                if bh_name is not None:
                    log.debug("{}: added '{}'".format(task_name, bh_name))
                    num += 1

                    if (JOURNAL_INTERNAL is not None) and (num % JOURNAL_INTERNAL == 0):
                        catalog.journal_entries()

                    if catalog.args.travis and (num > catalog.TRAVIS_QUERY_LIMIT):
                        log.warning("Exiting on travis limit")
                        break

                pbar.update(1)

    log.info("Added {} entries".format(num))
    if (num != EXPECTED_TOTAL) and (not catalog.args.travis):
        log.warning("Number of entries added {} does not match expectation {}!".format(
            num, EXPECTED_TOTAL))

    return


def _add_entry_for_data_line(catalog, line):
    """

    Sample Entries:
    --------------
    000132.83+145608.0|000.386795|+14.935573| 0.3989| 18.898| -23.131| 45.356|  751|  303| 52251
        |0|1|1|0|   4026|    2.450|  8.119|   4699|    2.671|  8.114|       |         |
        |8.119|       |  10.293|Sloan|DR5|Simbad|NED

    000135.51-004206.7|000.397978|-00.701886| 3.5779| 19.183| -27.951| 47.015| 1489|  104| 52991
        |0|0|0|1|       |         |       |       |         |       |   6207|  271.312|  9.536
        |9.536|       |   3.937|Sloan|DR5|Simbad|NED

    Columns:
    -------
    [x]  0  SDSS     (A18)   SDSS-DR5 Object Designation (HHMMSS.ss+DDMMSS.s, J2000)
    [x]  1  RAJ2000  (F10.6) Right Ascension in decimal degrees (J2000)
    [x]  2  DEJ2000  (F10.6) Declination in decimal degrees (J2000)
    [x]  3  z        (F7.4)  Redshift
    [ ]  4  imag     (F7.3)  PSF i-band apparent magnitude (1)
    [x]  5  iMAG     (F8.3)  PSF i-band absolute magnitude, K-corrected to z=2
    [x]  6  logLbol  (F7.3)  ? log of bolometric luminosity (erg/s)
    [ ]  7  Plate    (I5)    Plate number
    [ ]  8  Fiber    (I5)    Fiber identification number
    [x]  9  ObsDate  (I6)    MJD date of spectroscopic observation
    [ ] 10  F        (I1)    [0/1] FIRST selection flag
    [ ] 11  R        (I1)    [0/1] ROSAT selection flag
    [ ] 12  U        (I1)    [0/1] Uniform selection flag
    [ ] 13  B        (I1)    [0/1] Broad Absoprtion Lines flag
    [x] 14  WHb      (I7)    ? Full-width at Half-Maximum of H{beta}
    [x] 15  L5100    (F9.3)  ? Monochromatic luminosity at 5100{AA}
    [x] 16  BHHb     (F7.3)  ? Virial mass of black hole estimated using H{beta} (log scale)
    [x] 17  WMgII    (I7)    ? Full-width at Half-Maximum of MgII
    [x] 18  L3000    (F9.3)  ? Monochromatic luminosity at 3000{AA}	[ucd=phys.luminosity]
    [x] 19  BHMgII   (F7.3)  ? Virial mass of black hole estimated using MgII (log scale)
    [x] 20  WCIV     (I7)    ? Full-width at Half-Maximum of CIV
    [x] 21  L1350    (F9.3)  ? Monochromatic luminosity at 1350{AA}
    [x] 22  BHCIV    (F7.3)  ? Virial mass of black hole estimated using CIV (log scale)
    [x] 23  BHvir    (F7.3)  ? Virial mass of black hole (3)
    [ ] 24  CIVMgII  (I7)    ? CIV-MgII blueshift
    [ ] 25  S  N	 (F8.3)  Mean spectrum signal-to-noise ratio
    [ ] 26  Sloan    (a5)    SDSS details from most recent SDSS data release

    """
    log = catalog.log
    # log.debug("shen_2008._add_entry_for_data_line()")
    if len(line) != NUM_COLUMNS:
        log.warning("length of line: '{}', expected {}!  '{}'".format(
            len(line), NUM_COLUMNS, line))
        return None

    line = [ll.strip() for ll in line]

    # [0] SDSS Galaxy/BH Name
    # -----------------------
    data_name = "SDSS" + line[0]
    name = catalog.add_entry(data_name)
    # Add this source
    source = catalog.entries[name].add_source(
        url=SOURCE_URL, bibcode=SOURCE_BIBCODE, name=SOURCE_NAME, secondary=False)

    task_name = catalog.current_task.name
    catalog.entries[name].add_data(BLACKHOLE.TASKS, task_name)

    # [1/2] RA/DEC
    catalog.entries[name].add_quantity(BLACKHOLE.RA, line[1], source)
    catalog.entries[name].add_quantity(BLACKHOLE.DEC, line[2], source)

    # [3] Redshift
    catalog.entries[name].add_quantity(BLACKHOLE.REDSHIFT, line[3], source)

    # [4] i-band apparent magnitude
    # photo_kwargs = {
    #     PHOTOMETRY.MAGNITUDE: line[4],
    #     PHOTOMETRY.SOURCE: source,
    #     PHOTOMETRY.HOST: False,
    #     PHOTOMETRY.U_LUMINOSITY: 'apparent Magnitude',
    #     PHOTOMETRY.DESCRIPTION: 'PSF i-band apparent magnitude',
    #     PHOTOMETRY.BAND: 'i',
    #     PHOTOMETRY.INCLUDES_HOST: True,
    # }
    # catalog.entries[name].add_photometry(**photo_kwargs)

    # [9] Observation date
    # convert from MJD to string YYYY/MM/DD
    # obs_date = ap.time.Time(int(line[9]), format='mjd').datetime.strftime('%Y/%m/%d')
    # obs_date = float(line[9])
    obs_date = line[9]

    # [5] i-band Absolute magnitude (z=2)
    if len(line[5]):
        photo_kwargs = {
            PHOTOMETRY.MAGNITUDE: line[5],
            PHOTOMETRY.SOURCE: source,
            PHOTOMETRY.HOST: False,
            PHOTOMETRY.U_LUMINOSITY: 'Absolute Magnitude',
            PHOTOMETRY.DESCRIPTION: 'PSF i-band absolute magnitude, K-corrected to z=2',
            PHOTOMETRY.BAND: 'i',
            PHOTOMETRY.INCLUDES_HOST: True,
            PHOTOMETRY.KCORRECTED: True,
            PHOTOMETRY.TIME: obs_date,
            PHOTOMETRY.U_TIME: 'MJD',
        }
        if not catalog.entries[name].add_photometry(**photo_kwargs):
            log.raise_error("Adding photometry failed for '{}'\n:{}".format(
                name, photo_kwargs))

    # [6] Luminosity Bolometric
    if len(line[6]):
        photo_kwargs = {
            PHOTOMETRY.LUMINOSITY: line[6],
            PHOTOMETRY.SOURCE: source,
            PHOTOMETRY.HOST: False,
            PHOTOMETRY.U_LUMINOSITY: 'log (L/[erg/s])',
            PHOTOMETRY.DESCRIPTION: 'Using bolometric corrections in Richards+2006b',
            PHOTOMETRY.BAND: 'bolometric',
            PHOTOMETRY.INCLUDES_HOST: True,
            PHOTOMETRY.TIME: obs_date,
            PHOTOMETRY.U_TIME: 'MJD',
        }
        if not catalog.entries[name].add_photometry(**photo_kwargs):
            log.raise_error("Adding photometry failed for '{}'\n:{}".format(
                name, photo_kwargs))

    # [14-22] FWHM, Mass, and Monochromatic Luminosities by line
    line_names = ["H-Beta", "Mg-II", "C-IV"]
    line_waves = ["5100", "3000", "1350"]
    line_vars = ["HBETA", "MGII", "CIV"]
    for ii, (nn, ww, vv) in enumerate(zip(line_names, line_waves, line_vars)):
        line_name = "{} ({} A)".format(nn, ww)

        # FWHM for this line
        col = 14 + ii*3
        if len(line[col]):
            var = getattr(BLACKHOLE, "FWHM_" + vv)
            desc = "Full-width at Half-Maximum of {}".format(line_name)
            quant_kwargs = {QUANTITY.U_VALUE: 'km/s', QUANTITY.DESCRIPTION: desc}
            catalog.entries[name].add_quantity(var, line[col], source, **quant_kwargs)

        # Luminosity from this line
        col = 15 + ii*3
        if len(line[col]):
            desc = 'Monochromatic luminosity for {} (lambda*L_lambda)'.format(line_name)
            photo_kwargs = {
                PHOTOMETRY.LUMINOSITY: line[col],
                PHOTOMETRY.SOURCE: source,
                PHOTOMETRY.HOST: False,
                PHOTOMETRY.U_LUMINOSITY: 'log (L/[erg/s])',
                PHOTOMETRY.DESCRIPTION: desc,
                PHOTOMETRY.WAVELENGTH: ww,
                PHOTOMETRY.U_WAVELENGTH: 'Angstrom',
                PHOTOMETRY.TIME: obs_date,
                PHOTOMETRY.U_TIME: 'MJD',
            }
            if not catalog.entries[name].add_photometry(**photo_kwargs):
                log.raise_error("Adding photometry failed for '{}' ({}) \n:{}".format(
                    name, nn, photo_kwargs))

        # Mass from this Line
        col = 16 + ii*3
        if len(line[col]):
            var = BLACKHOLE.MASS
            mass_method = getattr(BH_MASS_METHODS, "VIR_" + vv)
            desc = "Virial mass estimated using {}".format(line_name)
            quant_kwargs = {QUANTITY.U_VALUE: 'log(M/Msol)',
                            QUANTITY.DESCRIPTION: desc,
                            QUANTITY.KIND: mass_method}
            catalog.entries[name].add_quantity(var, line[col], source, **quant_kwargs)

    # [23] Mass from optimal line (based on redshift)
    val = line[23]
    if len(val):
        desc = ("Virial BH-Mass Using H-Beta for z < 0.7; "
                "Mg-ii for 0.7 < z < 1.9; and C-iv for z > 1.9")
        quant_kwargs = {QUANTITY.U_VALUE: 'log(M/Msol)',
                        QUANTITY.DESCRIPTION: desc,
                        QUANTITY.KIND: BH_MASS_METHODS.VIR}
        catalog.entries[name].add_quantity(BLACKHOLE.MASS, val, source, **quant_kwargs)

    return name


if __name__ == "__main__":
    do_wevers_2017()
