'''

'''
import os
import logging
import time

import rasterio
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
from numba import jit

from init_helpers import (
    _rotate2azimuth,
    _calc_horizon_indices,
    _calc_horizon_slope,
)

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.WARNING)

@jit(nopython=True)
def _calc_rotated_mask(alt, rot_slope):
    '''
    takes an elevation array, a 'slope to horizon (radians)' array,
    and a solar altitude as inputs, returns a (TILTED) array of visible points
    '''
    #assert alt 
    alt = np.deg2rad(90 - alt)
    shape = rot_slope.shape
    mask = np.zeros(shape)
    for k in range(0, shape[0]):
        for i in range(0, shape[0]):
            if rot_slope[i,k] > alt:
                mask[i,k] = 1
            elif rot_slope[i,k] < alt:
                mask[i,k] = 0
            else:
                mask[i,k] = -1
            
    return mask

@jit(nopython=False)
def _bbox(array):
    '''
    A helper for the _rerotate_mask method.
    '''
    rows = np.any(array, axis=1)
    cols = np.any(array, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    return rmin, rmax, cmin, cmax

@jit(nopython=False)
def _rerotate_mask(rot_elev, rot_mask, azi):   
    '''
    rotate mask back to original position, set non-1s to zeros
    '''
    
    #rotated_elevG, tiltedMask = self.invisiblePoints()
    #dimLength = self.resolution
    
    mask = ndimage.rotate(rot_mask, angle=azi, reshape=True, 
                            order=0, mode='constant', cval=np.nan)

    mask[np.isnan(mask)] = 0
    mask[mask == 0.5] = 0

    #create ref from the rotated elevation grid, set nans to zeros, extract extents from ref
    ref = ndimage.rotate(rot_elev, angle=azi, reshape=True, 
                            order=0, mode='constant', cval=np.nan)
    ref[np.isnan(ref)] = 0
    rmin, rmax, cmin, cmax = _bbox(array=ref)

    #clip extractMask using referenced extents, reset extractMask 0's to nan's
    mask = mask[rmin:rmax, rmin:cmax]
    mask[mask==0] = np.nan

    return mask

@jit(nopython=False)
def _square_mask(mask, resolution):
    '''

    '''
    target_shape = (resolution, resolution)

    if mask.shape == target_shape:
        mask = mask
    elif mask.shape != target_shape:
        row_diff = target_shape[0] - mask.shape[0]
        col_diff = target_shape[1] - mask.shape[1]
        row_stacker = np.zeros((mask.shape[0]))
        col_stacker = np.zeros((target_shape[1],1))

        if mask.shape[0] == mask.shape[1]:
            for i in range(1,row_diff+1):
                mask = np.append(mask, [row_stacker], axis=0)
            for i in range(1,col_diff+1):
                mask = np.append(mask, col_stacker, axis=1)
        else:
            mask = np.zeros(target_shape)
        
    mask[mask==0] = np.nan

    return mask



#---------------------------------------------------------------------
# Init w/ args
#---------------------------------------------------------------------
@jit(nopython=False)
def go_fast(azi, arr, alt):

    rotated_elevation_grid = _rotate2azimuth(azi, arr)

    # ( Extra args to avoid calling np.zeros w/in Numba )
    horz_arr = np.zeros(rotated_elevation_grid.shape, dtype=int)
    nhorz = horz_arr.shape[0]

    horizon_indices = _calc_horizon_indices(
        grid=rotated_elevation_grid, horz_arr=horz_arr, nhorz=nhorz
    )
    rotated_slope_array = (
        _calc_horizon_slope(rotated_elevation_grid, horz_arr=horizon_indices)
    )

    resolution = rotated_elevation_grid.shape[0]

    #---------------------------------------------------------------------
    # Run mask
    #---------------------------------------------------------------------
    rot_elev=rotated_elevation_grid 
    rot_slope=rotated_slope_array

    rotated_mask = _calc_rotated_mask(alt=alt, rot_slope=rot_slope)
    rerotated_mask = _rerotate_mask(
        rot_elev=rot_elev, rot_mask=rotated_mask, azi=azi
    )
    square_mask = _square_mask(mask=rerotated_mask, resolution=resolution)

    #---------------------------------------------------------------------
    # Do something with mask
    #---------------------------------------------------------------------
    return square_mask

#---------------------------------------------------------------------
# Arguments
#---------------------------------------------------------------------
data_dir = 'data_subset'
data_lst = os.listdir(data_dir)
data_fn = data_lst[0]
dataset = rasterio.open(data_dir + '/' + data_fn)

azi = 90
arr = dataset.read(1) #np.ones((100,100))
alt = 5

# DO NOT REPORT THIS... COMPILATION TIME IS INCLUDED IN THE EXECUTION TIME!
start = time.time()
go_fast(azi=azi, arr=arr, alt=alt)
end = time.time()
print("Elapsed (with compilation) = %s" % (end - start))

# NOW THE FUNCTION IS COMPILED, RE-TIME IT EXECUTING FROM CACHE
start = time.time()
img = go_fast(azi=azi, arr=arr, alt=alt)
end = time.time()
print("Elapsed (after compilation) = %s" % (end - start))

print(img)
plt.imshow(img)
plt.show()