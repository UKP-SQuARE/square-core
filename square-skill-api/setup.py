from setuptools import setup, find_packages

setup(
    name="square_skill_api",
    version="0.0.6",
    description="",
    url="www.informatik.tu-darmstadt.de/ukp",
    author="UKP",
    author_email="baumgaertner@ukp.informatik.tu-darmstadt.de",
    packages=find_packages(),
    install_requires=[
        "uvicorn>=0.15.0",
        "fastapi>=0.65.2",
        "pydantic>=1.8.2",
    ],
)
