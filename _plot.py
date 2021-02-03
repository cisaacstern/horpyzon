import numpy as np
import matplotlib.pyplot as plt

def plot_sun(sunposition, d):
    '''

    '''
    fig = plt.figure(figsize=d['figsize'])

    tks = [np.deg2rad(a) for a in np.linspace(0,360,8,endpoint=False)]
    xlbls = np.array(['N','45','E','135','S','225','W','315'])

    ax = fig.add_subplot(111, projection='polar')
    ax.set_theta_zero_location('N')
    ax.set_xticks((tks))
    ax.set_xticklabels(xlbls, rotation="vertical", size=12)
    ax.tick_params(axis='x', pad=0.5)
    ax.set_theta_direction(-1)
    ax.set_rmin(0)
    ax.set_rmax(90)
    ax.set_rlabel_position(90)
    ax.set_title('Sun Position')

    xs = np.deg2rad(sunposition[0,:])
    ys = 90 - sunposition[1,:]

    ax.scatter(xs, ys, s=10, c='orange', alpha=0.5)
    
    plt.subplots_adjust(top=d['top'], bottom=d['bottom'], 
                        left=d['left'], right=d['right'])
    plt.close()
    return fig
