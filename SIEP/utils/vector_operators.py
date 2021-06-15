import geojson
from geojson.feature import Feature, FeatureCollection
from shapely.geometry import shape
from copy import deepcopy
from pyproj import Transformer

def get_feature_bounds(feature: Feature):
    assert isinstance(
        feature, Feature
    ), "Instance of geojson.feature.Feature expected"
    return shape(feature.geometry).bounds


def get_feature_collection_bound(featurecollection: FeatureCollection):
    assert isinstance(
        featurecollection, FeatureCollection
    ), "Instance of geojson.feature.FeatureCollection expected"
    bounds = [None, None, None, None]
    for feature in featurecollection.features:
        x_min, y_min, x_max, y_max = get_feature_bounds(feature)
        if not bounds[0] or x_min < bounds[0]:
            bounds[0] = x_min
        if not bounds[1] or y_min < bounds[1]:
            bounds[1] = y_min
        if not bounds[2] or x_max > bounds[2]:
            bounds[2] = x_max
        if not bounds[3] or y_max > bounds[3]:
            bounds[3] = y_max
    return tuple(bounds)


def get_bound(gjson: geojson):
    assert isinstance(
        gjson, (FeatureCollection, Feature)
    ), "Only geojson is supported at the moment"
    assert gjson.is_valid, "Geojson isn't valid"
    if isinstance(gjson, Feature):
        return get_feature_bounds(gjson)
    return get_feature_collection_bound(gjson)


def transform(gjson:geojson, from_epsg, to_epsg):
    # TODO: It's only for polygon
    assert isinstance(
        gjson, (FeatureCollection, Feature)
    ), "Instance of geojson.feature.FeatureCollection expected"
    gjson = deepcopy(gjson)
    
    transformer = Transformer.from_crs(from_epsg, to_epsg, always_xy=True)
    for feature in gjson.features:
        coordinates = []
        for envelope in feature.geometry.coordinates:
            envelopes = []
            for coordinate in envelope:
                envelopes.append(list(transformer.transform(*coordinate)))
            coordinates.append(envelopes)
        feature["geometry"]["coordinates"] = coordinates
    return gjson