from setuptools import find_packages, setup

setup(
    name="src",
    version="0.0.1",
    author="Sofija, Grace, Hamish, Thomas",
    author_email="author@example.com",
    description="This repository containts the code for the AI4ER Group Team Challenge on wildfire prediciton. ",
    url="url-to-github-page",
    packages=find_packages(),
    test_suite="src.tests.test_all.suite",
)
