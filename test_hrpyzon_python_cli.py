
import os
import datetime
import logging

import rasterio
import numpy as np
import matplotlib.pyplot as plt
import pysolar

from hrpyzon_python import Horizon

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class Test():

    def __init__(self, data_dir, data_fn, local_dt):
        '''
        Parameters
        ==========
        data_dir : str

        data_fn : str

        local_dt : datetime.datetime
            e.g. datetime.datetime(year, month, day, hour, minute)
        '''
        self.dataset = rasterio.open(data_dir + '/' + data_fn)
        assert self.dataset.count == 1, ('Input must be single-band,' 
                                        'got %s bands.', self.dataset.count)
        self.array = self.dataset.read(1)
        self.lng, self.lat = self._return_center()
        self.local_dt = local_dt
        self.utc = self._return_utc(local_dt=local_dt)
        self.azimuth = pysolar.solar.get_azimuth(
                                    latitude_deg=self.lat,
                                    longitude_deg=self.lng,
                                    when=self.utc
                                    )
        self.altitude = pysolar.solar.get_altitude(
                                    latitude_deg=self.lat,
                                    longitude_deg=self.lng,
                                    when=self.utc
                                    )
        

    #--------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------
    
    def _return_center(self):
        '''

        '''
        dat = self.dataset
        corner_lng, corner_lat = dat.transform * (0,0)
        res = (dat.bounds.right - dat.bounds.left) / dat.shape[0]
        half = dat.shape[0] / 2
        offset_deg = res * half

        center_lng, center_lat = (
            corner_lng - offset_deg, corner_lat - offset_deg
        )

        return center_lng, center_lat

    def _calc_utc_offset(self):
        '''

        '''        
        longitude, _ = self._return_center()
        offset = np.abs(longitude) / 15
        offset = np.around(offset, decimals=0)
        if longitude < 0:
            return int(-offset)
        else:
            return int(offset)

    def _return_utc(self, local_dt):
        '''

        '''

        offset = self._calc_utc_offset()
        
        ldt = self.local_dt
        day, hour = ldt.day, ldt.hour
        hour = hour - offset

        if hour < 24:
            day = day
        elif hour >= 24:
            day = day+1
            hour = hour-24
        
        logger.warning('_return_utc needs update for edge mos/yrs')

        print(ldt.year, ldt.month, day, hour, ldt.minute)

        return datetime.datetime(ldt.year, ldt.month, day, hour, ldt.minute,
                                0, 0, tzinfo=datetime.timezone.utc)

    #--------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------
    
    def plot_array(self):
        '''

        '''
        fig,ax = plt.subplots(1, figsize=(5,5))
        ax.imshow(self.array, cmap='viridis')
        plt.show()

    def return_mask(self):
        hzn = Horizon(azimuth=self.azimuth, elev_grid=self.array)
        mask = hzn.calc_obstruction_for_altitude(
                        altitude=self.altitude, azimuth=self.azimuth
                        )
        return mask 

    def plot_mask(self):
        fig,ax = plt.subplots(1, figsize=(5,5))
        mask = self.return_mask()
        ax.imshow(mask, cmap='binary')
        plt.show()


#-------------------------------------------------------
# Test
#-------------------------------------------------------
subset_dir = 'data_subset'
subset_dat = os.listdir(subset_dir)


local_dt = datetime.datetime(year=2021, month=3, day=1, hour=8, minute=0)

test = Test(data_dir=subset_dir, data_fn=subset_dat[0], 
            local_dt=local_dt)

test.plot_mask()
