#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

current_version = "1.8.2"

requirements = [
    "confapp",
    "pyserial",
    "logging-bootstrap",
    "python-dateutil",
    "safe-and-collaborative-architecture"
]

setup(
    name="pybpod-api",
    version=current_version,
    description="""BPod Python API""",
    author=[
        "Joshua Sanders",
        "Carlos Mão de Ferro",
        "Ricardo Ribeiro",
        "Luís Teixeira",
        "Mohamed Elgohary"
    ],
    author_email="joshua21@gmail.com, cajomferro@gmail.com, ricardojvr@gmail.com, micboucinha@gmail.com",
    license="MIT",
    url="https://github.com/pybpod/pybpod-api",
    include_package_data=True,
    packages=find_packages(
        exclude=["contrib", "docs", "tests", "examples", "deploy", "reports"]
    ),
    install_requires=requirements,
)
