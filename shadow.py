import os
import sys
import datetime as dt
from datetime import datetime
import time

import numpy as np
from pysolar.solar import get_azimuth, get_altitude
import matplotlib.pyplot as plt

from shadow_jit.geo_helpers import(
    _return_center,
    _calc_utc_offset,
    _return_utc,
)
from shadow_jit.mask_funcs import go_fast
from _open import _open

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

        azi = 180 - azis[i]

        if i == 0:
            start = time.time()
            stack = go_fast(azi=azi, alt=alts[i], arr=arr, res=res)
            end = time.time()
            print("i = %s, Elapsed (with comp.) = %s" % (i, end - start))
        else:
            start = time.time()
            stack = np.dstack(
                (stack, go_fast(azi=azi, alt=alts[i], arr=arr, res=res))
            )
            end = time.time()
            print("i = %s, Elapsed (after comp.) = %s" % (i, end - start))

    print(stack.shape)

    np.savez('npz_timeseries/' + outfile, 
                arr=arr, 
                stack=stack, 
                sun=np.vstack(
                    (np.asarray(azis), np.asarray(alts))
                )
            )

if __name__ == '__main__':
    '''
    Run with, e.g.:
    $ python shadow.py 'data_subset' 'subset.tif' '2021-06-21 06:00:00'
    '''
    print("This is the name of the program:", sys.argv[0]) 
    print("Argument List:", str(sys.argv))
    ddir = sys.argv[1]
    d_fn = sys.argv[2]
    s_dt = sys.argv[3]

    start = time.time()
    dataset, arr, res, outfile = _open(data_dir=ddir, data_fn=d_fn)
    #plt.imshow(arr)
    #plt.show()
    loop(dataset=dataset, arr=arr, res=res, outfile=outfile, s_dt=s_dt)
    end = time.time()
    print('Total elapsed = %s' % (end - start))