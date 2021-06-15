import pytest
from SIEP.provider import ProviderBase
from SIEP.searcher import Sentinel2L2ASearcher, Searcher


@pytest.fixture
def provider():
	return ProviderBase(obj_type=Searcher)

def test_search_provider(provider):
    provider.register("S2L2A", Sentinel2L2ASearcher)
    assert provider.get("S2L2A") == Sentinel2L2ASearcher
    assert provider.names == ['S2L2A']    
    provider.deregister("S2L2A")
    with pytest.raises(ValueError):
        ex = provider.get("S2L2A")

    class TestExplorer:
        pass

    with pytest.raises(AssertionError):
        provider.register("TestFail", TestExplorer)
