## Satellite Image Explorer and Processor (SIEP)

SIEP allows users to search satellite scenes with specific filtering criteria and use the scenes with the processors to make the mathematical computations for scientific purposes.

SIEP is an extendable system that currently has implementations for the L2A product of Sentinel-2. It uses API built with STAC specification (for now Element84 API only) for searching and currently calculates NDVI, NDWI, and the general statistics of those indices.

### Use Cases

Users can use the tool to compute NDVI, NDWI and generate statics of those indices. The NDVI allows users to monitor vegetation, while NDWI enables users to monitor water content. These indices could be used separately or in conjunction for different applications such as flood detection, deforestation detection, vegetation health, etc.

### Installation and Using Tool

The tool has been tested in python 3.9, therefore it's advisable. However the libraries used should also work with python 3.6 onwards. The tool can be installed by directly installing this package via pip as follows:

```bash
>> pip install git+ssh://git@github.com:Geosynopsis/SatProcessor.git
```

or if you would like to make use of the conda-environment file prepared by author, you could clone and install as follows:

```bash
>> git clone git@github.com:Geosynopsis/SatProcessor.git
>> cd SatProcessor
>> conda env create -f conda-env.yaml
>> conda activate SatProcessor
>> python setup.py install
```

### Using with CLI

Users can use the tool after installation by directly accessing the script or via cli as follows: 

```bash
>> siep -s sentinel-2 -p l2a -g ./doberitzer_heide.geojson -i ndvi -i ndwi
```

### Design Detail

During the system's design, we were mindful of the system's modularity and ease of extension in the future. However, it makes some assumptions that are core to the strategy:

> The search is a client implementation of API with STAC specification. One can integrate another type of API using an adapter that maps the results to the Collection, ItemCollection, Item, and Asset types of STAC.

The system implements consists of three different significant components `Searcher` , `Downloader` , and `Calculator` . Searcher is responsible for search while Downloader for downloading data and Calculator for operations on the data. Since the search, data access model, and operation depend on different factors such as the satellite mission, product type, distribution format of files, etc., separate implementations of those components are developed and provided through factories to limit coupling.

A high level UML diagram of the system looks as such:

![High Level Architecture](high-level-architecture.png)

### Tests

We have tested each component of the system for correct behavior as well as expected exceptions. Please report to us if you see the potential to strengthen the system further.
The test plan we adopted for this system is as follows:

* Unit test each component
* Integration test of whole user interaction flow with different input configurations
