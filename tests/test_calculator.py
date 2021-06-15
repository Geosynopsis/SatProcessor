import numpy as np
import numpy.testing as npt
import pytest
from SIEP.calculator import Sentinel2Calculator
from SIEP.downloader import Downloader





@pytest.fixture
def calculator():
    class FakeDownloader(Downloader):
        async def download(self, assets, gjson=None):
            arrays = []
            for idx, asset in enumerate(assets):
                arrays.append(np.ones((100, 100)) * (idx + 1))
            return arrays
    fakedownloader = FakeDownloader(None)
    return Sentinel2Calculator(fakedownloader)


@pytest.mark.asyncio
async def test_ndvi(calculator):
    ndvi = await calculator.compute("ndvi")
    npt.assert_almost_equal(ndvi, np.ones((100, 100)) * (1.0/3.0))

@pytest.mark.asyncio
async def test_ndwi(calculator):
    ndvi = await calculator.compute("ndwi")
    npt.assert_almost_equal(ndvi, np.ones((100, 100)) * (-1.0/3.0))

