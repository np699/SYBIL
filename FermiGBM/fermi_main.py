from fermi_skymap_functions import *
from parser import main_parser_args
import joblib

flux_area_model = joblib.load('flux_area_fit.pkl') # fit to GBM data
#FIXME temportary fix!!!
flux_area_residuals = np.load('residuals_no_outliers.npy')

def generate_skymaps():
    detected = []
    grb_filename = []
    kn_coords = []
    args = main_parser_args()
    filepath = args.LIGO_sim_dir
    savedir = args.save_dir
    if 'nsbh' in filepath:
        gw_type = 'nsbh'
    elif 'bns' in filepath:
        gw_type = 'bns'
    else:
        gw_type = '_'
    ids, ra, dec, dl = parse_gw_skymaps(filepath)

    for i in range(0, len(ids)):
        observed = grb_observed()
        if not observed:
            detected.append(False)
            grb_filename.append(None)
            kn_coords.append(None)
            continue
        radius = get_gbm_radius(dl[i], flux_area_model, flux_area_residuals)
        skymap_grb = get_GBM_from_GW(ra[i], dec[i], radius)
        save_filename = f'GBM_{gw_type}_{ids[i]}'
        save_skymap_arrays(skymap_grb, save_filename, savedir)
        detected.append(True)
        grb_filename.append(save_filename)
        kn_coords.append((ra[i], dec[i]))
        print(f"GRB {i} / {len(ids)} detected")

    record_results(ids, detected, grb_filename, kn_coords)


if __name__ == "__main__":
    generate_skymaps()

