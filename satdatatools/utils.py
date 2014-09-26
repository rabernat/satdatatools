import numpy as np
from scipy import ndimage
# constants
# Earth radius
a=6.371e6

def coarsen(data, fact=2, required_count=0.5):
    """Coarsen a 2D image by factor fact. Handle mask appropriately"""
    Ny, Nx = data.shape
    assert isinstance(fact, int), type(fact)
    
    # make sure we have a masked array
    data = np.ma.masked_array(data, mask=False, keep_mask=True)

    # pad array as necessary to make it nicely divisible by fact
    p = ((0, fact - np.mod(Ny,fact)), (0, fact - np.mod(Nx,fact)))
    data = np.ma.masked_array(
                np.pad(data, p, mode='constant' ),
                np.pad(data.mask, p, mode='constant', constant_values=(True,) ))
    Ny, Nx = data.shape

    Y, X = np.ogrid[0:Ny, 0:Nx]
    regions = Nx/fact * (Y/fact) + X/fact
    dsum = ndimage.sum(data.filled(0), labels=regions, index=np.arange(regions.max() + 1))
    count = ndimage.sum(~data.mask, labels=regions, index=np.arange(regions.max() + 1))
    res = np.ma.masked_array(dsum / count, count<(required_count*fact**2))
    res.shape = (Ny/fact, Nx/fact)
    return res


def sphere_distance(lon, lat):
    """Compute the distance in the i and j direction
    between points on a 2D grid."""
    dlatj = np.abs(np.radians(np.diff(lat, axis=0)))
    dlonj = np.abs(np.radians(np.diff(lon, axis=0)))
    dlati = np.abs(np.radians(np.diff(lat, axis=1)))
    dloni = np.abs(np.radians(np.diff(lon, axis=1)))

    # fix wraparound
    dloni[dloni>(np.pi)] -= 2*np.pi
    dloni = np.abs(dloni)
    dlonj[dlonj>(np.pi)] -= 2*np.pi
    dlonj = np.abs(dlonj)
    
    #loni = np.radians(0.5*(lon[:,:-1] + lon[:,1:]))
    lati = np.radians(0.5*(lat[:,:-1] + lat[:,1:]))
    #lonj = np.radians(0.5*(lon[:-1] + lon[1:]))
    latj = np.radians(0.5*(lat[:-1] + lat[1:]))
    
    disti = a * 2*np.arcsin( np.sqrt( np.sin(dlati/2)**2 + np.cos(lati)**2 * np.sin(dloni/2)**2) )
    distj = a * 2*np.arcsin( np.sqrt( np.sin(dlatj/2)**2 + np.cos(latj)**2 * np.sin(dlonj/2)**2) )
    
    return distj, disti

def sphere_gradient(lon, lat, f):
    """Compute the gradient of f on 2D grid with given
    lon and lat."""
    distj, disti = sphere_distance(lon,lat)
    dfdi = np.diff(f,axis=1) / disti
    dfdj = np.diff(f,axis=0) / distj
    return dfdj, dfdi
