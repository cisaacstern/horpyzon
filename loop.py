import os
import sys
import datetime as dt
from datetime import datetime
import time

import rasterio
import numpy as np
from pysolar.solar import get_azimuth, get_altitude

from funcs.geo_helpers import(
    _return_center,
    _calc_utc_offset,
    _return_utc,
)
from funcs.mask_funcs import go_fast

def load(data_dir, data_fn):
    '''
    
    '''
    dataset = rasterio.open(data_dir + '/' + data_fn)
    arr = dataset.read(1)
    assert arr.shape[0] == arr.shape[1], 'Input array must be square.'
    res = arr.shape[0]
    outfile = data_fn.replace('.tif', '.npz')

    return dataset, arr, res, outfile

def loop(dataset, arr, res, outfile, s_dt):
    '''
    
    '''
    start_dt = datetime.strptime(s_dt, "%Y-%m-%d %H:%M:%S")
    lng, lat = _return_center(dat=dataset)
    offset = _calc_utc_offset(longitude=lng)
    start_utc = _return_utc(offset=offset, local_dt=start_dt)

    times = [start_utc + dt.timedelta(seconds=i*60) for i in range(0,721,15)]
    azis = [get_azimuth(lat, lng, when=times[i]) for i in range(len(times))]
    alts = [get_altitude(lat, lng, when=times[i]) for i in range(len(times))]

    azis = [int(np.around(x, decimals=0)) for x in azis]
    alts = [int(np.around(x, decimals=0)) for x in alts]

    print('start_utc is ', start_utc)
    print('ending utc is ', times[-1])
    print('azimuths are, ', azis)
    print('altitudes are, ', alts)

    for i in range(len(times)):
        if i == 0:
            start = time.time()
            stack = go_fast(azi=azis[i], alt=alts[i], arr=arr, res=res)
            end = time.time()
            print("i = %s, Elapsed (with comp.) = %s" % (i, end - start))
        else:
            start = time.time()
            stack = np.dstack(
                (stack, go_fast(azi=azis[i], alt=alts[i], arr=arr, res=res))
            )
            end = time.time()
            print("i = %s, Elapsed (after comp.) = %s" % (i, end - start))

    print(stack.shape)

    np.savez('npz_timeseries/' + outfile, 
                arr=arr, 
                stack=stack, 
                azis=np.asarray(azis),
                alts=np.asarray(alts),
            )

if __name__ == '__main__':
    print("This is the name of the program:", sys.argv[0]) 
    print("Argument List:", str(sys.argv))
    ddir = sys.argv[1]
    d_fn = sys.argv[2]
    s_dt = sys.argv[3]
    dataset, arr, res, outfile = load(data_dir=ddir, data_fn=d_fn)
    loop(dataset=dataset, arr=arr, res=res, outfile=outfile, s_dt=s_dt)
    