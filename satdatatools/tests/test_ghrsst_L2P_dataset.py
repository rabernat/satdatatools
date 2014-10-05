import numpy as np
from satdatatools import ghrsst_L2P_dataset as ghrsst
import os

def test_ghrsst_collection():
    
    collection_list = [ghrsst.GHRSSTOpenDAPCatalog()]

    base_dir = '/Volumes/Bucket1/Data/ghrsst/data/L2P/MODIS_A/JPL/'
    if os.path.exists(base_dir):
        collection_list.append(ghrsst.GHRSSTCollection(base_dir))

    # get the first file in the collection
    for c in collection_list:
        f = c.iterate().next()
        d = ghrsst.GHRSSTFile(f)
        mask = d.proximity_confidence < 5
        assert mask.sum()==1972781
        np.testing.assert_almost_equal(
          np.ma.masked_array(d.sea_surface_temperature, mask).mean(),
          302.745145885)

