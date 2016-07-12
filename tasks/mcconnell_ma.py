"""Retrieve the data from [McConnell & Ma 2013]

See: http://adsabs.harvard.edu/abs/2013ApJ...764..184M
"""
import logging
import os
from bs4 import BeautifulSoup

from astrocats.catalog.utils import pbar

'''
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

class McConnell_Ma:

    def __init__(self, catalog):
        self._catalog = catalog
        self._log = catalog.log
        self.name = type(self).__name__
        self.nice_name = 'McConnell & Ma 2013 Data'
        self.active = True
        self.update = False
        self.archived = True
        self.bibcode = '2013ApJ...764..184M'
        self.url = 'http://adsabs.harvard.edu/abs/2013ApJ...764..184M'
        return

    def log(self, msg, level=logging.DEBUG):
        """Log a message at the desired level prepending the name of this object.
        """
        log_msg = '{}: {}'.format(self.name, msg)
        self._catalog.log.log(level, log_msg)
        return

    def load(self):
        task_str = catalog.get_current_task_str()
        data_url = 'http://blackhole.berkeley.edu/current_ascii.txt'
        cached_path = os.path.join(
            catalog.get_current_task_repo(), self.bibcode + '.txt')
        html = catalog.load_cached_url(data_url, cached_path)
        if not html:
            self.log("Failed to load data.", level=logging.WARNING)
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
