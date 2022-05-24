import astropy.units as u
from astropy.coordinates import SkyCoord
import sunpy.map
from sunpy.coordinates import HeliographicCarrington

class Dopplergram:
	def __init__(self, path):
		self.path = path
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
		print("HEADER ", out_map.fits_header)
		print("TOP RIGHT COORD ", out_map.top_right_coord)
		print("BOTTOM LEFT COORD ", out_map.bottom_left_coord)
		print("data ", out_map.data)
		print("shape ", out_map.data.shape)
		print("FRAME ", out_map.coordinate_frame)

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

		origin = SkyCoord(origin[0]*u.deg, origin[1]*u.deg, frame=HeliographicCarrington, obstime=smap.date, 
					observer=smap.observer_coordinate, rsun=696000*u.km)

		return origin

