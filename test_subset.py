import os
import datetime
import time

import rasterio
import numpy as np
import matplotlib.pyplot as plt
from pysolar.solar import get_azimuth, get_altitude

from geo_helpers import(
    _return_center,
    _calc_utc_offset,
    _return_utc,
)
from mask_funcs import go_fast

#---------------------------------------------------------------------
# Arguments
#---------------------------------------------------------------------
data_dir = 'data_subset'
data_lst = os.listdir(data_dir)
data_fn = data_lst[0]
dataset = rasterio.open(data_dir + '/' + data_fn)
arr = dataset.read(1)
assert arr.shape[0] == arr.shape[1], 'Input array must be square.'
res = arr.shape[0]

local_dt = datetime.datetime(year=2021, month=3, day=1, hour=8, minute=0)
lng, lat = _return_center(dat=dataset)
offset = _calc_utc_offset(longitude=lng)
utc = _return_utc(offset=offset, local_dt=local_dt)

azi = get_azimuth(latitude_deg=lat, longitude_deg=lng, when=utc)
alt = get_altitude(latitude_deg=lat, longitude_deg=lng, when=utc)

azi = int(np.around(azi, decimals=0))
alt = int(np.around(alt, decimals=0))

print('azimuth is %s, alitude is' % azi, alt)

#---------------------------------------------------------------------
# Timeit
#---------------------------------------------------------------------

# DO NOT REPORT THIS... COMPILATION TIME IS INCLUDED IN THE EXECUTION TIME!
start = time.time()
go_fast(azi=azi, arr=arr, alt=alt, res=res)
end = time.time()
print("Elapsed (with compilation) = %s" % (end - start))

# NOW THE FUNCTION IS COMPILED, RE-TIME IT EXECUTING FROM CACHE
start = time.time()
img = go_fast(azi=azi, arr=arr, alt=alt, res=res)
end = time.time()
print("Elapsed (after compilation) = %s" % (end - start))

plt.imshow(img, cmap='binary')
plt.show()

