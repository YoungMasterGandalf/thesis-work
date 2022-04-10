from dopplergram import Dopplergram
import numpy as np

from conf import data_conf, postel_conf

file_path = data_conf["path"]

origin = postel_conf["origin"]
shape = postel_conf["shape"]
scale = postel_conf["scale"]
make_plot = postel_conf["make_plot"]

if __name__ == "__main__":
	file = file_path

	dg = Dopplergram(file)
	data = dg.get_postel_projected_data(origin=origin, shape=shape, scale=scale, make_plot=make_plot)

	#np.savetxt("data2.csv", data, delimiter=",")

	print("data from main ", data)