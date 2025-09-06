from setuptools import setup, find_packages

setup(
    name="api-sentinel",
    version="0.1.0",
    author="aimrrs",
    author_email="aimrrs404@gmail.com",
    description="A lightweight SDK for real-time API cost monitoring and control.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aimrrs/api-sentinel-sdk",
    packages=find_packages(),
    install_requires=[
        "requests",
        "openai",
        "tiktoken"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)