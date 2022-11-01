import os
import numpy as np
import datetime

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
import sunpy.map
from sunpy.coordinates import HeliographicCarrington, RotatedSunFrame

import header_info as hi
from conf import PATH, FOLDER_PATH, ORIGIN, SHAPE, TIME_STEP, SCALE, MAKE_PLOT, R_SUN, ARTIFICIAL_LON_VELOCITY, SAVE_FILE, OUTPUT_DIR, FILENAME


class Dopplergram:
	def __init__(self, file_path, time_delta_relative_to_base:float=0.):
		self.path = file_path
		self.smap = sunpy.map.Map(self.path)
		self.data = self.smap.data
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

		rect_offset_x = ORIGIN[0]
		rect_offset_y = ORIGIN[1]

		origin = self.get_heliographic_carrington_origin()

		out_shape = SHAPE
		out_header = sunpy.map.make_fitswcs_header(
		    out_shape,
		    origin,
		    scale=SCALE*u.deg/u.pix,
		    projection_code="ARC"
		)

		out_map = self.smap.reproject_to(out_header)

		if MAKE_PLOT:

			import matplotlib.pyplot as plt

			out_map.plot_settings = self.smap.plot_settings

			fig = plt.figure(figsize=(8, 4))

			ax = fig.add_subplot(1, 2, 1, projection=self.smap)
			self.smap.plot(axes=ax)
			self.smap.draw_grid(axes=ax, color='white')
			self.smap.draw_limb(axes=ax, color='white')
			ax.plot_coord(origin, 'o', color='red', fillstyle='none', markersize=20)

			bottom_left = SkyCoord((rect_offset_x - SHAPE[0]/2*SCALE[0])*u.deg, (rect_offset_y - SHAPE[1]/2*SCALE[1])*u.deg,
                       frame=HeliographicCarrington, obstime=self.smap.date, observer=self.smap.observer_coordinate)
			self.smap.draw_quadrangle(bottom_left, width=SHAPE[0]*SCALE[0]*u.deg, height=SHAPE[1]*SCALE[1]*u.deg,
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

	def get_heliographic_carrington_origin(self):

		origin = ORIGIN * u.deg
		r_sun = R_SUN * u.Mm
		artificial_lon_velocity = ARTIFICIAL_LON_VELOCITY * u.m/u.second

		carrington_frame = HeliographicCarrington(obstime=self.smap.date, 
					observer=self.smap.observer_coordinate, rsun=r_sun)

		origin = SkyCoord(origin[0], origin[1], frame=carrington_frame)
		
		diffrot_origin = RotatedSunFrame(base=origin, duration=self.time_delta_relative_to_base)
		transformed_diffrot_origin = diffrot_origin.transform_to(carrington_frame)
		
		radius = self._calculate_circle_of_latitude_radius(r_sun, latitude=origin.lat)
		angular_velocity = (artificial_lon_velocity/radius).si # omega = v/r
		angle = angular_velocity*self.time_delta_relative_to_base * u.rad # phi = omega*t
		
		transformed_diffrot_origin = SkyCoord(transformed_diffrot_origin.lon + angle, transformed_diffrot_origin.lat, frame=carrington_frame)
		
		return transformed_diffrot_origin

	def _calculate_circle_of_latitude_radius(self, r_sun, latitude):

		radius = r_sun*np.cos(latitude)

		return radius


def create_datacube_from_files_in_folder(folder_path: str, time_step:float=45.0):

	"""
	Looks into specified path, iterates through all of the present .fits files and returns a 3-D numpy array of shape (x-shape, y-shape, time-shape) containing series 
	of Postel projected dopplergram data.

	Arguments:
	folder_path -- path to the directory containing .fits files for projections
	"""
	
	try:
		file_object = os.listdir(folder_path)
	except Exception as e:
		print(e)
		return None

	datacube_list = []
	file_count = len(list(file_object))
	base_index = int(file_count/2)

	start1 = datetime.datetime.now()
	for i, filename in enumerate(file_object):
		file_path = os.path.join(folder_path, filename)
		index_relative_to_base = i - base_index
		time_delta_relative_to_base = index_relative_to_base*time_step
		
		if os.path.isfile(file_path):
			start = datetime.datetime.now()
			dg = Dopplergram(file_path, time_delta_relative_to_base=time_delta_relative_to_base)
			data = dg.get_postel_projected_data()
			print(f"PROJECTION {i} RUNTIME ", datetime.datetime.now() - start)

			datacube_list.append(data.tolist())
			
			if i == 0:
				hi.header_dict["T_REC_FI"] = [dg.smap.date.value, "Observation time of the first image"]

			if i == len(list(file_object)) - 1:
				hi.header_dict["T_REC_LA"] = [dg.smap.date.value, "Observation time of the last image"]
		
	print("FOR LOOP RUNTIME ", datetime.datetime.now() - start1)

	datacube_array = np.array(datacube_list)

	return datacube_array


def create_fits_file_from_data_array(datacube_array: np.array, output_dir: str = ".", filename: str = "test.fits"):

	"""
	Takes a np.array datacube and parses it into a .fits file. Fits file details are specified in header_info.py

	Arguments:
	datacube_array -- numpy array to be parsed into .fits as data
	output_dir -- path to a directory where the .fits file should be stored
	filename -- name of the .fits file
	"""

	hi.header_dict["CRLN_REF"] = [ORIGIN[0], "Carrington lon of the reference point"]
	hi.header_dict["CRLT_REF"] = [ORIGIN[1], "Carrington lat of the reference point"]
	hi.header_dict["DAXIS1"] = [SCALE[0]*np.pi/180, "Scaling factor - x axis [rad/px]"]
	hi.header_dict["DAXIS2"] = [SCALE[1]*np.pi/180, "Scaling factor - y axis [rad/px]"]
	hi.header_dict["DAXIS3"] = [TIME_STEP, "Scaling factor - t axis (time step) [seconds]"]
	hi.header_dict["RSUN_MM"] = [R_SUN, "Sun's radius in megameters"]
	

	print("SHAPE ", datacube_array.shape)
	hdu = fits.PrimaryHDU(datacube_array)
	
	for hdr_key, hdr_value in hi.header_dict.items():
		if hdr_value is not None:
			if type(hdr_value) == list:
				hdu.header.append((hdr_key, hdr_value[0], hdr_value[1]))
			else:
				hdu.header[hdr_key] = hdr_value

	hdul = fits.HDUList([hdu])

	if not os.isdir(output_dir):
		os.makedirs(output_dir)

	hdul.writeto(os.path.join(output_dir, filename), overwrite=True)

	print("HEADER ", hdu.header)