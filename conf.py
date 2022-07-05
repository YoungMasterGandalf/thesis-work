#TODO: add configuration for saving data --> mainly fits but maybe also csv, numpy etc.

data_conf = {
    ##"path": "./data/test_mag/hmi.m_45s.20101020_000000_TAI.2.magnetogram.fits",
    #"path": "./data/test_doppl/hmi.v_45s.20181129_000000_TAI.2.Dopplergram.fits"
    "path": "D:\\0_VSE\\hmi.v_45s.20100701_000000_TAI.2.Dopplergram.fits",
    "folder_path": "D:/0_VSE"
}

postel_conf = {
    "origin": (143, -20),
    "shape": (512, 512),
    #"scale": [0.0301, 0.0301],
    "scale": [0.12, 0.12],
    "make_plot": False,
    "r_sun": 696, # radius of the Sun in Mm
}

output_conf = {
    "save_file": True,
    "output_dir": "D:/0_VSE",
    "filename": "test_datacube.fits"
}