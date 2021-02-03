import numpy as np
import richdem as rd

def np2rdarray(in_array, res, no_data=-9999):
    '''
    slope and aspect calculations are performed by richdem, which
    requires data in rdarray format. this function converts numpy
    arrays into rdarrays.
    '''
    out_array = rd.rdarray(in_array, no_data=no_data)
    out_array.projection = c.PROJECTION
    cell_scale = np.around(a=c.SIDE_LEN/res, decimals=5)
    out_array.geotransform = [0, cell_scale, 0, 0, 0, cell_scale]
    return out_array

def calc_attributes(grid):
    '''
    given input grid, returns slope and aspect grids
    '''
    rda = np2rdarray(np.asarray(grid), -9999)

    slope_outfile = TemporaryFile()
    np.save(slope_outfile, rd.TerrainAttribute(rda, attrib='slope_radians'))
    _ = slope_outfile.seek(0)
    slope_grid = np.load(slope_outfile)
    slope_outfile.close()

    aspect_outfile = TemporaryFile()
    np.save(aspect_outfile, rd.TerrainAttribute(rda, attrib='aspect'))
    _ = aspect_outfile.seek(0)
    aspect_grid = np.load(aspect_outfile)
    aspect_grid[aspect_grid>180] = aspect_grid[aspect_grid>180]-360
    aspect_outfile.close()

    return slope_grid, aspect_grid