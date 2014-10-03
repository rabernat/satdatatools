import numpy as np
#from scipy.io import netcdf_file
import netCDF4
import bz2
import os
from fnmatch import fnmatch
import tempfile
import subprocess
from lxml import etree
from urllib2 import urlopen
from urlparse import urljoin

class GHRSSTFile(object):
    """A class to wrap a single ghrsst file."""

    def __init__(self, fname, variables=None, use_tmpfile=True):
        # try to figure out what we got
        #assert isinstance(fobj, file)
        assert isinstance(fname, str)
        if fname[:4]=='http':
            # it's an OpenDAP url
            self.ncf = netCDF4.Dataset(fname)
        elif os.path.exists(fname):
            if fnmatch(fname, '*.bz2') and use_tmpfile:
                fobj = tempfile.TemporaryFile('w+b', suffix='nc')
                subprocess.call(["bzcat", fname], stdout=fobj)
                fobj.seek(0)
            elif fnmatch(fname, '*.bz2'):
                fobj = bz2.BZ2File(fname, 'rb')
            else:
                fobj = file(fname, 'rb')            
            #self.ncf = netcdf_file(fobj)
            self.ncf = netCDF4.Dataset(fobj)
        else:
            raise IOError("Couldn't figure out how to open " + fname)

        self.fname = fname
        if variables is None:
            variables = self.ncf.variables.keys()
        for varname in variables:
            self._get_and_scale_variable(varname)
        #fobj.close()

    def _get_and_scale_variable(self, varname):
        v = self.ncf.variables[varname]
        data = v[:]
        if hasattr(v, '_FillValue'):
            mask = data == v._FillValue
            if np.any(mask):
                data = np.ma.masked_array(data, mask)
        if hasattr(v, 'scale_factor'):
            # can't do in place because we need type conversion
            if v.scale_factor != 1:
                data = data * v.scale_factor
        if hasattr(v, 'add_offset'):
            if v.add_offset != 0:
                data = data + v.add_offset
        setattr(self, varname, data)

class GHRSSTCollection(object):
    """A way to iterate through a bunch of ghrsst L2P files."""

    def __init__(self, base_dir):
        self.base_dir = base_dir

    # I'm not sure this is the right way to do this 
    def iterate(self, yield_fname=False):
        for root, subdirs, files in os.walk(self.base_dir):
            for f in files:
                if fnmatch(f, '*.nc') or fnmatch(f, '*.bz2'):
                    fname = os.path.join(root, f)
                    if yield_fname:
                        yield fname
                    else:
                        yield GHRSSTFile(fname)

namespace="http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0"

def crawl(baseurl, catalog):
    xml = etree.parse(urlopen(urljoin(baseurl, catalog)))
    dataset = xml.find('.//{%s}dataset' % namespace)
    for dataset in xml.iterfind('.//{%s}dataset[@urlPath]' % namespace):
        newurl = urljoin(baseurl, dataset.attrib['urlPath'])
        yield newurl
    for subdir in xml.iterfind('.//{%s}catalogRef' % namespace):
        newurl = '/'.join([dataset.attrib['name'],
                subdir.attrib['{http://www.w3.org/1999/xlink}href']])
        for url in crawl(baseurl, newurl):
            yield url

                        
class GHRSSTOpenDAPCatalog(object):
    """A way to iterate through ghrsst L2P files via OpenDAP"""
    
    def __init__(self, baseurl='http://data.nodc.noaa.gov/opendap/',
                       catalog='ghrsst/L2P/MODIS_A/JPL/catalog.xml'
                       ):
        self.baseurl = baseurl
        self.catalog = catalog

    def iterate(self):
        for datafile in crawl(self.baseurl, self.catalog):
            yield datafile


        
