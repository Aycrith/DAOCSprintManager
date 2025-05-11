"""Setup script for the daoc_sprint_manager package."""

from setuptools import setup, find_packages

setup(
    name="daoc_sprint_manager",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "opencv-python>=4.11.0",
        "pillow>=11.2.0",
        "numpy>=2.1.0",
        "tqdm>=4.67.0",
        "onnxruntime>=1.15.0",
    ],
    python_requires=">=3.8",
) 