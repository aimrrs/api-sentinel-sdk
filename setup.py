from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="api-sentinel-sdk",
    version="0.1.0",
    author="aimrrs",
    author_email="aimrrs404@gmail.com",
    description="A lightweight SDK for real-time API cost monitoring and control.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aimrrs/api-sentinel-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/aimrrs/api-sentinel-sdk/issues",
        "Documentation": "https://github.com/aimrrs/api-sentinel-sdk#readme",
        "Source Code": "https://github.com/aimrrs/api-sentinel-sdk",
    },
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "openai>=1.0.0",
        "tiktoken>=0.3.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="api monitoring sdk sentinel cost tracking openai",
    python_requires='>=3.8',
    include_package_data=True,
    license="MIT",
    license_files=["LICENSE"],
)