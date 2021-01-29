# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#Load-dataset" data-toc-modified-id="Load-dataset-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Load dataset</a></span><ul class="toc-item"><li><span><a href="#Open-and-explore" data-toc-modified-id="Open-and-explore-1.1"><span class="toc-item-num">1.1&nbsp;&nbsp;</span>Open and explore</a></span></li><li><span><a href="#Plot" data-toc-modified-id="Plot-1.2"><span class="toc-item-num">1.2&nbsp;&nbsp;</span>Plot</a></span></li></ul></li><li><span><a href="#Solar-azimuth" data-toc-modified-id="Solar-azimuth-2"><span class="toc-item-num">2&nbsp;&nbsp;</span>Solar azimuth</a></span><ul class="toc-item"><li><span><a href="#Find-lat/long-of-center" data-toc-modified-id="Find-lat/long-of-center-2.1"><span class="toc-item-num">2.1&nbsp;&nbsp;</span>Find lat/long of center</a></span></li><li><span><a href="#Choose-a-datetime" data-toc-modified-id="Choose-a-datetime-2.2"><span class="toc-item-num">2.2&nbsp;&nbsp;</span>Choose a <code>datetime</code></a></span></li><li><span><a href="#Find-solar-azimuth" data-toc-modified-id="Find-solar-azimuth-2.3"><span class="toc-item-num">2.3&nbsp;&nbsp;</span>Find solar azimuth</a></span></li></ul></li><li><span><a href="#Test-Horizon" data-toc-modified-id="Test-Horizon-3"><span class="toc-item-num">3&nbsp;&nbsp;</span>Test <code>Horizon</code></a></span><ul class="toc-item"><li><span><a href="#Run-an-obstruction" data-toc-modified-id="Run-an-obstruction-3.1"><span class="toc-item-num">3.1&nbsp;&nbsp;</span>Run an obstruction</a></span></li></ul></li></ul></div>

# +
import os
import datetime

import rasterio
import matplotlib.pyplot as plt
import pysolar

from hrpyzon_python import Horizon
# -

# # Load dataset

# ## Open and explore

subset_dir = 'data_subset'
subset_dat = os.listdir(subset_dir)
subset_dat

dataset = rasterio.open(subset_dir + '/' + subset_dat[0])

dataset.bounds

dataset.meta

# ## Plot

subset = dataset.read(1)

fig,ax = plt.subplots(1, figsize=(5,5))
ax.imshow(subset)
plt.show()

# # Solar azimuth

# ## Find lat/long of center

corner_lng, corner_lat = dataset.transform * (0,0)
#corner_lng, corner_lat

res = (dataset.bounds.right - dataset.bounds.left) / dataset.shape[0]
#res

half = dataset.shape[0] / 2
#half

offset_deg = res * half
#offset_deg

center_lng, center_lat = (
    corner_lng - offset_deg, corner_lat - offset_deg
)
#center_lng, center_lat

# ## Choose a `datetime`

# +
# when is sunrise on a given day? does pysolar know?
# -

year = 2021
month = 3
day = 1
hour = 8
minute = 0

UTC_OFFSET = 8

# +
hour = hour + UTC_OFFSET

if hour < 24:
    day = day
elif hour >= 24:
    day = day+1
    hour = hour-24
# -

utc_dt = datetime.datetime(year, month, day, hour, minute, 
                           0, 0, tzinfo=datetime.timezone.utc)
utc_dt


# ## Find solar azimuth

azimuth = pysolar.solar.get_azimuth(
    latitude_deg=center_lat,
    longitude_deg=center_lng,
    when=utc_dt
)
azimuth

# # Test `Horizon`

hzn = Horizon(azimuth=azimuth, elev_grid=subset)

# ## Run an obstruction

help(hzn.calc_obstruction_for_altitude)

# ^ get a better doctring in there! for the help method!

altitude = pysolar.solar.get_altitude(
    latitude_deg=center_lat,
    longitude_deg=center_lng,
    when=utc_dt
)
altitude

mask = hzn.calc_obstruction_for_altitude(altitude=altitude, azimuth=azimuth)

fig,ax = plt.subplots(1, figsize=(5,5))
ax.imshow(mask, cmap='binary')
plt.show()


