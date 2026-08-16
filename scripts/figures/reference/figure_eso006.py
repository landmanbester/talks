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
pfb_model = '/home/bester/projects/ESO137/output_old/fits/stage9/stage9_combined_bda_I_robm03_model_time0000_mfs.fits'
pfb_image = '/home/bester/projects/ESO137/output_old/fits/stage9/stage9_combined_bda_I_robm03_image_mfs.fits'
wsc_model = '/home/bester/projects/ESO137/output_old/wsclean/run4-MFS-model.fits'
wsc_image = '/home/bester/projects/ESO137/output_old/wsclean/run4-MFS-image.fits'

colmap = 'inferno'

# get wcs and data
with fits.open(pfb_model) as hdul:
    wcs = WCS(hdul[0].header)
    data = hdul[0].data.squeeze()
    wcs = wcs.dropaxis(2)
    wcs = wcs.dropaxis(2)

# with fits.open(wsc_model) as hdul:
#     wcs = WCS(hdul[0].header)
#     wcs.wcs.crval[0] += 360
#     data = hdul[0].data.squeeze()
#     wcs = wcsw.dropaxis(2)
#     wcs = wcsw.dropaxis(2)


# import ipdb; ipdb.set_trace()
# shift to region of interest
nx, ny = data.shape
# shift_ra = 0.3
# shift_dec = -0.1
shift_ra = 0.0
shift_dec = 0.05
width = 0.315
height = 0.21

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
fig = plt.figure(figsize=(24, 16))
ax = fig.add_subplot(2, 2, 1, projection=wcs)

# import ipdb; ipdb.set_trace()
vmax = np.percentile(data, 99)
vmin = data.min()
vmin = -0.005*vmax
norm = ImageNormalize(data, vmin=vmin, vmax=vmax, stretch=LogStretch())
im = ax.imshow(data, cmap=colmap, norm=norm, origin='lower')

# how to make the colorbar narrower?
# cax = inset_axes(ax,
#                  width="3%",  # width = 3% of parent_bbox width
#                  height="100%",  # height : 100%
#                  loc='lower right',
#                  bbox_to_anchor=(0., 0., 1.1, 1),
#                  bbox_transform=ax.transAxes,
#                  borderpad=0)
# divider = make_axes_locatable(ax)
# cax = divider.append_axes("right", size="5%", pad=0.05)

# cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
# cbar.set_label('Jy/pixel', rotation=270, labelpad=15, fontsize=6)
# cbar.ax.tick_params(labelsize=4)

# formatter = ticker.ScalarFormatter(useMathText=True)
# formatter.set_scientific(True)
# formatter.set_powerlimits((0, 0))
# cbar.formatter = formatter
# cbar.update_ticks()

ax.coords.grid(color='white', alpha=0.25, linestyle='solid')
# ax.coords['ra'].set_axislabel('Right Ascension')
ax.coords['dec'].set_axislabel('Declination', fontsize=12)
ax.coords['ra'].set_ticks_visible(False)
ax.coords['ra'].set_ticklabel_visible(False)
ax.set_aspect('equal')


# get wcs and data
with fits.open(wsc_model) as hdul:
    wcs = WCS(hdul[0].header)
    wcs.wcs.crval[0] += 360
    data = hdul[0].data.squeeze()
    wcs = wcs.dropaxis(2)
    wcs = wcs.dropaxis(2)

data = data[y_min:y_max, x_min:x_max]
wcs = wcs[y_min:y_max, x_min:x_max]
print(data.min())
axw = fig.add_subplot(2, 2, 2, projection=wcs, sharey=ax)

# import ipdb; ipdb.set_trace()
# vmax = np.percentile(data, 99.9)
norm = ImageNormalize(data, vmin=vmin, vmax=vmax, stretch=LogStretch())
im = axw.imshow(data, cmap=colmap, norm=norm, origin='lower')

# how to make the colorbar narrower?
# cax = inset_axes(ax,
#                  width="3%",  # width = 3% of parent_bbox width
#                  height="100%",  # height : 100%
#                  loc='lower right',
#                  bbox_to_anchor=(0., 0., 1.1, 1),
#                  bbox_transform=ax.transAxes,
#                  borderpad=0)
# divider = make_axes_locatable(axw)
# cax = divider.append_axes("right", size="5%", pad=0.05)

