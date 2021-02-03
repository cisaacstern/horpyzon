
import rasterio

import tcorrect_std.tc_funcs as tc
import tcorrect_std.rd_funcs as rd
from _open import _open


def attributes(elev_arr):
    '''
    
    '''



def broadcast():
    '''
    
    '''

if __name__ == '__main__':
    '''
    Run with, e.g.:
    $ python loop.py 'data_subset' 'subset.tif' '2021-06-21 06:00:00'
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