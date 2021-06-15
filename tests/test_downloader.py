import json
from datetime import datetime
from pathlib import Path

import geojson
import pystac
import pytest
from SIEP.downloader import COGDownloader
from SIEP.searcher import Sentinel2L2ASearcher

DATA_PATH = Path("./tests/data")
GJSON_PATH = DATA_PATH / "quetta.geojson"


@pytest.fixture
def gjson():
    with open(GJSON_PATH) as f:
        return geojson.load(f)


@pytest.fixture
@pytest.mark.asyncio
async def downloader():
    res = await Sentinel2L2ASearcher().search_items(
        [67.001839, 30.171547, 67.032051, 30.196773,],
        datetime(2018, 1, 1),
        datetime(2018, 2, 1),
    )
    item = res.items[0]
    return COGDownloader(item)


@pytest.mark.asyncio
async def test_download(downloader, gjson):
    red = await downloader.download(assets=["B04"], gjson=gjson)
    assert red[0].mean() == 2014.7269139051066
    assert red[0].data.mean() == 2013.230553552832
    assert red[0].std() == 495.68389860043123
    assert red[0].data.std() == 495.62663211419215
