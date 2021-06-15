import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Iterable, List

import click
import geojson
import numpy as np
import pystac
import rasterio
import rasterio.features
import rasterio.windows
from matplotlib import pyplot as plt
from pyproj import CRS, Transformer

from SIEP.calculator import (
    Calculator,
    calculation_provider,
    generate_statistics,
)
from SIEP.downloader import Downloader, download_provider
from SIEP.searcher import Searcher, search_provider
from SIEP.utils.vector_operators import get_bound, transform

logging.basicConfig(level=logging.INFO)

FILE = "/home/abheeman/Documents/HobbyProjects/SatProcessor/doberitzer_heide.geojson"


def plot(array: np.ndarray, title: str):
    plt.figure()
    plt.imshow(array)
    plt.title(title)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.colorbar()


async def calculate_indices(
    satellite: str,
    product: str,
    gjson: geojson.Feature or geojson.FeatureCollection,
    indices: Iterable[str],
):
    """Calculates indices of the first scene for given satellite and product
    within the bound of the given geojson vector.

    Returns:
        Dict[str, np.ndarray]: Dictionary with indice names as key and resulting numpy masked array as value.
    """
    bbox = get_bound(gjson)
    provider_key = f"({satellite}, {product})"

    if provider_key not in search_provider.names:
        raise ValueError(
            f"No implementation of search provider exist for satellite {satellite} and product {product}"
        )

    explorer: Searcher = search_provider.get(provider_key)()
    res = await explorer.search_items(bbox)

    if provider_key not in download_provider.names:
        raise ValueError(
            f"No implementation of downloader exist for satellite {satellite} and product {product}"
        )
    dataaccessor: Downloader = download_provider.get(provider_key)(res.items[0])

    if provider_key not in calculation_provider.names:
        raise ValueError(
            f"No implementation of calculater exist for satellite {satellite} and product {product}"
        )
    operator: Calculator = calculation_provider.get(provider_key)(dataaccessor)

    indice_map = {}
    for idx in indices:
        indice_map[idx] = await operator.compute(idx, gjson=gjson)
    return indice_map


async def read_geojson(geojson_file: str):
    """Reads and validates geojson file

    Args:
        geojson_file (str): Path to the geojson file

    Returns:
        geojson.Feature or geojson.FeatureCollection: geojson feature or featurecollection
    """
    geojson_file = Path(geojson_file)
    assert geojson_file.exists(), "Geojson file doesn't exist"
    with open(geojson_file) as f:
        gjson = geojson.load(f)
        assert gjson.is_valid, "Provided geojson is not valid"
        return gjson


async def main(
    satellite: str,
    product: str,
    geojson_file: str,
    indices: Iterable[str],
    stats: bool,
):
    """Computes indices and their general statistics for latest scene for given
    satellite and product type. 

    Args:
        satellite (str): Satellite name sentinel-2
        product (str): Product name like l2a
        geojson_file (str): Geojson file denoting region of interest
        indices (Iterable[str]): Indice to calculate
        stats (bool): Should statistics be calculated
    """
    start = datetime.now()
    gjson = await read_geojson(geojson_file)
    indices_map = await calculate_indices(satellite, product, gjson, indices)
    for idx, indice in indices_map.items():
        if stats:
            print(f"Statistics for {idx}: {generate_statistics(indice)}")
        plot(indice, f"Indice {idx}")
    plt.show(block=True)
    print(f"It took {datetime.now() - start} ")


@click.command()
@click.option(
    "--satellite",
    "-s",
    default="sentinel-2",
    help="Satellite name in lowercase like sentinel-2, landsat-8",
)
@click.option(
    "--product",
    "-p",
    default="l2a",
    help="Product type name in lowercase like l1c, l2a",
)
@click.option(
    "--indices", "-i", help="Indice to calculate", multiple=True, required=True
)
@click.option(
    "--geojson_file",
    "-g",
    help="Geojson file denoting region of interest",
    required=True,
)
@click.option("--stats", "-st", help="Do you want statistics?", default=True)
def main_sync(satellite, product, indices, geojson_file, stats):

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(satellite, product, geojson_file, indices, stats)
    )


if __name__ == "__main__":
    main_sync()
