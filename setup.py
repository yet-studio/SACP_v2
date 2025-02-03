from setuptools import setup, find_packages

setup(
    name="sacp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "plotly>=5.0.0",
        "pandas>=1.0.0",
        "beautifulsoup4>=4.9.0",
        "pyyaml>=5.1",
    ],
    python_requires=">=3.8",
)
