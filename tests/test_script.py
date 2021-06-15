import pytest
from pathlib import Path
from SIEP.script import calculate_indices, read_geojson, main_sync
import numpy.ma as ma
from click.testing import CliRunner

DATA_PATH = Path("./tests/data")
GJSON_PATH = DATA_PATH / "quetta.geojson"

@pytest.fixture
@pytest.mark.asyncio
async def gjson():
    return await read_geojson(GJSON_PATH)

@pytest.mark.asyncio 
async def test_calculate_indices(gjson):
    indices = ('ndwi', 'ndvi')
    results = await calculate_indices(
        satellite="sentinel-2",
        product="l2a",
        gjson=gjson,
        indices=("ndwi", "ndvi")
    )
    for idx in indices:
        assert idx in results
        assert isinstance(results[idx], ma.MaskedArray)


@pytest.mark.parametrize("satellite, product, geojson_file, indices, raises", [
    ('sentinel-2', 'l2a', str(GJSON_PATH), ('ndwi',), False),
    ('landsat-8', 'l2a', str(GJSON_PATH), ('ndwi',), True),
    ('sentinel-2', 'l1c', str(GJSON_PATH), ('ndwi',), True),
    ('sentinel-2', 'l2a', str(GJSON_PATH), ('ndri',), True),

])
def test_script(satellite, product, geojson_file, indices, raises):
    runner = CliRunner()
    indices_command = []
    for idx in indices:
        indices_command.append("-i")
        indices_command.append(idx)
    result = runner.invoke(main_sync, ["-s", satellite, "-p", product, "-g", geojson_file]+indices_command)
    if raises:
        assert result.exception != None 
    else:
        assert not result.exception


