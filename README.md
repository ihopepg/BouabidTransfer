# 📱 BouabidTransfer 🚀

**BouabidTransfer** is a production-grade Windows desktop application designed for ultra-fast, reliable data transfer from iPhones to PC. Built with Python and PyQt6, it bypasses the bloat of iTunes to provide a direct, secure bridge for your photos, videos, and documents.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-lightgrey)

---

## ✨ Key Features

* **⚡ Dual-Channel Speed:** Optimized for **USB 3.0** (Primary) and **Local Wi-Fi** acceleration. 
* **📂 Multi-Format Support:** Transfer Photos (HEIC, RAW, JPG), Videos (4K, HDR, MOV), and Documents without quality loss.
* **🛡️ Privacy First:** 100% Local. No cloud dependency, no data tracking, and no internet required for transfers.
* **🔄 Zero-Freeze UI:** Fully asynchronous engine ensures the interface remains responsive even during 20GB+ transfers.
* **✅ Data Integrity:** Real-time SHA-256 checksum validation to ensure files are never corrupted.

---

## 🛠️ Architecture

The app uses a modular **Layered Architecture**:
1.  **UI Layer:** Built with **PyQt6** for a modern, hardware-accelerated experience.
2.  **Core Engine:** A custom threading manager handling chunked data streams.
3.  **Protocol Layer:** Leverages `pymobiledevice3` for native Apple Mobile Device Service (AMDS) communication.

---

## 🚀 Getting Started

### Prerequisites
- Windows 10 or 11
- Python 3.11 or higher
- [iTunes](https://www.apple.com/itunes/) installed (for Apple Mobile Device Drivers)

### Installation
1. **Clone the repository**
   ```bash
   git clone [https://github.com/YourUsername/BouabidTransfer.git](https://github.com/YourUsername/BouabidTransfer.git)
   cd BouabidTransfer
