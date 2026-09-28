"""Setup configuration for SMB3 Randomizer."""
from setuptools import setup, find_packages

setup(
    name="smb3-randomizer",
    version="0.1.0",
    description="A generic ROM-based randomizer framework for Super Mario Bros 3",
    author="cheetahella16-crypto",
    url="https://github.com/cheetahella16-crypto/smb3-randomizer",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