# cbar = fig.colorbar(im, ax=cax, fraction=0.046, pad=0.04)
# # cbar.set_label('Jy/pixel', rotation=270, labelpad=15, fontsize=6)
# cbar.ax.tick_params(labelsize=4)

# formatter = ticker.ScalarFormatter(useMathText=True)
# formatter.set_scientific(True)
# formatter.set_powerlimits((0, 0))
# cbar.formatter = formatter
# cbar.update_ticks()

axw.coords.grid(color='white', alpha=0.25, linestyle='solid')
# axw.coords['ra'].set_axislabel('Right Ascension')
axw.coords['ra'].set_ticks_visible(False)
axw.coords['ra'].set_ticklabel_visible(False)
axw.coords['dec'].set_ticks_visible(False)
axw.coords['dec'].set_ticklabel_visible(False)
axw.set_aspect('equal')


with fits.open(pfb_image) as hdul:
    wcs = WCS(hdul[0].header)
    data = hdul[0].data.squeeze()
    wcs = wcs.dropaxis(2)
    wcs = wcs.dropaxis(2)

data = data[y_min:y_max, x_min:x_max]
wcs = wcs[y_min:y_max, x_min:x_max]
ax = fig.add_subplot(2, 2, 3, projection=wcs)

vmax = np.percentile(data[data>0], 98)
vmin = -np.percentile(np.abs(data[data<0]), 98)
norm = ImageNormalize(data, vmin=vmin, vmax=vmax, stretch=LogStretch())
im = ax.imshow(data, cmap=colmap, norm=norm, origin='lower')

# cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
# cbar.set_label('Intensity', rotation=270, labelpad=15)
# cbar.ax.tick_params(labelsize=4)

# formatter = ticker.ScalarFormatter(useMathText=True)
# formatter.set_scientific(True)
# formatter.set_powerlimits((0, 0))  # Set to scientific notation if exponent is not between -3 and 3
# cbar.formatter = formatter
# cbar.update_ticks()

ax.coords.grid(color='black', alpha=0.25, linestyle='solid')
ax.coords['ra'].set_axislabel('Right Ascension', fontsize=12)
# ax.coords['ra'].set_ticks_visible(False)
ax.coords['dec'].set_axislabel('Declination', fontsize=12)
# ax.coords['dec'].set_ticks_visible(False)
ax.set_aspect('equal')

# get wcs and data
with fits.open(wsc_image) as hdul:
    wcs = WCS(hdul[0].header)
    data = hdul[0].data.squeeze()
    wcs = wcs.dropaxis(2)
    wcs = wcs.dropaxis(2)

data = data[y_min:y_max, x_min:x_max]
wcs = wcs[y_min:y_max, x_min:x_max]

axw = fig.add_subplot(2, 2, 4, projection=wcs) #, sharey=ax)

# vmax = np.percentile(data[data>0], 99.9)
# vmin = -np.percentile(np.abs(data[data<0]), 99.9)
norm = ImageNormalize(data, vmin=vmin, vmax=vmax, stretch=LogStretch())
im = axw.imshow(data, cmap=colmap, norm=norm, origin='lower')

# how to make the colorbar narrower?
# cax = inset_axes(ax,
#                  width="3%",  # width = 3% of parent_bbox width
#                  height="100%",  # height : 100%
#                  loc='lower right',
#                  bbox_to_anchor=(0., 0., 1.1, 1),
#                  bbox_transform=ax.transAxes,
#                  borderpad=0)
# divider = make_axes_locatable(ax)
# cax = divider.append_axes("right", size="5%", pad=0.05)

# cbar = fig.colorbar(im, ax=axw, fraction=0.046, pad=0.04)
# cbar.set_label('Jy/pixel', rotation=270, labelpad=15, fontsize=6)
# cbar.ax.tick_params(labelsize=4)

# formatter = ticker.ScalarFormatter(useMathText=True)
# formatter.set_scientific(True)
# formatter.set_powerlimits((0, 0))
# cbar.formatter = formatter
# cbar.update_ticks()

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
plt.savefig('/home/bester/projects/ESO137/rise-paper-3/figures/eso006.png',
            dpi=500,
            bbox_inches='tight')
plt.close()
