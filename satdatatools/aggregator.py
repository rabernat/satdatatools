import numpy as np
from scipy.io import netcdf_file
import bz2
import os
from fnmatch import fnmatch
from numba import jit

@jit
def binsum2D(data, i, j, Nx, Ny):
    data_binned = np.zeros((Ny,Nx), dtype=data.dtype)
    N = len(data)
    for n in range(N):
        data_binned[j[n],i[n]] += data[n]
    return data_binned

class latlon_aggregator(object):
    """A class for aggregating L2 data into a gridded dataset."""

    def __init__(self, dlon=1., dlat=1., lonlim=(-180,180), latlim=(-90,90)):
        self.dlon = dlon
        self.dlat = dlat
        self.lonmin = lonlim[0]
        self.lonmax = lonlim[1]
        self.latmin = latlim[0]
        self.latmax = latlim[1]
        # define grids
        self.lon = np.arange(self.lonmin, self.lonmax, dlon)
        self.lat = np.arange(self.latmin, self.latmax, dlat)
        self.Nx, self.Ny = len(self.lon), len(self.lat)
        self.lonc = self.lon + self.dlon/2
        self.latc = self.lat + self.dlat/2
    
    def binsum(self, data, lon, lat):
        """Bin the data into the lat-lon grid.
        Returns gridded dataset."""
        i = np.digitize(lon.ravel(), self.lon)
        j = np.digitize(lat.ravel(), self.lat)
        return binsum2D(data.ravel(), i, j, self.Nx, self.Ny)

    def zeros(self, dtype=np.dtype('f4')):
        return np.zeros((self.Ny, self.Nx), dtype=dtype)
