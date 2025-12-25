# BouabidTransfer

**Professional Windows Desktop Application for iPhone to PC Data Transfer**

## Overview

BouabidTransfer is a production-ready Windows desktop application designed to transfer data from iPhone devices to Windows PCs with maximum speed and reliability. The application intelligently combines USB, Wi-Fi, and Bluetooth channels to optimize transfer performance while maintaining data integrity and security.

## Features

- **Multi-Channel Transfer**: Automatically combines USB, Wi-Fi, and Bluetooth for optimal performance
- **Comprehensive File Support**: Photos (HEIC, JPG, PNG, RAW), Videos (MOV, MP4, 4K, HDR), Documents, and more
- **Multiple Destinations**: Internal drives, external USB drives
- **Data Integrity**: Checksum validation, resume interrupted transfers
- **iPhone Compatibility**: iPhone 6 through iPhone 17 Pro Max
- **User-Friendly Interface**: Clean, intuitive UI inspired by professional tools
- **Security & Privacy**: All data stays local, no cloud dependency

## System Requirements

- **Operating System**: Windows 10 or Windows 11
- **Python**: 3.9 or higher
- **USB Port**: For direct device connection
- **Network**: Wi-Fi network (optional, for acceleration)
- **Storage**: Sufficient space on target drive

## Installation

### From Source

1. Clone this repository:
```bash
git clone <repository-url>
cd BouabidTransfer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

### From Installer

Download and run `BouabidTransfer-Setup.exe` to install the application.

## Usage

1. Connect your iPhone to your Windows PC via USB
2. Launch BouabidTransfer
3. Trust the computer on your iPhone when prompted
4. Select the files you want to transfer
5. Choose the destination folder
6. Click "Start Transfer"
7. Monitor progress in real-time

## Architecture

See `docs/ARCHITECTURE.md` for detailed technical documentation.

## Known Limitations

- Requires "Trust This Computer" authorization on iPhone
- Some iCloud-only files may require manual download
- Transfer speed depends on USB cable quality and device model
- iOS security restrictions may limit access to certain system files

## License

[Specify your license here]

## Support

For issues, questions, or contributions, please refer to the project documentation.



