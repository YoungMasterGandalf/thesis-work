import os
import numpy as np
import scipy.linalg

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
import sunpy.map
from sunpy.coordinates import HeliographicCarrington

import header_info as hi

# TODO: Fix and reintroduce logger
# from log import setup_logger

# module_logger = setup_logger(__name__)

class Dopplergram:
	def __init__(self, origin: list[float], shape: list[int], time_step: float, scale: list[float], r_sun: float, 
              artificial_lon_velocity: float, test_mode: bool, file_path: str, time_delta_relative_to_base: float=0.):
		self.origin = origin
		self.shape = shape
		self.time_step = time_step
		self.scale = scale
		self.r_sun = r_sun
		self.artificial_lon_velocity = artificial_lon_velocity
		self.test_mode = test_mode
     
		self.smap = sunpy.map.Map(file_path)
		self.time_delta_relative_to_base = time_delta_relative_to_base * u.second

	def get_postel_projected_data(self):

		"""
		Returns a numpy array of shape "shape" containing the projected subdata.

		Arguments:
		origin -- origin of the Postel projection (Heliographic Carrington coordinates)
		shape -- shape of the desired data matrix in pixels
		scale -- scaling vector --> deg/px
		"""

		projected_map = self.postel_project_map()

		return projected_map.data

	def postel_project_map(self):

		"""
		TODO: plot should be a separate method (or maybe shouldn't even be here)
		TODO 2: rect_offset is not a good solution --> solve somehow else
		"""

		rect_offset_x = self.origin[0]
		rect_offset_y = self.origin[1]

		origin = self.get_heliographic_carrington_origin()

		out_shape = self.shape
		out_header = sunpy.map.make_fitswcs_header(
		    out_shape,
		    origin,
			scale = self.scale * u.deg / u.pix,
		    projection_code="ARC"
		)

		out_map = self.smap.reproject_to(out_header)

		if self.test_mode:
			import matplotlib.pyplot as plt

			out_map.plot_settings = self.smap.plot_settings

			fig = plt.figure(figsize=(12, 6))

			ax = fig.add_subplot(1, 2, 1, projection=self.smap)
			self.smap.plot(axes=ax)
			self.smap.draw_grid(axes=ax, color='white')
			self.smap.draw_limb(axes=ax, color='white')
			ax.plot_coord(origin, 'o', color='red', fillstyle='none', markersize=20)

			bottom_left = SkyCoord((rect_offset_x - self.shape[0]/2*self.scale[0])*u.deg, 
                          (rect_offset_y - self.shape[1]/2*self.scale[1])*u.deg,
                       frame=HeliographicCarrington, obstime=self.smap.date, observer=self.smap.observer_coordinate)
			self.smap.draw_quadrangle(bottom_left, width=self.shape[0]*self.scale[0]*u.deg, 
                             height=self.shape[1]*self.scale[1]*u.deg, edgecolor='green', linewidth=1.5)

			ax = fig.add_subplot(1, 2, 2, projection=out_map)
			out_map.plot(axes=ax)
			out_map.draw_grid(axes=ax, color='blue')
			out_map.draw_limb(axes=ax, color='blue')
			ax.plot_coord(origin, 'o', color='red', fillstyle='none', markersize=20)

			ax.set_title('Postel projection centered at ROI', y=1.1)
			# plt.show()
			plt.savefig("/Users/daniel/Documents/doppl_projection.png", dpi=600)

		return out_map

	def get_heliographic_carrington_origin(self):
		origin = self.origin * u.deg
		r_sun = self.r_sun * u.Mm
		artificial_lon_velocity = self.artificial_lon_velocity * u.m/u.second

		carrington_frame = HeliographicCarrington(obstime=self.smap.date, 
					observer=self.smap.observer_coordinate, rsun=r_sun)

		origin = SkyCoord(origin[0], origin[1], frame=carrington_frame)
		
		radius = self._calculate_circle_of_latitude_radius(r_sun, latitude=origin.lat)
		angular_velocity = (artificial_lon_velocity/radius).si # omega = v/r
		angle = angular_velocity*self.time_delta_relative_to_base * u.rad # phi = omega*t
		
		shifted_origin = SkyCoord(origin.lon + angle, origin.lat, frame=carrington_frame)
		
		return shifted_origin

	def _calculate_circle_of_latitude_radius(self, r_sun, latitude):

		radius = r_sun*np.cos(latitude)

		return radius


