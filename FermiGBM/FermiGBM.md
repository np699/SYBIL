# Generating FERMI GBM skymaps corresponding to LIGO detections

This directory contains the work developing ([fermiskymap_testing.ipynb](./fermiskymap_testing.ipynb)) and code to generate skymaps for what FERMI GBM would observe given an NSBH or BNS merger detected in gravitational waves ([fermi_main.py](./fermi_main.py)).

## Overview

We start with simulated LIGO NSBH or BNS detections, and use the simulated ra, dec, and luminosity distance. 

We assume a top hat function for gamma-ray burst detectability. We set the probability of detection with the assumption that the jets must be within 15 degrees of the line of sight, although this probabilty can be modified in the script. We set a fixed luminosity at 2 × 10<sup>52</sup> ergs/s ([source](https://arxiv.org/pdf/2401.13636)).

Our default detection probability is 60 / 360, assuming two symmetrical jets, either of which can be within 15 degrees of the observer's line of site.

If the given event passes this probability draw, we generate a circular GBM skymap with a Gaussian probability distribution, use that distribution to select a location within this GBM skymap for the KN, and translate the GBM skymap so this KN location alligns with the location from the generated LIGO event. To get the radius of the skymap we (1) use the GW luminosity distance and fixed gamma-ray luminosity to get flux and (2) use a fit trend between localization radius and flux from real gbm data to draw a radius value.

When we simulate GRB detections for a given set of LIGO events, we save a csv file with columns: GW_filename, detected (true/false),GRB_filename,KN_coords. The last two columns are left blank for events that have detected: False. We save each simulated GBM skymap in the format GBM_{nsbh or bns}_{simulated gw id}.npz, which contains numpy arrays of the skymap ras, dec, and probabilities.

We started exploring Fermi GBM skymaps using the [Gamma-ray Data Tools](https://fermi.gsfc.nasa.gov/ssc/data/analysis/gbm/gbm_data_tools/gdt-docs/notebooks/Skymaps.html), but note that the final tool we develop shouldn't need to use this package.

## Scientific Assumptions

While GBM localizations can be elongated, we currently assume them all to be circular, which appears accurate generally.

We do not take into account GBM sky coverage, ie the "Earth shadow" which could block detection of an event.

We assume that the jet detectability follows a top hat function, and that jets must be within 15 degrees of the line of sight to be detected. This is a simplification, and future work could check how inaccurate it is for our use case (we consulted Dr. Eric Burns on this).

## Improvements: 

There are a handful of "FIXME" comments, not particularly comprehensive.
Add GBM sky coverage do detectability calculation (is 70%, so significant).
The assumption of a fixed luminosity with detection a binary dependent on angle could be made more complex. 
Remove all dependency on Fermi 'gdt' package - used when first developing, but not necessary for end product.

## Dependencies

- `numpy`
- `matplotlib`
- `astropy_healpix`
- `astropy`
- `gdt`

This code was tested with Python 3.12. The not so standard package, gdt (or the Gamma-ray Data Tools), is pip installable with:

```sh
pip install astro-gdt-fermi
gdt-data init
```

## Example Usage

```sh

python fermi_main.py --LIGO_sim_dir "../skymaps/nsbh1_injection.json" --save_dir "./simulations/nsbh/"
```