from setuptools import setup, find_packages

setup(
    name="square_skill_helpers",
    version="0.0.4",    
    description="",
    url="www.informatik.tu-darmstadt.de/ukp",
    author="UKP",
    author_email="baumgaertner@ukp.informatik.tu-darmstadt.de",
    packages=find_packages(),
    install_requires=[
        "requests==2.26.0",
        "numpy==1.21.3",                     
        "python-dotenv==0.19.1",                     
    ],
)
