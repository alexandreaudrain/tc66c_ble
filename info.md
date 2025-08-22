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

## 🧪 Requirements

- A TC66C USB multimeter with BLE enabled
- Home Assistant running on a system with Bluetooth support

## 🧾 Notes

> ✅ This integration has been successfully tested with **Home Assistant OS (HAOS)** running on a **Raspberry Pi 5**.

## 👨‍💻 Maintainer

Developed and maintained by [@alexandreaudrain](https://github.com/alexandreaudrain)

---
