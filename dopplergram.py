import matplotlib.pyplot as plt

import astropy.units as u
from astropy.coordinates import SkyCoord

import sunpy.map
from sunpy.coordinates import HeliographicStonyhurst

class Dopplergram:
	def __init__(self, path):
		self.path = path
		self.smap = None
		self.data = None

	def get_postel_projected_data(self, origin = (0, 0), shape = (512, 512), scale: list = [0.12, 0.12]):

		"""
		Returns a numpy array of shape "shape" containing the projected subdata.

		Arguments:
		origin -- origin of the Postel projection (so far Helioprojective!!!)
		shape -- shape of the desired data matrix in pixels
		scale -- scaling vector --> deg/px
		"""

		self._create_sunpy_map_from_file(self.path)
		self.data = self.smap.data

		projected_map = self._postel_project_map(origin, shape, scale)

		return projected_map.data

	def _create_sunpy_map_from_file(self, filepath: str):

		self.smap = sunpy.map.Map(filepath)
		#aia_map.plot_settings['norm'].vmin = 0
		#aia_map.plot_settings['norm'].vmax = 10000

	def _postel_project_map(self, origin, shape, scale, to_plot=True):

		"""
		TODO: plot should be a separate method (or maybe shouldn't even be here)
		"""

		smap = self.smap
		origin = self._get_heliographic_stonyhurst_origin(origin)

		#out_shape = (512, 512)
		out_shape = shape
		out_header = sunpy.map.make_fitswcs_header(
		    out_shape,
		    origin,
		    #scale=[0.12, 0.12]*u.deg/u.pix,
		    scale=scale*u.deg/u.pix,
		    projection_code="ARC"
		)

		out_map = smap.reproject_to(out_header)
		out_map.plot_settings = smap.plot_settings

		print("data ", out_map.data)
		print("shape ", out_map.data.shape)

		if to_plot:
			fig = plt.figure(figsize=(8, 4))

			ax = fig.add_subplot(1, 2, 1, projection=smap)
			smap.plot(axes=ax)
			smap.draw_grid(axes=ax, color='white')
			smap.draw_limb(axes=ax, color='white')
			ax.plot_coord(origin, 'o', color='red', fillstyle='none', markersize=20)

			bottom_left = SkyCoord(-shape[0]/2*scale[0]*u.deg, -shape[1]/2*scale[1]*u.deg,
                       frame=HeliographicStonyhurst, obstime=smap.date)
			smap.draw_quadrangle(bottom_left, width=shape[0]*scale[0]*u.deg, height=shape[1]*scale[1]*u.deg,
                    edgecolor='green', linewidth=1.5)

			ax = fig.add_subplot(1, 2, 2, projection=out_map)
			out_map.plot(axes=ax)
			out_map.draw_grid(axes=ax, color='blue')
			out_map.draw_limb(axes=ax, color='blue')
			ax.plot_coord(origin, 'o', color='red', fillstyle='none', markersize=20)
			ax.set_title('Postel projection centered at ROI', y=-0.1)
			plt.show()

		return out_map

	def _get_heliographic_stonyhurst_origin(self, origin):

		smap = self.smap
		origin_hpc = SkyCoord(origin[0]*u.arcsec, origin[1]*u.arcsec, frame=smap.coordinate_frame)
		origin = origin_hpc.heliographic_stonyhurst

		return origin

