import numpy as np

# constants
# Earth radius
a=6.371e6

def sphere_distance(lon, lat):

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
    distj, disti = sphere_distance(lon,lat)
    dfdi = np.diff(f,axis=1) / disti
    dfdj = np.diff(f,axis=0) / distj
    return dfdj, dfdi
