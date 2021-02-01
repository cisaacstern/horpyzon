# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"></ul></div>

'''

'''
import logging
import time

import numpy as np
from scipy import ndimage

from numba import int64, float64
from numba.experimental import jitclass

from init_helpers import (
    _rotate2azimuth,
    _slope,
    _calc_horizon_indices,
    _calc_horizon_slope,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
'''
spec = [
    ('azimuth', float64),
    ('elev_grid', float64[:,:]),
    ('rotated_grid', float64[:,:]),
    ('rotated_elevation_grid', float64[:,:]),
    ('rotated_slope_array', float64[:,:]),
    ('resolution', int64),
]

@jitclass(spec)
'''
class Horizon():
    '''
    This class initializes horizons in the "ill posed manner" described in Dozier.
    Once initialized, it provides instance methods for calculating shade at selected timepoints.
    In reality, each sun position has a unique azimuth. For the purposes of this model, however,
    we bin azimuth into a discrete number of user-defined buckets. This explains why we
    initalize this class based on the azimuth: because azimuths are reused for multiple timepoints
    i.e. altitudes. Azimuths are also the most computationally expensive.
    '''
    def __init__(self, azimuth, elev_grid):
        '''

        ''' 

        self.azimuth = azimuth

        rotated_grid = _rotate2azimuth(azimuth, elev_grid)
        horizon_indices = _calc_horizon_indices(grid=rotated_grid)
        rotated_slope_array = (
            _calc_horizon_slope(rotated_grid, horz_arr=horizon_indices)
        )

        self.rotated_elevation_grid = rotated_grid
        self.rotated_slope_array = rotated_slope_array

        #self.rotated_elevation_grid, self.rotated_slope_array = (
        #    _initialize_azimuth(azimuth=azimuth, elev_grid=elev_grid)
        #)
        self.resolution = elev_grid.shape[0]

    #---------------------------------------------------------------------
    # Private API
    #---------------------------------------------------------------------
      

    #---------------------------------------------------------------------
    # Public API
    #---------------------------------------------------------------------

    def calc_obstruction_for_altitude(self, altitude, azimuth):
        '''

        '''
        rot_elev=self.rotated_elevation_grid 
        rot_slope=self.rotated_slope_array
        resolution=self.resolution
        
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
    
        def _bbox(array):
            '''
            A helper for the _rerotate_mask method.
            '''
            rows = np.any(array, axis=1)
            cols = np.any(array, axis=0)
            rmin, rmax = np.where(rows)[0][[0, -1]]
            cmin, cmax = np.where(cols)[0][[0, -1]]

            return rmin, rmax, cmin, cmax

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
        
        rotated_mask = _calc_rotated_mask(alt=altitude, rot_slope=rot_slope)
        rerotated_mask = _rerotate_mask(
            rot_elev=rot_elev, rot_mask=rotated_mask, azi=azimuth
        )
        square_mask = _square_mask(mask=rerotated_mask, resolution=resolution)

        return square_mask

#---------------------------------------------------------------------
# Test area
#---------------------------------------------------------------------
azimuth = 90
test_arr = np.ones((100,100))
print('azimuth is of type %s' % type(azimuth))
print('array is of type %s' % type(test_arr))
print('array content is of type %s' % type(test_arr[1,1]))

start = time.time()
hzn = Horizon(azimuth=azimuth, elev_grid=test_arr)
end = time.time()

print('Elapsed = %s' % (end - start))