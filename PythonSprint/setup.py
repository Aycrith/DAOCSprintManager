"""
DAOC Sprint Manager setup configuration.
"""

from setuptools import setup, find_packages

setup(
    name="daoc-sprint-manager",
    version="1.0.0",
    description="A system tray application for managing sprint detection in Dark Age of Camelot using ML",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "pystray>=0.19.4",
        "Pillow>=10.0.0",
        "pydantic>=2.0.0",
        "psutil>=5.9.0",
        "numpy>=1.24.0",
        "opencv-python>=4.8.0",
        "onnxruntime>=1.16.0",
        "torch>=2.1.0",
        "torchvision>=0.16.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pyinstaller>=6.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
        ],
        "train": [
            "torch>=2.1.0",
            "torchvision>=0.16.0",
            "tensorboard>=2.15.0",
            "scikit-learn>=1.3.0",
            "matplotlib>=3.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "daoc-sprint-manager=daoc_sprint_manager.main:main",
        ],
    },
    package_data={
        "daoc_sprint_manager": [
            "models/*.onnx",
            "models/model_versions.json",
            "models/model_metadata.json",
            "config/*.json",
            "assets/*.png",
            "assets/*.ico",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
) 