import pytest
from astropy.io import fits as pyfits
from astropy.utils.data import get_pkg_data_filename, download_file
from numpy.testing import assert_array_almost_equal
from ..kepcotrend import kepcotrend
from ..kepio import delete

lc = download_file("https://archive.stsci.edu/missions/kepler/lightcurves/0051/005110407/kplr005110407-2009350155506_llc.fits", cache=True)
cbv = download_file("https://archive.stsci.edu/pub/kepler/cbv/kplr2009350155506-q03-d25_lcbv.fits", cache=True)
lc_cot = get_pkg_data_filename("data/kplr005110407-2009350155506_llc-kepcotrend.fits")
print(cbv)

def test_kepcotrend():
    kepcotrend(lc, cbv, '1 2 3', outfile="kepcotrend.fits")
    f = pyfits.open("kepcotrend.fits")
    g = pyfits.open(lc_cot)
    assert_array_almost_equal(f[1].data['CBVSAP_FLUX'],
                              g[1].data['CBVSAP_FLUX'])
    assert_array_almost_equal(f[1].data['CBVSAP_MODL'],
                              g[1].data['CBVSAP_MODL'])
    delete("kepcotrend.fits", "log_kepextract.txt", False)
