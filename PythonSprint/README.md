# DAOC Sprint Manager

A modern system tray application for managing sprint detection in Dark Age of Camelot using machine learning.

## Features

- Intelligent sprint detection using ML model
- System tray interface for easy access
- Automatic game window detection
- Configurable hotkeys and settings
- Low resource usage
- Cross-character support

## System Requirements

- Windows 10 or later
- Python 3.9 or later (for source installation)
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- DirectX 9 compatible graphics card

## Installation

### Method 1: Pre-built Executable (Recommended)

1. Download the latest release from the [Releases](https://github.com/yourusername/daoc-sprint-manager/releases) page
2. Extract the ZIP file to your desired location
3. Run `DAOC Sprint Manager.exe` from the extracted folder

For detailed installation instructions and troubleshooting, see [INSTALLATION.md](docs/INSTALLATION.md).

### Method 2: Installing from Source

#### Prerequisites

1. Install Python 3.9 or later from [python.org](https://python.org) or Anaconda
2. Install Git from [git-scm.com](https://git-scm.com)

#### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/daoc-sprint-manager.git
   cd daoc-sprint-manager
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python src/daoc_sprint_manager/main.py
   ```

For build instructions, see [DISTRIBUTION_GUIDE.md](docs/DISTRIBUTION_GUIDE.md).

## Usage

1. Launch the application
2. Look for the DAOC Sprint Manager icon in your system tray
3. Left-click to toggle sprint detection
4. Right-click for additional options:
   - Configure Settings
   - View Detection Status
   - Check for Updates
   - View Logs
   - Exit

## Configuration

The application creates a configuration directory with default settings:
- Icon detection sensitivity
- Hotkeys
- UI preferences
- Model settings

Edit `config/settings.json` to customize your preferences.

For detailed configuration instructions, see [INSTALLATION.md](docs/INSTALLATION.md).

## Development

### Setup

1. Follow the "Installing from Source" steps above
2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

### Testing

Run the test suite:
```bash
pytest
```

### Building

Create a distributable package:
```bash
python build_exe.py
```

See [DISTRIBUTION_GUIDE.md](docs/DISTRIBUTION_GUIDE.md) for detailed build instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details on our code of conduct and development process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [PyInstaller](https://www.pyinstaller.org/) for executable creation
- [pystray](https://github.com/moses-palmer/pystray) for system tray functionality
- [ONNX Runtime](https://onnxruntime.ai/) for ML model inference
- [OpenCV](https://opencv.org/) for image processing
- [PyTorch](https://pytorch.org/) for ML model training 