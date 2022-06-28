from setuptools import setup, find_packages
VERSION = '0.0.2'

setup(
   name='management_client',
   version=VERSION,
   license="MIT",
   description="",
   author="UKP",
   packages=find_packages(
        exclude=("tests", ".gitignore", "requirements.dev.txt", "pytest.ini")
    ),
   install_requires=[
       "square-auth>=0.0.3",
       "asyncio",
       "aiohttp==3.8.1",
       "requests==2.27.1"
   ],
)
