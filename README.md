# TC66C BLE Integration for Home Assistant

This custom integration allows Home Assistant to discover and connect to **TC66C USB multimeter devices** via Bluetooth Low Energy (BLE). Once paired, it exposes a set of real-time sensors for monitoring electrical metrics directly from your TC66C dongle.

## 🔧 Features

- Automatic discovery of TC66C devices over BLE
- Manual device selection via the Home Assistant UI
- Creates the following sensors:
  - `voltage`
  - `current`
  - `power`
  - `resistance`
  - `temperature`
  - `data_plus`
  - `data_minus`

Each sensor updates in real time and can be used in dashboards, automations, or energy monitoring setups.

## 📦 Installation

This integration is compatible with [HACS](https://hacs.xyz), the Home Assistant Community Store.

### Option 1: Add via HACS

Click the button below to add this repository to HACS:

[![Add to Home Assistant](https://img.shields.io/badge/Add%20to%20Home%20Assistant-Install%20with%20HACS-blue?logo=home-assistant&style=for-the-badge)](https://my.home-assistant.io/redirect/hacs_repository/?owner=alexandreaudrain&repository=tc66c_ble&category=integration)

> Replace `<your-github-username>` and `<your-repo-name>` with your actual GitHub info.

### Option 2: Manual Installation

1. Copy this repository into your Home Assistant `custom_components` folder.

2. Restart Home Assistant
3. Go to **Settings > Devices & Services > Add Integration**
4. Search for **TC66 BLE** and follow the setup instructions

## 🧪 Requirements

- A TC66C USB multimeter with BLE enabled
- Home Assistant running on a system with Bluetooth support

## 🧾 Notes

> ✅ This integration has been successfully tested with **Home Assistant OS (HAOS)** running on a **Raspberry Pi 5**.

## 👨‍💻 Maintainer

Developed and maintained by [@alexandreaudrain](https://github.com/alexandreaudrain)

---
