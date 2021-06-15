import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List

import aiohttp
import pystac

from .provider import ProviderBase


class ItemCollection:
    """
    Very simple implementation of the ItemCollection response of STAC Search.
    It's implemented here since it's not available in pystac.
    """

    def __init__(self, item_collection: Dict):
        self._items = []
        for feature in item_collection["features"]:
            self._items.append(pystac.Item.from_dict(feature))
        self._next_url = None
        self._prev_url = None
        for link in item_collection["links"]:
            if link["rel"] == "next":
                self._next_url = link["href"]
            if link["rel"] == "prev":
                self._prev_url = link["href"]

    @property
    def items(self) -> List[pystac.Item]:
        """Returns list of scenes in current response
        
        Returns:
            List[pystac.Item]: List of scenes.
        """
        return self._items

    async def _make_request(self, url):
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url) as resp:
                if resp.status == 200:
                    return self.__class__(await resp.json())
                text = await resp.text()
                raise Exception(text)

    async def next_items(self) -> "ItemCollection":
        if self._next_url:
            return await self._make_request(self._next_url)

    async def previous_items(self) -> "ItemCollection":
        if self._prev_url:
            return await self._make_request(self._prev_url)


class Searcher(ABC):
    """
    Abstract class for explorer. It's assumed that each implementation of
    Explorer is developed according STAC Specification for single collection
    """

    @abstractmethod
    async def get_collection(self) -> pystac.Collection:
        raise NotImplementedError

    @abstractmethod
    async def search_items(
        self,
        bbox: List[float],
        start_date: datetime = None,
        end_date: datetime = None,
        **kwargs
    ) -> ItemCollection:
        """Method searches the satellite scenes for given polygon and optionally
        limited to given date range in the descending order by date.

        Args:
            polygon (List[float]): Bounding box of the region of interest.
            start_date (datetime, optional):  Datetime of start date. Defaults to
                None, the start_date filter isn't used.
            end_date (datetime, optional): Datetime of end date. Defaults to
                None, the end_date filter isn't used.

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError




class Element84Searcher(Searcher):
    COLLECTION_PATTERN = (
        "https://earth-search.aws.element84.com/v0/collections/{}"
    )

    def __init__(self, collection: str):
        self.collection_url = self.COLLECTION_PATTERN.format(collection)
        self.items_url = self.collection_url + "/items"

    async def get_collection(self):
        async with aiohttp.ClientSession() as sess:
            async with sess.get(self.collection_url) as resp:
                a = await resp.json()
                return pystac.Collection.from_dict(a)

    async def _build_parameters(self, bbox, start_date, end_date):
        assert isinstance(
            start_date, (type(None), datetime)
        ), "start_date must be instance of NoneType or datetime"
        assert isinstance(
            end_date, (type(None), datetime)
        ), "end_date must be instance of NoneType or datetime"
        collection = await self.get_collection()
        if not start_date:
            start_date = collection.extent.temporal.intervals[0][0]
        if not end_date:
            end_date = datetime.now()

        parameters = dict(
            bbox=json.dumps(bbox),
            sort=json.dumps([{"field": "datetime", "direction": "desc"},]),
            datetime=f"{start_date.isoformat()}/{end_date.isoformat()}",
        )
        return parameters

    async def search_items(self, bbox, start_date=None, end_date=None, **kwargs):
        parameters = await self._build_parameters(bbox, start_date, end_date, **kwargs)
        async with aiohttp.ClientSession() as sess:
            async with sess.get(self.items_url, params=parameters) as resp:
                if resp.status == 200:
                    return ItemCollection(await resp.json())
                error_text = await resp.text()
                raise Exception(
                    f"Searching {resp.url} returned with error {error_text} and status code {resp.status}"
                )


class Sentinel2L2ASearcher(Element84Searcher):
    def __init__(self):
        super().__init__(collection="sentinel-s2-l2a-cogs")


search_provider = ProviderBase(obj_type=Searcher)
search_provider.register("(sentinel-2, l2a)", Sentinel2L2ASearcher)

