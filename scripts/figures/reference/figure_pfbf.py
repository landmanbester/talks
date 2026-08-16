import sys
import numpy as np
import matplotlib as mpl
mpl.rcParams.update({ 'font.size': 9, 'font.family': 'serif'})
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.visualization import LogStretch, LinearStretch, ImageNormalize
from astropy.coordinates import SkyCoord
import astropy.units as u
from pyrap.tables import table
import matplotlib.ticker as ticker
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.axes_grid1 import make_axes_locatable


field = table("/home/bester/projects/ESO137/msdir/ms1_target.ms::FIELD")
ra, dec = field.getcol('PHASE_DIR')[0][0]
ra_center = np.rad2deg(ra)
dec_center = np.rad2deg(dec)


# List of FITS files
pfb_model = '/home/bester/projects/ESO137/output_old/fits/hi/hi_combined_bda_I_main_model_time0000_mfs.fits'
pfb_image = '/home/bester/projects/ESO137/output_old/fits/hi/hi_combined_bda_I_main_image_mfs.fits'
pfb_residual = '/home/bester/projects/ESO137/output_old/fits/hi/hi_combined_bda_I_main_residual_time0000_mfs.fits'
pfb_update = '/home/bester/projects/ESO137/output_old/fits/hi/hi_combined_bda_I_main_update_time0000_mfs.fits'

colmap = 'inferno'

# get wcs and data
with fits.open(pfb_model) as hdul:
    wcs = WCS(hdul[0].header)
    data = hdul[0].data.squeeze()
    wcs = wcs.dropaxis(2)
    wcs = wcs.dropaxis(2)

# shift to region of interest
nx, ny = data.shape
shift_ra = 0.3
shift_dec = -0.1
# shift_ra = 0.0
# shift_dec = 0.
width = 0.7
height = 0.7

center = SkyCoord(ra_center - shift_ra, dec_center - shift_dec, unit='deg')
x_center, y_center  = wcs.world_to_pixel(center)
x_width = width / wcs.pixel_scale_matrix[0, 0]
y_height = height / wcs.pixel_scale_matrix[1, 1]
x_max = int(x_center - x_width / 2)
x_min = int(x_center + x_width / 2)
y_min = int(y_center - y_height / 2)
y_max = int(y_center + y_height / 2)
x_min, x_max = max(0, x_min), min(nx, x_max)
y_min, y_max = max(0, y_min), min(ny, y_max)


data = data[y_min:y_max, x_min:x_max]
wcs = wcs[y_min:y_max, x_min:x_max]

# Create a 1x2 grid of subplots
fig = plt.figure(figsize=(24, 24))
ax = fig.add_subplot(2, 2, 1, projection=wcs)

# import ipdb; ipdb.set_trace()
vmax = np.percentile(data, 99.9)
vmin = data.min()
norm = ImageNormalize(data, vmin=data.min(), vmax=vmax, stretch=LogStretch())
im = ax.imshow(data, cmap=colmap, norm=norm, origin='lower')

ax.coords.grid(color='white', alpha=0.25, linestyle='solid')
# ax.coords['ra'].set_axislabel('Right Ascension')
ax.coords['dec'].set_axislabel('Declination', fontsize=12)
ax.coords['ra'].set_ticks_visible(False)
ax.coords['ra'].set_ticklabel_visible(False)
ax.set_aspect('equal')


# get wcs and data
with fits.open(pfb_image) as hdul:
    wcs = WCS(hdul[0].header)
    wcs.wcs.crval[0] += 360
    data = hdul[0].data.squeeze()
    wcs = wcs.dropaxis(2)
    wcs = wcs.dropaxis(2)

data = data[y_min:y_max, x_min:x_max]
wcs = wcs[y_min:y_max, x_min:x_max]

axw = fig.add_subplot(2, 2, 2, projection=wcs, sharey=ax)

vmax = np.percentile(data[data>0], 98)
vmin = -np.percentile(np.abs(data[data<0]), 98)
norm = ImageNormalize(data, vmin=vmin, vmax=vmax, stretch=LogStretch())
im = axw.imshow(data, cmap=colmap, norm=norm, origin='lower')

axw.coords.grid(color='white', alpha=0.25, linestyle='solid')
# axw.coords['ra'].set_axislabel('Right Ascension')
axw.coords['ra'].set_ticks_visible(False)
axw.coords['ra'].set_ticklabel_visible(False)
axw.coords['dec'].set_ticks_visible(False)
axw.coords['dec'].set_ticklabel_visible(False)
axw.set_aspect('equal')


with fits.open(pfb_residual) as hdul:
    wcs = WCS(hdul[0].header)
    data = hdul[0].data.squeeze()
    wcs = wcs.dropaxis(2)
    wcs = wcs.dropaxis(2)

data = data[y_min:y_max, x_min:x_max]
wcs = wcs[y_min:y_max, x_min:x_max]
ax = fig.add_subplot(2, 2, 3, projection=wcs)

vmax = np.percentile(data[data>0], 99)
vmin = -np.percentile(np.abs(data[data<0]), 99)
norm = ImageNormalize(data, vmin=vmin, vmax=vmax, stretch=LinearStretch())
im = ax.imshow(data, cmap=colmap, norm=norm, origin='lower')

ax.coords.grid(color='black', alpha=0.25, linestyle='solid')
ax.coords['ra'].set_axislabel('Right Ascension', fontsize=12)
# ax.coords['ra'].set_ticks_visible(False)
ax.coords['dec'].set_axislabel('Declination', fontsize=12)
# ax.coords['dec'].set_ticks_visible(False)
ax.set_aspect('equal')

# get wcs and data
with fits.open(pfb_update) as hdul:
    wcs = WCS(hdul[0].header)
    data = hdul[0].data.squeeze()
    wcs = wcs.dropaxis(2)
    wcs = wcs.dropaxis(2)

data = data[y_min:y_max, x_min:x_max]
wcs = wcs[y_min:y_max, x_min:x_max]

axw = fig.add_subplot(2, 2, 4, projection=wcs) #, sharey=ax)

vmax = np.percentile(data[data>0], 99)
vmin = -np.percentile(np.abs(data[data<0]), 99)
norm = ImageNormalize(data, vmin=vmin, vmax=vmax, stretch=LinearStretch())
im = axw.imshow(data, cmap=colmap, norm=norm, origin='lower')

axw.coords.grid(color='black', alpha=0.25, linestyle='solid')
axw.coords['ra'].set_axislabel('Right Ascension', fontsize=12)
# axw.coords['ra'].set_ticks_visible(False)
axw.coords['dec'].set_ticks_visible(False)
axw.coords['dec'].set_ticklabel_visible(False)
axw.set_aspect('equal')

# Adjust the layout
# plt.tight_layout()
fig.subplots_adjust(hspace=0.01, wspace=0.0)

# Save the figure
plt.savefig('/home/bester/projects/ESO137/rise-paper-3/figures/pfbf.jpeg',
            dpi=350,
            bbox_inches='tight')
plt.close()
