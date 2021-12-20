from setuptools import setup


setup(
    name="square-data-cli",
    version="0.1.0",
    author="UKP SQuARE",
    description="Client tools for the SQuARE Datastore API.",
    packages=["square_data_cli"],
    install_requires=[
        "adapter-transformers == 2.2.0",
        "h5py == 3.3.0",
        "numpy == 1.21.0",
        "requests == 2.25.1",
        "tqdm == 4.61.1",
    ],
    entry_points={
        "console_scripts": [
            "square-data-cli=square_data_cli:main",
        ]
    },
    python_requires=">=3.6.0",
)
