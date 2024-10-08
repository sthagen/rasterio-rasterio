import logging
import sys

import pytest
import rasterio

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def test_tags_read():
    with rasterio.open('tests/data/RGB.byte.tif') as src:
        assert src.tags() == {'AREA_OR_POINT': 'Area'}
        assert src.tags(ns='IMAGE_STRUCTURE') == {'INTERLEAVE': 'PIXEL'}
        assert src.tags(ns='bogus') == {}
        assert 'STATISTICS_MAXIMUM' in src.tags(1)
        with pytest.raises(IndexError):
            tags = src.tags(4)

def test_tags_update(tmpdir):
    tiffname = str(tmpdir.join('foo.tif'))
    with rasterio.open(
            tiffname, 
            'w', 
            driver='GTiff', 
            count=1, 
            dtype=rasterio.uint8, 
            width=10, 
            height=10) as dst:

        dst.update_tags(a='1', b='2')
        dst.update_tags(1, c=3)
        with pytest.raises(IndexError):
            dst.update_tags(4, d=4)

        assert dst.tags() == {'a': '1', 'b': '2'}
        assert dst.tags(1) == {'c': '3' }
        
        # Assert that unicode tags work.
        # Russian text appropriated from pytest issue #319
        # https://bitbucket.org/hpk42/pytest/issue/319/utf-8-output-in-assertion-error-converted
        dst.update_tags(ns="rasterio_testing", rus="другая строка")
        assert dst.tags(ns="rasterio_testing") == {"rus": "другая строка"}

    with rasterio.open(tiffname) as src:
        assert src.tags() == {"a": "1", "b": "2"}
        assert src.tags(1) == {"c": "3"}
        assert src.tags(ns="rasterio_testing") == {"rus": "другая строка"}


def test_tags_update_twice(tmpdir):
    path = str(tmpdir.join('test.tif'))
    with rasterio.open(
            path, 'w',
            'GTiff', 3, 4, 1, dtype=rasterio.ubyte) as dst:
        dst.update_tags(a=1, b=2)
        assert dst.tags() == {'a': '1', 'b': '2'}
        dst.update_tags(c=3)
        assert dst.tags() == {'a': '1', 'b': '2', 'c': '3'}


def test_tags_eq(tmpdir):
    path = str(tmpdir.join('test.tif'))
    with rasterio.open(
            path, 'w',
            'GTiff', 3, 4, 1, dtype=rasterio.ubyte) as dst:
        dst.update_tags(a="foo=bar")
        assert dst.tags() == {'a': "foo=bar"}

def test_tags_xml_prefix():
    with rasterio.open('tests/data/RGB.byte.rpc.vrt') as src:
        md = src.tags(ns='xml:VRT')
        assert 'xml:VRT' in md
        assert md.get('xml:VRT').startswith('<VRTDataset')
