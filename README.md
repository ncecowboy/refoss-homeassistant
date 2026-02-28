[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Refoss LAN
Local-network control of Refoss smart devices for Home Assistant — no cloud required.

- **Home Assistant version required**: 2025.2.5 or above

## Supported device models

### New Open API devices (firmware-based RPC protocol)

These devices are discovered automatically by probing `http://<device-ip>/rpc/Refoss.DeviceInfo.Get`.
No UDP broadcast is required.

| Model | Description | Entities |
|-------|-------------|----------|
| `R11` | Smart Wi-Fi Relay Switch (1 channel) | Switch, Power, Voltage, Current, Monthly Energy |
| `R21` | Smart Wi-Fi Dual Relay Switch (2 channels) | Switch ×2, Power ×2, Voltage ×2, Current ×2, Monthly Energy ×2 |
| `P11S` | Smart Wi-Fi Plug | Switch, Power, Voltage, Current, Monthly Energy |
| `EM06P` | Smart Wi-Fi Power Energy Monitor (6 channel) | Power, Voltage, Current, Power Factor, Monthly Energy — per channel |
| `EM16P` | Smart Wi-Fi Power Energy Monitor (16 channel) | Power, Voltage, Current, Power Factor, Monthly Energy — per channel |

### Legacy LAN devices (Meross-style protocol)

These devices are discovered via UDP broadcast on ports 9988/9989.

| Model | Description | Version required |
|-------|-------------|-----------------|
| `R10` | Smart Wi-Fi Switch | all |
| `EM06` | Smart Energy Monitor (6 channel) | v2.3.8 and above |
| `EM16` | Smart Energy Monitor (16 channel) | v3.1.7 and above |

## Installation

You can install this component in two ways: via HACS or manually.
HACS is a community-maintained component manager that allows you to install GitHub-hosted integrations in a few clicks.

### Option A: Installing via HACS (recommended)
If you have HACS installed, just search for **"Refoss LAN"** in the HACS Integrations section and click **Install**.
When the installation completes, **you must restart Home Assistant** before the integration becomes available.

### Option B: Manual installation (custom_component)
1. Download the latest zip release archive from [here](https://github.com/Refoss/refoss-homeassistant/releases/latest).
2. Unzip and copy the `refoss_lan` directory into the `custom_components` directory of your Home Assistant configuration folder.
   The configuration directory is usually `~/.homeassistant/` and contains your `configuration.yaml`.
   After a correct installation the directory tree should look like this:
    ```
    └── ...
    └── configuration.yaml
    └── secrets.yaml
    └── custom_components
        └── refoss_lan
            └── __init__.py
            └── entity.py
            └── switch.py
            └── sensor.py
            └── ...
    ```
   > **Note**: if the `custom_components` directory does not exist, create it first.

3. Restart Home Assistant.

## Configuration

Before adding a device, make sure it is connected to your Wi-Fi network and that Home Assistant can reach it by IP address.

- In the HA UI go to **Settings → Devices & Services**, click **+ Add Integration**, search for **"Refoss LAN"**, and follow the prompts.
- Or click here: [![Start Config Flow](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=refoss_lan)

You will be asked for:
| Field | Description |
|-------|-------------|
| **Host** | The local IP address (or hostname) of the Refoss device |
| **Update interval (seconds)** | How often Home Assistant polls the device for state changes (default: 10 s) |

The integration automatically detects whether the device uses the new Open API (RPC) or the legacy LAN protocol and configures itself accordingly.

## Tips
- **Home Assistant and the device must be on the same local network.**
- **VMware HAOS**: set the virtual machine network adapter to **Bridged** mode.
- **Docker**: run the Home Assistant container with `--network host`.
- **Refoss LAN** and the built-in **Refoss** cloud integration cannot be used at the same time for the same device. If you plan to use Refoss LAN, remove the Refoss cloud integration entry first.
- To reconfigure an existing entry (e.g. after the device gets a new IP), go to **Settings → Devices & Services**, find the device, click the three-dot menu and choose **Reconfigure**.
