#TODO: add configuration for saving data --> mainly fits but maybe also csv, numpy etc.

data_conf = {
    ##"path": "./data/test_mag/hmi.m_45s.20101020_000000_TAI.2.magnetogram.fits",
    #"path": "./data/test_doppl/hmi.v_45s.20181129_000000_TAI.2.Dopplergram.fits"
    "path": "C:\\Users\\42077\\OneDrive - Univerzita Karlova\\Diplomka\\Diplomka\\Dopplerograms\\hmi.v_45s.20181129_000000_TAI.2.Dopplergram.fits",
    "folder_path": "C:/Users/42077/OneDrive - Univerzita Karlova/Diplomka/Diplomka/Dopplerograms"
}

postel_conf = {
    #"origin": (137.51482, 5.5117860),
    "origin": (250, 0),
    "shape": (512, 512),
    #"scale": [0.0301, 0.0301],
    "scale": [0.12, 0.12],
    "make_plot": False,
    "r_sun": 696, # radius of the Sun in Mm
}

output_conf = {
    "save_file": True,
    "output_dir": ".",
    "filename": "test_file2.fits"
}