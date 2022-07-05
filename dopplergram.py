import os
import numpy as np

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
import sunpy.map
from sunpy.coordinates import HeliographicCarrington

from conf import postel_conf

import datetime


header_dict = {
    "T_REC_FI": None,
    "T_REC_LA": None,
    "CRLN_REF": None,
    "CRLT_REF": None,
    "CDELT1": None,
    "CDELT2": None
}


class Dopplergram:
	def __init__(self, file_path):
		self.path = file_path
		self.smap = None
		self.data = None

	def get_postel_projected_data(self, origin = (0, 0), shape = (512, 512), scale: list = [0.12, 0.12], make_plot: bool = True):

		"""
		Returns a numpy array of shape "shape" containing the projected subdata.

		Arguments:
		origin -- origin of the Postel projection (Heliographic Carrington coordinates)
		shape -- shape of the desired data matrix in pixels
		scale -- scaling vector --> deg/px
		"""

		self._create_sunpy_map_from_file(self.path)
		self.data = self.smap.data

		projected_map = self._postel_project_map(origin, shape, scale, make_plot)

		return projected_map.data

	def _create_sunpy_map_from_file(self, filepath: str):

		self.smap = sunpy.map.Map(filepath)

	def _postel_project_map(self, origin, shape, scale, make_plot):

		"""
		TODO: plot should be a separate method (or maybe shouldn't even be here)
		TODO 2: rect_offset is not a good solution --> solve somehow else
		"""

		rect_offset_x = origin[0]
		rect_offset_y = origin[1]

		smap = self.smap
		origin = self._get_heliographic_carrington_origin(origin)

		out_shape = shape
		out_header = sunpy.map.make_fitswcs_header(
		    out_shape,
		    origin,
		    scale=scale*u.deg/u.pix,
		    projection_code="ARC"
		)

		out_map = smap.reproject_to(out_header)

		if make_plot:

			import matplotlib.pyplot as plt

			out_map.plot_settings = smap.plot_settings

			fig = plt.figure(figsize=(8, 4))

			ax = fig.add_subplot(1, 2, 1, projection=smap)
			smap.plot(axes=ax)
			smap.draw_grid(axes=ax, color='white')
			smap.draw_limb(axes=ax, color='white')
			ax.plot_coord(origin, 'o', color='red', fillstyle='none', markersize=20)

			bottom_left = SkyCoord((rect_offset_x - shape[0]/2*scale[0])*u.deg, (rect_offset_y - shape[1]/2*scale[1])*u.deg,
                       frame=HeliographicCarrington, obstime=smap.date, observer=smap.observer_coordinate)
			smap.draw_quadrangle(bottom_left, width=shape[0]*scale[0]*u.deg, height=shape[1]*scale[1]*u.deg,
                    edgecolor='green', linewidth=1.5)

			ax = fig.add_subplot(1, 2, 2, projection=out_map)
			out_map.plot(axes=ax)
			out_map.draw_grid(axes=ax, color='blue')
			out_map.draw_limb(axes=ax, color='blue')
			ax.plot_coord(origin, 'o', color='red', fillstyle='none', markersize=20)

			### Green former quadrangle projected on the Postel map 
			#out_map.draw_quadrangle(bottom_left, width=shape[0]*scale[0]*u.deg, height=shape[1]*scale[1]*u.deg,
            #        edgecolor='green', linewidth=1.5)

			ax.set_title('Postel projection centered at ROI', y=-0.1)
			plt.show()

		return out_map

	def _get_heliographic_carrington_origin(self, origin):

		smap = self.smap
		r_sun = postel_conf["r_sun"]

		origin = SkyCoord(origin[0]*u.deg, origin[1]*u.deg, frame=HeliographicCarrington, obstime=smap.date, 
					observer=smap.observer_coordinate, rsun=r_sun*u.Mm)

		return origin


def create_datacube_iterator_from_files_in_folder(folder_path: str):
	# TODO: 1. Add support for user defined speed of ref point movement, 2. Add differential rotation, 3. Add paralellization

	"""
	Looks into specified path, iterates through all of the present .fits files and returns a 3-D numpy array of shape (x-shape, y-shape, time-shape) containing series 
	of Postel projected dopplergram data.

	Arguments:
	folder_path -- path to the directory containing .fits files for projections
	"""

	origin = postel_conf["origin"]
	shape = postel_conf["shape"]
	scale = postel_conf["scale"]
	make_plot = postel_conf["make_plot"]
	
	try:
		file_object = os.listdir(folder_path)
	except Exception as e:
		print(e)
		return None

	# datacube_list = []

	for i, filename in enumerate(file_object):
		
		file_path = os.path.join(folder_path, filename)
		
		if os.path.isfile(file_path):
			dg = Dopplergram(file_path)
			start = datetime.datetime.now()
			data = dg.get_postel_projected_data(origin=origin, shape=shape, scale=scale, make_plot=make_plot)
			projection_time = datetime.datetime.now() - start
			print(f"PROJECTION {i} RUNTIME ", projection_time)

			# datacube_list.append(data.tolist())
			
			if i == 0:
				header_dict["T_REC_FI"] = [dg.smap.date.value, "Observation time of the first image"]

			if i == len(list(file_object)) - 1:
				header_dict["T_REC_LA"] = [dg.smap.date.value, "Observation time of the last image"]

			yield data

	# datacube_array = np.array(datacube_list)

	# return datacube_array


def create_fits_file_from_data_array(datacube_array: np.array, output_dir: str = ".", filename: str = "test.fits"):

	"""
	Takes a np.array datacube and parses it into a .fits file. Fits file details are specified in header_info.py

	Arguments:
	datacube_array -- numpy array to be parsed into .fits as data
	output_dir -- path to a directory where the .fits file should be stored
	filename -- name of the .fits file
	"""

	origin = postel_conf["origin"]
	scale = postel_conf["scale"]

	header_dict["CRLN_REF"] = [origin[0], "Carrington lon of the reference point"]
	header_dict["CRLT_REF"] = [origin[1], "Carrington lat of the reference point"]
	header_dict["CDELT1"] = [scale[0]*np.pi/180, "Scaling factor - x axis [rad/px]"]
	header_dict["CDELT2"] = [scale[1]*np.pi/180, "Scaling factor - y axis [rad/px]"]

	print("SHAPE ", datacube_array.shape)
	hdu = fits.PrimaryHDU(datacube_array)
	
	for hdr_key, hdr_value in header_dict.items():
		if hdr_value is not None:
			if type(hdr_value) == list:
				hdu.header.append((hdr_key, hdr_value[0], hdr_value[1]))
			else:
				hdu.header[hdr_key] = hdr_value

	hdul = fits.HDUList([hdu])
	hdul.writeto(os.path.join(output_dir, filename), overwrite=True)

	print("HEADER ", hdu.header)

def stack_images(iterable, shape):
	
	datacube = np.zeros(shape)

	for i, item in enumerate(iterable):
		print("INDEX ", i)
		print(f"DATACUBE {i} SHAPE ", datacube[i].shape)
		datacube += item

	return datacube