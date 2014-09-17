import numpy as np
from scipy.io import netcdf_file
import bz2
import os
from fnmatch import fnmatch
import tempfile
import subprocess

class ghrsst_file(object):
    """A class to wrap a single ghrsst file."""

    def __init__(self, fobj):
        assert isinstance(fobj, file)
        self.ncf = netcdf_file(fobj)

        self.fname = fobj.name
        for varname in self.ncf.variables:
            self._get_and_scale_variable(varname)

    def _get_and_scale_variable(self, varname):
        v = self.ncf.variables[varname]
        data = v.data
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

class ghrsst_collection(object):
    """A way to iterate through a bunch of ghrsst L2P files."""

    def __init__(self, base_dir):
        self.base_dir = base_dir

    # I'm not sure this is the right way to do this 
    def iterate(self, use_tmpfile=True):
        for root, subdirs, files in os.walk(self.base_dir):
            for f in files:
                if fnmatch(f, '*.nc') or fnmatch(f, '*.bz2'):
                    fname = os.path.join(root, f)
                    if fnmatch(f, '*.bz2') and use_tmpfile:
                        fobj = tempfile.TemporaryFile('w+b', suffix='nc')
                        subprocess.call(["bzcat", fname], stdout=fobj)
                        fobj.seek(0)
                    elif fnmatch(f, '*.bz2'):
                        fobj = bz2.BZ2File(fname, 'rb')
                    else:
                        fobj = file(fname, 'rb')
                    yield ghrsst_file(fobj)
                    fobj.close()
