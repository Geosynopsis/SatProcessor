from pathlib import Path

import geojson
import numpy as np
import numpy.testing as npt
import pytest
from SIEP.utils.vector_operators import get_bound, transform

DATA_PATH = Path("./tests/data")


@pytest.mark.parametrize(
    "injson,epsg,outjson",
    [
        (
            DATA_PATH / "doberitzer_heide.geojson",
            3857,
            DATA_PATH / "doberitzer_heide_3857.geojson",
        )
    ],
)
def test_trasnform(injson, epsg, outjson):
    with open(injson) as j:
        o = transform(geojson.load(j), 4326, epsg)
        with open(outjson) as oj:
            for f1, f2 in zip(o.features, geojson.load(oj).features):
                assert f1.geometry.type == f2.geometry.type
                npt.assert_almost_equal(
                    np.array(f1.geometry.coordinates).round(1),
                    np.array(f1.geometry.coordinates).round(1),
                )


@pytest.mark.parametrize(
    "injson,bounds",
    [
        (
            DATA_PATH / "doberitzer_heide.geojson",
            (12.969017, 52.459461, 13.100681, 52.534602),
        ),
        (
            DATA_PATH / "doberitzer_heide_3857.geojson",
            (1443704.371736, 6883632.128507, 1458361.17191, 6897371.684341,),
        ),
        (
            DATA_PATH / "quetta.geojson",
            (
                67.00183868408203,
                30.171546895744946,
                67.03205108642578,
                30.196772595195785,
            ),
        ),
    ],
)
def test_bounds(injson, bounds):
    with open(injson) as j:
        assert get_bound(geojson.load(j)) == bounds
