from astropy.io import fits

hdul = fits.open("/nfshome/michal/students/Chmurny/DATACUBES/new_quad_surf_corr.fits")
# hdul = fits.open("/home/daniel/Downloads/new_quadr_surf_corr.fits")

print(hdul.info())
print(hdul[0].header)

hdul.close()
