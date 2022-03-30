from dopplergram import Dopplergram
import datetime
import numpy as np

if __name__ == "__main__":
	start = datetime.datetime.now()
	file = '../Diplomka/Dopplerograms/hmi.v_45s.20181129_000000_TAI.2.Dopplergram.fits'

	dg = Dopplergram(file)
	data = dg.get_postel_projected_data()

	np.savetxt("data2.csv", data, delimiter=",")

	print("time elapsed ", datetime.datetime.now() - start)
	print("data from main ", data)