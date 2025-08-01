
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="epw-visualizer",
    version="1.0.0",
    author="EPW Visualizer Team",
    author_email="contact@epwvisualizer.com",
    description="A Python-based weather data visualization tool for analyzing EnergyPlus Weather (EPW) files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/epw-visualizer",
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
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "epw-visualizer=app:main",
        ],
    },
    keywords="weather data visualization epw energyplus streamlit",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/epw-visualizer/issues",
        "Source": "https://github.com/yourusername/epw-visualizer",
        "Documentation": "https://github.com/yourusername/epw-visualizer#readme",
    },
)
