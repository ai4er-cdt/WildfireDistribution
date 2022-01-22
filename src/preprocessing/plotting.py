from datetime import datetime
from calendar import monthrange
import matplotlib as mpl
import matplotlib.pylab as plt
import xarray as xr
import numpy as np

import utils


#: Plot output path (TODO: should be read from some file)
plot_output_path = "/home/users/hrac2/WildfireDistribution/report/figures/"

def selected_months_JD(pp_modisJD, date, shape_root = None):
    """Saves a plot of the burn data corresponding to the chosen date.

        Args: 
            date: date in the format "YYYYMM" that is chosen for plotting
            shape_root: shape file (.shp) path of training area (optional)
    """

    # Initialise the subplot object
    plt.rcParams.update({'font.size': 13})
    fig, ax = plt.subplots(1, figsize=(9,7))
    
    # Want first colours in the map to be: -2 = dark grey, -1 = light grey, 0 = white
    cmaplist1 = plt.cm.gray(np.linspace(0, 1, 4))[1:]

    # case: non-binarized data
    if not pp_modisJD.binary_flag:
        
        # Find the first and last Julian Day present in the month requested 
        start_JD = datetime.strptime(date, pp_modisJD.date_format).timetuple().tm_yday
        end_JD = start_JD + monthrange(int(date[:4]), int(date[4:]))[1] -1
        range_JD = end_JD - start_JD

        # Then have a scale of yellow -> orange -> red for the Julian Day of burn days 
        cmaplist2 = plt.cm.YlOrRd(np.linspace(0, 1, range_JD))

        # case: January
        if start_JD == 1:
            cmap = mpl.colors.LinearSegmentedColormap.from_list('Custom cmap', np.vstack((cmaplist1, cmaplist2)), range_JD+2)
            bounds = np.linspace(-2.5, end_JD+0.5, range_JD+3)

        # case: February-December
        else:
            # Want 0-start_JD = black, to signify axis break 
            cmaplist1 = np.vstack((cmaplist1, np.array([0,0,0,1])))
            cmap = mpl.colors.LinearSegmentedColormap.from_list('Custom cmap', np.vstack((cmaplist1, cmaplist2)), range_JD+3)
            bounds = np.concatenate([np.linspace(-2.5, 0.5, 4), np.linspace(start_JD-0.5, end_JD+0.5, range_JD)])

        # Define the ticks for the colour bar
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
        ticks = np.concatenate([np.array([-2,-1,0]),np.arange(start_JD,end_JD+1)])
                            
        # Plot the data
        pp_modisJD.data.sel(date=date).plot(ax=ax, cmap=cmap, norm=norm, cbar_kwargs={'ticks': ticks,'label': 'Julian Day (1 -> 366)'});

    # case: binarized data (just plot burns in red)
    else: 
        bounds = np.linspace(-2.5, 1.5, 5)
        cmap = mpl.colors.LinearSegmentedColormap.from_list('Custom cmap', np.vstack((cmaplist1, np.array([1,0,0,1]))), 4)
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
        ticks = np.array([-2,-1,0,1])

        pp_modisJD.data.sel(date=date).plot(ax=ax, cmap=cmap, norm=norm, cbar_kwargs={'ticks': ticks,'label': 'Burn Classification'});

        
    # Add remaining components to the graph
    ax.set_title(date[4:] + '/' + date[:4], fontsize=20, fontweight="bold");
    ax.set_xlabel('Longitude (\N{DEGREE SIGN}W)',fontsize=16);
    ax.set_ylabel('Latitude (\N{DEGREE SIGN}N)',fontsize=16);

    # Optionally add a blue square to illustrate the training area
    if shape_root != None:
        training_coords = utils.extract_vertices(shape_root)
        ax.plot(training_coords[:,0],training_coords[:,1],'--b',linewidth=1);

    plt.savefig(plot_output_path+date+'_JD.png')


def selected_months_CL(pp_modisCL, date, shape_root = None):
    """Saves a plot of the confidence data corresponding to the chosen date.

    Args: 
        date: date in the format "YYYYMM" that is requested for plotting
        shape_root: shape file (.shp) path of training area (optional)
    """

    # Initialise the subplot object
    plt.rcParams.update({'font.size': 13})
    fig, ax = plt.subplots(1, figsize=(9,7))
    ticks = np.arange(0,101,10)
    
    # Prepare the colormap and force 0 -> black 
    cmap = plt.cm.plasma
    cmaplist = [cmap(i) for i in range(cmap.N)]
    cmaplist[0] = (0,0,0,1)
    cmap = mpl.colors.LinearSegmentedColormap.from_list('Custom cmap', cmaplist, cmap.N)
    
    # Plot the data
    pp_modisCL.data.plot(ax=ax, cmap=cmap, vmin=0, vmax=100, cbar_kwargs={'ticks': ticks,'label': 'Confidence (%)'});
    ax.set_title(date[4:] + '/' + date[:4], fontsize=20, fontweight="bold");
    ax.set_xlabel('Longitude (\N{DEGREE SIGN}W)',fontsize=16);
    ax.set_ylabel('Latitude (\N{DEGREE SIGN}N)',fontsize=16);

    # Optionally add a white square to illustrate the training area
    if shape_root != None:
        training_coords = utils.extract_vertices(shape_root)
        ax.plot(training_coords[:,0],training_coords[:,1],'--w',linewidth=1.5);

    plt.savefig(plot_output_path+date+'_CL.png')


def monthly_histogram(monthly_quantities):
    """Saves a plot of the means/standard deviations of the quantities stored in 'monthly_quantities', for each month.

    Args:
        monthly_quantities:  date ('YYYYMM'): quantity of interest
    """

    # Calculate means and standard deviations
    monthly_means, _ = utils.calc_means(monthly_quantities)
    monthly_std_devs = utils.calc_std_devs(monthly_quantities)
    
    # Plot the means as a histogram and standard deviations as error bars 
    plt.rcParams.update({'font.size': 13})
    fig, ax = plt.subplots(figsize=(12,7))
    ax.bar(monthly_means.keys(), monthly_means.values(), yerr=monthly_std_devs.values(), align='center', color = 'orange', alpha=0.7, ecolor='black', capsize=10)
    ax.set_title('Means and Standard Deviations of Burn Proportion', fontsize=20, fontweight="bold");
    ax.set_ylabel('Mean Burn Proportion',fontsize=16)
    ax.set_xlabel('Month',fontsize=16)
    ax.yaxis.grid(True)
    plt.savefig(plot_output_path+'burn_proportion_hist.png')



