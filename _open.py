import rasterio

def _open(data_dir, data_fn):
    '''
    
    '''
    dataset = rasterio.open(data_dir + '/' + data_fn)
    arr = dataset.read(1)
    assert arr.shape[0] == arr.shape[1], 'Input array must be square.'
    res = arr.shape[0]
    outfile = data_fn.replace('.tif', '.npz')

    return dataset, arr, res, outfile