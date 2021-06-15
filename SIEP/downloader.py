import threading
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from os import cpu_count
from typing import Any, List

import numpy as np
import numpy.ma as ma
import pystac
import rasterio
import rasterio.features
import rasterio.windows
from geojson import Feature, FeatureCollection

from .provider import ProviderBase
from .searcher import search_provider
from .utils import get_block_candidates
from .utils.vector_operators import get_bound, transform
import logging

logger = logging.getLogger(__name__)


class Downloader(ABC):
    def __init__(self, item: pystac.Item):
        self._item = item

    @property
    def item(self):
        return self._item

    @abstractmethod
    async def download(
        self, assets: List[str], gjson: Feature or FeatureCollection = None,
    ) -> List[np.ndarray]:
        """Downloads the assets as list of numpy arrays belonging to given item. 

        Args:
            item (pystac.Item): Scene metadata with information regarding assets
            assets (List[str]): Name of assets to be downloaded
            gjson (FeatureorFeatureCollection, optional): Geojson which defines
                the extent and mask of the returned array. Defaults to None.

        Returns:
            List[np.ndarray]: List of numpy array in same order as assets
        """
        raise NotImplementedError


class COGDownloader(Downloader):
    def _download(self, href, gjson):

        THREAD_LOCK = threading.Lock()

        def read_window(ds, w):
            # Since we call this function from threads and the thread remain
            # idle while waiting for data, other processes could claim the
            # thread and therefore, there were problems of corrupt data
            # experience. Therefore, it's advisable to lock the thread while
            # it's waiting for data.
            logger.info(f"Downloading data {ds} for window {w}")
            with THREAD_LOCK:
                return ds.read(1, window=w)

        # Since we are using asynio `aiocogeo` would have been a great library
        # to be used. In trying to use it, there were some nodatavalues
        # introduced where data was supposed to be there. This could be replaced
        # with the library, once the solution the problem is figured out.
        with rasterio.open(href) as cog:
            transformed_gjson = transform(gjson, 4326, cog.crs.to_epsg())
            window = rasterio.features.geometry_window(
                dataset=cog,
                shapes=[g.geometry for g in transformed_gjson.features],
            )

            mask = rasterio.features.geometry_mask(
                geometries=[g.geometry for g in transformed_gjson.features],
                out_shape=(window.height, window.width),
                transform=(
                    cog.transform[0],
                    cog.transform[1],
                    cog.transform[2] + window.col_off * cog.transform[0],
                    cog.transform[3],
                    cog.transform[4],
                    cog.transform[5] + window.row_off * cog.transform[4],
                ),
                all_touched=True,
            )

            windows = [
                rasterio.windows.Window(
                    col_off=w[0], row_off=w[1], width=w[2], height=w[3]
                )
                for w in get_block_candidates(
                    width=window.width,
                    height=window.height,
                    x_off=window.col_off,
                    y_off=window.row_off,
                    x_chunk=1024,
                    y_chunk=1024,
                )
            ]
            array = np.zeros((window.height, window.width))
            with ThreadPoolExecutor(cpu_count()) as executor:
                for w, res in zip(
                    windows,
                    executor.map(read_window, [cog] * len(windows), windows),
                ):
                    x_start = w.col_off - window.col_off
                    y_start = w.row_off - window.row_off
                    x_end = x_start + w.width
                    y_end = y_start + w.height
                    array[y_start:y_end, x_start:x_end] = res
            return ma.masked_array(array, mask=mask)

    async def download(self, assets, gjson=None):
        assert all(
            self.item.assets.get(a, None) != None for a in assets
        ), "All assets to download must exist in item"
        hrefs = [self.item.assets[asset].href for asset in assets]
        func = partial(self._download, gjson=gjson)
        arrays = {}
        with ThreadPoolExecutor(cpu_count()) as executor:
            for asset, array in zip(assets, executor.map(func, hrefs)):
                arrays[asset] = array
        return [arrays[a] for a in assets]


download_provider = ProviderBase(obj_type=Downloader)
download_provider.register("sentinel-2_l2a", COGDownloader)

