# Dolpa Underwater Technologies - Ground Control Station (GCS)

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green?style=flat&logo=qt)
![Networking](https://img.shields.io/badge/Networking-TCP%2FIP-orange)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)

**Dolpa Underwater Technologies Ground Control Station** is a robust interface software designed to monitor and control underwater vehicles (ROV/AUV). It serves as the primary command center, handling real-time TCP/IP communication, critical system diagnostics, and sensor calibration.

This project demonstrates the implementation of a responsive GUI using **PyQt5**, socket programming for vehicle telemetry, and modular architecture for ease of maintenance.

---

## 📸 Interface Preview

<img width="600" height="400" alt="image" src="https://github.com/user-attachments/assets/a3ba0b57-fd2a-4b56-b043-75ad3d2d9bdd" />


---

## ✨ Key Features

* **Real-Time Communication:** Establishes a stable TCP/IP socket connection with the vehicle to send commands and receive telemetry data.
* **System Diagnostics:**
    * **Leakage Test:** Critical pre-dive safety check module to ensure watertight integrity.
    * **Calibration:** One-click sensor calibration interface for IMU and other navigation sensors.
* **Responsive GUI:** Built with PyQt5, featuring a dynamic layout that adapts to different screen resolutions and window sizes.
* **Web Integration:** Embedded `QtWebEngine` for displaying map data or IP camera streams directly within the dashboard.
* **Configurable Architecture:** Uses `config.json` for dynamic IP addressing, port management, and UI scaling without code modification.

---

## 🛠️ Installation & Setup

To run this project locally, ensure you have Python 3 installed.

### 1. Clone the Repository
```bash
git clone [https://github.com/selmanmisen/Dolpa-Underwater-Tecnologies.git](https://github.com/selmanmisen/Dolpa-Underwater-Tecnologies.git)
cd Dolpa-Underwater-Tecnologies
```

## 2. Install requirements
```bash
pip install -r requirements.txt
```