def subtract_quadratic_surface_from_data(data: np.ndarray):

	transformed_data = np.zeros((data.shape[0]*data.shape[1], 3))

	current_index = 0
	for i in range(data.shape[0]):
		for j in range(data.shape[1]):
			transformed_data[current_index] = [i, j, data[i,j]]
			current_index += 1

	# regular grid covering the domain of the data
	X,Y = np.meshgrid(np.arange(data.shape[0]), np.arange(data.shape[1]))
	XX = X.flatten()
	YY = Y.flatten()

	# best-fit quadratic curve
	A = np.c_[np.ones(transformed_data.shape[0]), transformed_data[:,:2], np.prod(transformed_data[:,:2], axis=1), 
           transformed_data[:,:2]**2]
	solution, residues, rank, sing_vals = scipy.linalg.lstsq(A, transformed_data[:,2])
	
	# evaluate it on a grid
	quadratic_surface_points = np.dot(np.c_[np.ones(XX.shape), XX, YY, XX*YY, XX**2, YY**2], solution).reshape(X.shape)

	# Transpose surface fit points
	# TODO: Inspect the code and find why is it like this --> fix and comment the code for better clarity
	cleared_data = data - quadratic_surface_points.T

	return cleared_data

def fill_nan_values_with_median(data: np.ndarray) -> np.ndarray:
    data_median = np.nanmedian(data)
    new_data = np.nan_to_num(data, nan=data_median)
    
    return new_data


def create_datacube_from_files_in_folder(origin: list[float], shape: list[int], scale: list[float], r_sun: float, 
					 artificial_lon_velocity: float, test_mode: bool, folder_path: str, time_step:float=45.0):

	"""
	Looks into specified path, iterates through all of the present .fits files and returns a 3-D numpy array of shape 
 	(x-shape, y-shape, time-shape) containing series of Postel projected dopplergram data.

	Arguments:
	folder_path -- path to the directory containing .fits files for projections
	"""

	files = sorted([os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".fits")])
	
	file_count = len(files)
	base_index = int(file_count/2)

	datacube_array = np.zeros(shape=(file_count, shape[0], shape[1]))

	for i, file_path in enumerate(files):
		
		index_relative_to_base = i - base_index
		time_delta_relative_to_base = index_relative_to_base*time_step
		
		dg = Dopplergram(origin, shape, time_step, scale, r_sun, artificial_lon_velocity, test_mode, file_path, 
		   time_delta_relative_to_base=time_delta_relative_to_base)
		data = dg.get_postel_projected_data()
  
		data = fill_nan_values_with_median(data)

		data = subtract_quadratic_surface_from_data(data)

		datacube_array[i] = data
		
		if i == 0:
			hi.header_dict["T_REC_FI"] = [dg.smap.date.value, "Observation time of the first image"]

		if i == file_count - 1:
			hi.header_dict["T_REC_LA"] = [dg.smap.date.value, "Observation time of the last image"]

	return datacube_array


def create_fits_file_from_data_array(datacube_array: np.array, origin: list[float], scale: list[float], time_step: float, 
                                     r_sun: float, output_dir: str = ".", filename: str = "test.fits"):

	"""
	Takes a np.array datacube and parses it into a .fits file. Fits file details are specified in header_info.py

	Arguments:
	datacube_array -- numpy array to be parsed into .fits as data
	output_dir -- path to a directory where the .fits file should be stored
	filename -- name of the .fits file
	"""

	hi.header_dict["CRLN_REF"] = [origin[0], "Carrington lon of the reference point"]
	hi.header_dict["CRLT_REF"] = [origin[1], "Carrington lat of the reference point"]
	hi.header_dict["DAXIS1"] = [scale[0]*np.pi/180, "Scaling factor - x axis [rad/px]"]
	hi.header_dict["DAXIS2"] = [scale[1]*np.pi/180, "Scaling factor - y axis [rad/px]"]
	hi.header_dict["DAXIS3"] = [time_step, "Scaling factor - t axis (time step) [seconds]"]
	hi.header_dict["RSUN_MM"] = [r_sun, "Sun's radius in megameters"]
	

	print(f'Creating a .fits file "{filename}" from a datacube of shape {datacube_array.shape}...')
	hdu = fits.PrimaryHDU(datacube_array)
	
	for hdr_key, hdr_value in hi.header_dict.items():
		if hdr_value is not None:
			if type(hdr_value) == list:
				hdu.header.append((hdr_key, hdr_value[0], hdr_value[1]))
			else:
				hdu.header[hdr_key] = hdr_value

	hdul = fits.HDUList([hdu])

	if not os.path.isdir(output_dir):
		os.makedirs(output_dir)

	if not filename.endswith(".fits"):
		filename += ".fits"

	hdul.writeto(os.path.join(output_dir, filename), overwrite=True)

	print(f'Fits file "{filename}" created with a header:\n{hdu.header}')