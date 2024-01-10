import drms
import os

from urllib.request import urlretrieve
from urllib.error import URLError, HTTPError

TEST_QUERY = "hmi.v_45s[2011.01.11_00:00:00_TAI/30m]{Dopplergram}"
OUT_DIR = "/Users/daniel/Downloads/drms_test"
VERBOSE = True

def next_available_filename(fname):
    """
    Find next available filename, append a number if neccessary.
    """
    i = 1
    new_fname = fname
    while os.path.exists(new_fname):
        new_fname = f"{fname}.{int(i)}"
        i += 1
    return new_fname

if __name__ == "__main__":
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
        
    client = drms.Client(email="daniel123chmurny@gmail.com", verbose=True)
    export_request = client.export(TEST_QUERY, method="url", protocol="fits")
    export_request.wait(timeout=300, verbose=True)

    # self.urls contains the same records as self.data, except for the tar
    # methods, where self.urls only contains one entry, the TAR file.
    data = export_request.urls
    ndata = len(data)

    downloads = []
    for i in range(ndata):
        di = data.iloc[i]
        filename = di.filename

        fpath = os.path.join(OUT_DIR, filename)
        
        download_try = 1
        max_download_try_count = 10
        is_downloaded = False
        
        fpath_new = next_available_filename(fpath)
        # fpath_new = fpath
        fpath_tmp = next_available_filename(f"{fpath_new}.part")
        
        verbose = VERBOSE
        
        while (not is_downloaded) and (download_try < max_download_try_count):
            if verbose:
                print(f"Downloading file {int(i + 1)} (try no. {download_try}) of {int(ndata)}...")
                print(f"    record: {di.record}")
                print(f"  filename: {di.filename}")
            try:
                # print(f'Downloading file {i}: {filename}')
                # urlretrieve(di.url, fpath)
                urlretrieve(di.url, fpath_tmp)
            except (HTTPError, URLError):
                print(f'Download {download_try} failed.')
                download_try += 1
            else:
                fpath_new = next_available_filename(fpath)
                os.rename(fpath_tmp, fpath_new)
                if verbose:
                    print(f"  -> {os.path.relpath(fpath_new)}")
                is_downloaded = True
            
        if is_downloaded:
            downloads.append(fpath)
        else:
            raise Exception("File missing, download aborted.")

    res = data[["record", "url"]].copy()
    res["download"] = downloads

    print(export_request.status)
