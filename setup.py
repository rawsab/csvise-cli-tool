from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="csvise",
    version = "1.2.2",
    author="Rawsab Said",
    description="CLI Tools for Tabular Data - CSV analysis, validation, and beautiful display",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rawsabsaid/csvise-cli-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Filters",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "csvise=csvtools:main",
        ],
    },
    keywords="csv, cli, data-analysis, validation, table, rich, formatting",
    project_urls={
        "Bug Reports": "https://github.com/rawsabsaid/csvise-cli-tool/issues",
        "Source": "https://github.com/rawsabsaid/csvise-cli-tool",
    },
)
