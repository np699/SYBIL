import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import scipy.stats as stats
import json
import random
from gdt.missions.fermi.gbm.localization import GbmHealPix
from gdt.core.plot.sky import EquatorialPlot
from datetime import datetime

    
def grb_observed(prob_obs = 60 / 360):
    obs_bool = np.random.choice([True, False], p=[prob_obs, 1 - prob_obs])
    if not obs_bool:    
        return False
    else:
        return True
    
def parse_gw_skymaps(filename):
    with open(filename) as f:
        data = json.load(f)
    contents = data['injections']['content']
    simulation_ids = contents['simulation_id']
    ra = contents['ra']
    dec = contents['dec']
    dl = contents['luminosity_distance']
    return simulation_ids, ra, dec, dl

def draw_localization_radius(flux, model, residuals):
    """
    Given a flux value, draw a localization area from a Gamma distribution.
    Parameters:
    flux (float): The flux value.
    Returns:
    float: A localization 90% area.
    """
    log_flux = np.log(flux).reshape(-1, 1)
    mean_log_area = model.predict(log_flux)
    shape, loc, scale = stats.gamma.fit(residuals)
    gamma_sample = stats.gamma.rvs(shape, loc=loc, scale=scale)
    log_area = mean_log_area + gamma_sample
    area = np.exp(log_area)
    radius = (area[0] / (np.pi))**0.5
    return radius

def get_gbm_radius(dl, model, residuals):
    """
    Given a luminosity distance, calculate the localization radius for a GBM skymap
    """
    L = 2*10**52 # erg s-1
    flux = L / (4 * np.pi * dl**2)
    radius = draw_localization_radius(flux, model, residuals)
    return radius

def get_GBM_from_GW(kn_ra, kn_dec, radius):
    #make GRB skymap template
    gauss_map = GbmHealPix.from_gaussian(100, 0, radius)
    # select kn location in grb skymap taking into account pixel probability
    approx_res = np.sqrt(gauss_map.pixel_area)
    numpts_ra = int(np.floor(0.5*360.0/approx_res))
    numpts_dec= int(np.floor(0.5*180.0/approx_res))
    #probs has dimentions of 98 x 196, ra had 196 elements, dec has 98 elements
    probs, ra, dec = gauss_map.prob_array(numpts_ra = numpts_ra, numpts_dec = numpts_dec)
    flattened_ra = np.tile(ra, len(dec))
    flattened_dec = np.repeat(dec, len(ra))
    coords = zip(flattened_ra, flattened_dec)
    flattened_probs = np.concatenate(probs).ravel()
    select_index = np.arange(0, len(flattened_probs))
    select_pixel_grb = random.choices(select_index, weights=flattened_probs, k=1)[0]
    #translate the GRB skymap so selected pixel lines up with GW kn location
    ra_shift = kn_ra - flattened_ra[select_pixel_grb]
    dec_shift = kn_dec - flattened_dec[select_pixel_grb]
    skymap_grb = GbmHealPix.from_gaussian(ra_shift + 100, dec_shift + 0, radius)
    return skymap_grb

def save_skymap(skymap, filename):
    """
    function to save skymap as fits file
    """
    #need to fix this function
    skymap.write(f'simulations/{filename}.fits', overwrite=True)  

def save_skymap_arrays(skymap, filename, save_dir):
    """
    to save skymap as numpy arrays
    """
    approx_res = np.sqrt(skymap.pixel_area)
    numpts_ra = int(np.floor(0.5*360.0/approx_res))
    numpts_dec= int(np.floor(0.5*180.0/approx_res))
    probs, ra, dec = skymap.prob_array(numpts_ra = numpts_ra, numpts_dec = numpts_dec)
    flattened_ra = np.tile(ra, len(dec))
    flattened_dec = np.repeat(dec, len(ra))
    flattened_probs = np.concatenate(probs).ravel()
    np.savez(f'{save_dir}{filename}.npz', ra=flattened_ra, dec=flattened_dec, probs=flattened_probs)

def record_results(gw_filenames, detected, grb_filename, kn_coords):
    """
    Function to record results of simulation run
    """
    df = pd.DataFrame({
        'GW_filename': gw_filenames,
        'detected': detected,
        'GRB_filename': grb_filename,
        'KN_coords': kn_coords
    })
    time = datetime.now()
    df.to_csv(f'simulations/results_{time}.csv', index=False)

def open_gbm_skymap(filename):
    """
    Function to load skymap arrays from a .npz file
    """
    data = np.load(f'{filename}.npz')
    ra = data['ra']
    dec = data['dec']
    probs = data['probs']
    return ra, dec, probs

def equatorial_plot(map):
    skyplot = EquatorialPlot()
    skyplot.add_localization(map, detectors=[])
    plt.show()