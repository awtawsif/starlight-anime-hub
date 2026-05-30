from setuptools import setup, find_packages

setup(
    name="starlight-anime-hub",
    version="1.2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0",
        "rich>=13.0",
        "requests>=2.32",
        "beautifulsoup4>=4.13",
        "lxml>=6.0",
        "curl_cffi>=0.15.0",
    ],
    entry_points={
        "console_scripts": [
            "starlight=starlight_cli.cli:cli",
        ],
    },
)
