# SDR Hub

A solution for deploying and managing a Software Defined Radio (SDR) server station. It integrates essential services for control, monitoring, and diagnostics, facilitating efficient SDR server operations.

**Core Features:**

| Service  | Description                       | URL                        |
| -------- | --------------------------------- | -------------------------- |
| AirSpy   | The AirSpy SDR server.            | sdr://localhost:5555       |
| Homepage | Customizable dashboard interface. | https://sdrhub.xyz         |
| Glances  | Real-time system monitoring.      | https://glances.sdrhub.xyz |
| Dozzle   | Real-time Docker log viewer.      | https://dozzle.sdrhub.xyz  |
| Ntfy     | Real-time notification service.   | https://ntfy.sdrhub.xyz    |

## Getting Started

First, make a copy of the `.env.template` file and rename it to `.env`. Then, update any values as needed.

```sh
cp .env.template .env
```

After the update, modify the newly created `.env` file by adjusting the environment variable values accordingly.

### Installation

To set up the required systemd services and complete additional configurations, simply run the following command:

```sh
./install.sh
```

Then, start the project using the commands below.

```sh
./start.sh
```

#### Optional

To stop the Docker containers, just run the following command.

```sh
# Stops any previous run.
./stop.sh

# Optional: Prune all unused resources from the system.
./stop.sh --prune
```

## Supported SDR Hardwares

SDR Hub currently supports multiple SDR hardware interfaces, with primary integration for AirSpy devices. The architecture allows for extension to additional SDR platforms as required.

### AirSpy Target Platforms

The AirSpy server is compatible with the following Linux architectures:

| Platform     | Architecture Description          | Common Use Cases                                   |
| ------------ | --------------------------------- | -------------------------------------------------- |
| linux/amd64  | 64-bit x86 architecture           | Desktops, laptops, servers with Intel/AMD CPUs.    |
| linux/arm64  | 64-bit ARM architecture (AARCH64) | Raspberry Pi 4+, ARM servers, Apple M1/M2/M3 Macs. |
| linux/arm/v7 | 32-bit ARM architecture (ARMv7)   | Raspberry Pi 2/3, older embedded ARM devices.      |

You can set the target platform by modifying the `AIRSPY_TARGET_PLATFORM` environment variable in the `.env` file.

## Project Status

This project is currently under development and is not considered stable.

## License

MIT
