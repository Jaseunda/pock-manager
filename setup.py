from setuptools import setup, find_packages

setup(
    name="pockage",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "tqdm",
    ],
    entry_points={
        "console_scripts": [
            "pockage=pockage.cli:main",
            "poc=pockage.cli:main",
        ],
    },
    author="JASENUNDA",
    author_email="your.email@example.com",
    description="Simple Modern C++ Package Manager",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Jaseunda/pockage",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
)