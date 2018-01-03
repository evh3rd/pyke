import numpy as np
from astropy.utils.data import get_pkg_data_filename
import pytest
from ..targetpixelfile import KeplerTargetPixelFile, KeplerQualityFlags


filename_tpf_all_zeros = get_pkg_data_filename("data/test-tpf-all-zeros.fits")
filename_tpf_one_center = get_pkg_data_filename("data/test-tpf-non-zero-center.fits")


def test_tpf_shapes():
    """Are the data array shapes of the TargetPixelFile object consistent?"""
    tpf = KeplerTargetPixelFile(filename_tpf_all_zeros)
    assert tpf.quality_mask.shape == tpf.hdu[1].data['TIME'].shape
    assert tpf.aperture_mask.shape == tpf.hdu[1].data['FLUX'][0].shape
    assert tpf.flux.shape == tpf.flux_err.shape

def test_tpf_zeros():
    """Does the LightCurve of a zero-flux TPF make sense?"""
    tpf = KeplerTargetPixelFile(filename_tpf_all_zeros,quality_bitmask=None)
    lc = tpf.to_lightcurve()
    #IF you don't mask out bad data, time contains NaNs:
    assert np.any(lc.time != tpf.time)
    #When you do mask out bad data everything should work.
    tpf = KeplerTargetPixelFile(filename_tpf_all_zeros,quality_bitmask='hard')
    lc = tpf.to_lightcurve()
    assert len(lc.time) == len(lc.flux)
    assert np.all(lc.time == tpf.time)
    assert np.all(lc.flux == 0)
    # The default QUALITY bitmask should have removed all NaNs in the TIME
    assert ~np.any(np.isnan(tpf.time))

def test_tpf_ones():
    """Does the LightCurve of a one-flux TPF make sense?"""
    tpf = KeplerTargetPixelFile(filename_tpf_one_center)
    lc = tpf.to_lightcurve()
    assert np.all(lc.flux == 1)

def test_quality_flag_decoding():
    """Can the QUALITY flags be parsed correctly?"""
    flags = list(KeplerQualityFlags.STRINGS.items())
    for key, value in flags:
        assert KeplerQualityFlags.decode(key)[0] == value
    # Can we recover combinations of flags?
    assert KeplerQualityFlags.decode(flags[5][0] + flags[7][0]) == [flags[5][1], flags[7][1]]
    assert KeplerQualityFlags.decode(flags[3][0] + flags[4][0] + flags[5][0]) \
        == [flags[3][1], flags[4][1], flags[5][1]]

@pytest.mark.parametrize("quality_bitmask,answer",[('hard', 1101),
    ('conservative', 1141), ('default', 1275), (None, 1290),
    (1, 1290), (100, 1278), (2096639, 1101)])

def test_bitmasking(quality_bitmask,answer):
    '''Test whether the bitmasking behaves like it should'''
    tpf = KeplerTargetPixelFile(filename_tpf_one_center, quality_bitmask=quality_bitmask)
    lc = tpf.to_lightcurve()
    flux = lc.flux
    assert len(flux) == answer

def test_aperture_masking_errors():
    tpf = KeplerTargetPixelFile(filename_tpf_one_center, quality_bitmask='hard')
    af, er = tpf._get_aperture_flux()
    assert len(af) == len(er)
    assert np.all(er > 0)
    assert isinstance(er[0], np.float32)
    assert np.all(np.isfinite(af))
    assert np.all(np.isfinite(er))
