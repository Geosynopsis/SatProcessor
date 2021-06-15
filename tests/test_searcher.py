import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

import pytest
from shapely.geometry import box, shape
from SIEP.searcher import Sentinel2L2ASearcher

DATA_PATH = Path("./tests/data")


@pytest.fixture
def explorer():
    return Sentinel2L2ASearcher()


@pytest.mark.asyncio
async def test_collection(explorer):
    with open(DATA_PATH / "s2-l2a-cogs.json") as f:
        data = json.load(f)
        collection = await explorer.get_collection()
        data == collection.to_dict()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bbox,start_date,end_date,check_navigation",
    [
        ([53, 25, 55, 28], None, None, False),
        ([], datetime(2018, 1, 1), datetime(2018, 2, 1), False),
    ],
)
async def test_element84_explorer_success(
    explorer, bbox, start_date, end_date, check_navigation
):
    if not bbox:
        bbox = [-180, -90, 180, 90]
    bbox_shape = box(*bbox)
    res = await explorer.search_items(bbox, start_date, end_date)
    last_datetime = datetime.utcnow()
    items = deepcopy(res.items)
    for item in res.items:
        assert item.datetime <= last_datetime.replace(
            tzinfo=item.datetime.tzinfo
        )
        last_datetime = item.datetime
        footprint = shape(item.geometry)
        assert bbox_shape.intersects(footprint)

    # TODO: The next_items and previous_items aren't working with full capacity
    #  as the Element84API isn't navigatable, as it should be, when bounding box
    #  is passed. However, it can be addressed by passing the search context to
    #  the result itself.

    # if check_navigation:
    #     res = await res.next_items()
    #     for item in res.items:
    #         assert item.datetime < last_datetime
    #         last_datetime = item.datetime

    #     res = await res.previous_items()
    #     assert items == res.items

