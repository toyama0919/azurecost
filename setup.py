from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
install_requires = [
    "tabulate",
    "click>=7.0",
    "azure-identity",
    "azure-mgmt-core",
    "azure-mgmt-costmanagement",
    "azure-mgmt-resource",
]
extras_require = {"test": ["tox"]}

setup(
    name="azurecost",
    version="0.1.8",
    description="Simple and easy command line to view azure costs.",
    long_description=open(os.path.join(here, "README.md")).read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="azure cost tool costmanagement",
    author="Hiroshi Toyama",
    author_email="toyama0919@gmail.com",
    url="https://github.com/toyama0919/azurecost",
    license="MIT",
    packages=find_packages("src", exclude=["tests"]),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=extras_require["test"],
    entry_points={"console_scripts": ["azurecost=azurecost.commands:main"]},
)
