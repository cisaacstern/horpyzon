# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#Retrieve-data" data-toc-modified-id="Retrieve-data-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Retrieve data</a></span></li><li><span><a href="#Open-w/-rasterio" data-toc-modified-id="Open-w/-rasterio-2"><span class="toc-item-num">2&nbsp;&nbsp;</span>Open w/ <code>rasterio</code></a></span></li><li><span><a href="#Read-to-numpy.ndarray" data-toc-modified-id="Read-to-numpy.ndarray-3"><span class="toc-item-num">3&nbsp;&nbsp;</span>Read to <code>numpy.ndarray</code></a></span></li><li><span><a href="#Find-an-interesting-subset" data-toc-modified-id="Find-an-interesting-subset-4"><span class="toc-item-num">4&nbsp;&nbsp;</span>Find an interesting subset</a></span></li><li><span><a href="#Define-a-subset-transform" data-toc-modified-id="Define-a-subset-transform-5"><span class="toc-item-num">5&nbsp;&nbsp;</span>Define a subset transform</a></span></li><li><span><a href="#Write-subset-to-file" data-toc-modified-id="Write-subset-to-file-6"><span class="toc-item-num">6&nbsp;&nbsp;</span>Write subset to file</a></span></li></ul></div>

# +
import os

import rasterio
from rasterio.transform import Affine

import matplotlib.pyplot as plt
import matplotlib.patches as patches
# -

# # Retrieve data
#
# Explore data here: https://prd-tnm.s3.amazonaws.com/LidarExplorer/index.html#/
#
# The data used herein is a 1 arc-second DEM, downloaded from: https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/n38w119/USGS_1_n38w119.tif
#
# > Note that the `rasterio` usage employed throughout this document is referenced from https://rasterio.readthedocs.io/en/latest/quickstart.html#id2

raw_dir = 'data_raw'
raw_dat = os.listdir(raw_dir)
raw_dat

# # Open w/ `rasterio`

dataset = rasterio.open(raw_dir + '/' + raw_dat[0])

dataset.bounds

dataset.meta

# # Read to `numpy.ndarray`

Z = dataset.read(1)

type(Z)

Z.shape

# # Find an interesting subset 

# +
fig,ax = plt.subplots(1, 2, figsize=(10,5))

ncols = 1650 # anchor on x-axis
nrows = 3075 # anchor on y-axis
extent = 300 # linear extent

ax[0].imshow(Z)
rect = patches.Rectangle((ncols, nrows), extent, extent,
                         linewidth=1,edgecolor='r',facecolor='none')
ax[0].add_patch(rect)

subset = Z[nrows:nrows+extent, ncols:ncols+extent]
ax[1].imshow(subset)
plt.show
# -

# # Define a subset transform

x0_o, y0_o = dataset.transform * (0, 0)
res = (dataset.bounds.right - dataset.bounds.left) / dataset.shape[0]
print(f'''The upper left corner of the original dataset is
{x0_o, y0_o}
and each cell in the raster spans {res} degrees.''')

print(f'''The upper left corner of the subset is
({nrows} rows * {res}) = {nrows*res} degrees inset from the top, and
({ncols} columns * {res}) = {ncols*res} degrees inset from the left.''')

x0_s = x0_o - (ncols*res)
y0_s = y0_o - (nrows*res)
print(f'''The upper left corner of the subset is
{x0_s, y0_s}''')

# +
transform = Affine.translation(x0_s, y0_s) * Affine.scale(res, res)

transform
# -

transform * (0,0)

#  # Write subset to file

with rasterio.open(
    'data_subset/subset.tif',
    'w',
    driver='GTiff',
    height=inset.shape[0],
    width=inset.shape[1],
    count=1,
    dtype=inset.dtype,
    crs=dataset.meta['crs'],
    transform=transform,
) as dst:
    dst.write(subset, 1)

dataset.close()


