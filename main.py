from dopplergram import Dopplergram

if __name__ == "__main__":
	file = '../Diplomka/Dopplerograms/hmi.v_45s.20181129_000000_TAI.2.Dopplergram.fits'

	dg = Dopplergram(file)
	data = dg.get_postel_projected_data()
	print("data from main ", data)