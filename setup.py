from setuptools import setup, find_packages

setup(
    name="siep",
    version="0.0.1",
    author="Abhishek Manandhar",
    author_email="abheeman@hey.com",
    install_requires=[
        "aiohttp=3.7.4",
        "rasterio=1.2.4",
        "pystac=0.5.6",
        "shapely=1.7.1.1",
    ],
    test_requires=["pytest=6.2.4", "pytest-asyncio=0.15.1"],
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    include_package_data=True,
    platform="any",
    entry_points={"console_scripts": ["siep=SIEP.script:main_sync"]},
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules ",
    ],
)

