from .downloader import Downloader
from .provider import ProviderBase
import numpy as np
import numpy.ma as ma


class Calculator:
    AVAILABLE_OPERATIONS = {}

    def __init__(self, downloader: Downloader):
        self._downloader = downloader

    @property
    def downloader(self) -> Downloader:
        """Downloader instance to be used by calculator while performing computation

        Returns:
            Downloader: downloader instance.
        """
        return self._downloader

    @property
    def operations(self):
        """List of all the supported operations

        Returns:
            List[str]: list of all supported operations
        """
        return list(self.AVAILABLE_OPERATIONS.keys())

    async def compute(self, name: str, *args, **kwargs):
        """Applies the operation with name `name` on the data accessible via downloader.

        Args:
            name (str): name of the operation

        Returns:
            [type]: Output of operation, ideally numpy array
        """
        assert (
            name in self.operations
        ), f"Operation {name} is not implemented yet"
        operation = self.AVAILABLE_OPERATIONS.get(name)
        return await getattr(self, operation)(*args, **kwargs)


class Sentinel2Calculator(Calculator):
    AVAILABLE_OPERATIONS = {"ndvi": "_ndvi", "ndwi": "_ndwi"}

    async def _ndvi(self, eps=1e-6, gjson=None):
        red, nir = await self.downloader.download(["B04", "B08"], gjson=gjson)
        ndvi = (nir - red) / (nir + red + eps)
        ndvi[ndvi > 1] = 1
        ndvi[ndvi < -1] = -1
        return ndvi

    async def _ndwi(self, eps=1e-6, gjson=None):
        green, nir = await self.downloader.download(["B03", "B08"], gjson=gjson)
        ndwi = (green - nir) / (green + nir + eps)
        ndwi[ndwi > 1] = 1
        ndwi[ndwi < -1] = -1
        return ndwi


calculation_provider = ProviderBase(obj_type=Calculator)
calculation_provider.register("sentinel-2_l2a", Sentinel2Calculator)


def generate_statistics(array: np.ndarray):
    """Method to generate statistics from numpy array

    Args:
        array (np.ndarray): input array

    Returns:
        dict: Statistics of the array
    """
    return dict(mean=array.mean(), std=array.std(), median=ma.median(array))
