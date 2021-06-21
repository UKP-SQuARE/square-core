from setuptools import setup, find_packages

setup(
    name="ElkJsonFormatter",
    version="0.0.1",
    packages=find_packages(include=['ElkJsonFormatter']),
    install_requires=["python-json-logger==2.0.1"]
)
