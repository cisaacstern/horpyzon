import numpy as np

def calc_correction(grids, sunpos):
        '''
        The argument `grids` should be a tuple of `length = 2` for which
        `grids[0]` is an array of slope values in radians, and grids[1]
        is an array of aspect values in degrees, with south = 0, and east positive.
        '''
        slope, aspect = grids
        azi, alt = sunpos

        T0 = np.deg2rad(alt)
        P0 = np.deg2rad(180 - azi)

        S = np.deg2rad(slope) 
        A = np.deg2rad(aspect)

        cosT0 = np.cos(T0)
        cosS = np.cos(S)
        sinT0 = np.sin(T0)
        sinS = np.sin(S)
        cosP0A = np.cos(P0 - A)

        cosT = (cosT0*cosS) + (sinT0*sinS*cosP0A)

        return cosT/cosT0