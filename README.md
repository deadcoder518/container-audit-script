
# Docker Container Security Auditing Tool

A lightweight Python-based Docker **security auditing** tool - built as a personal project - that inspects container configurations to identify excessive privileges, potentially dangerous Linux capabilities, and insecure host filesystem mounts.

The tool uses Docker's inspection functionality and Python's `subprocess` module to generate a security report highlighting potential container misconfigurations.

## Features

- **Running User:** Identifies the user configured to run inside the container, highlighting when the default root user is used.
- **Privileged Mode:** Checks whether the container has been launched with privileged mode enabled.
- **Linux Capabilities:** Retrieves configured capabilities (`CapAdd` and `CapDrop`) and inspects runtime process capabilities through `/proc/1/status`.
- **Host Mounts:** Inspects mounted volumes and bind mounts, flagging potentially dangerous host paths such as `/` and `/var/run/docker.sock`.
- **Kernel Information:** Retrieves the host's Linux kernel version using `uname -r`.

## Requirements

- Python 3.x
- Docker Engine
- Docker CLI
- Access to the Docker daemon
- A running Docker container for runtime capability inspection

No third-party Python packages are required.

## Installation

Clone the repository:

```bash
git clone https://github.com/deadcoder518/container-audit-script.git
```

Navigate into the project directory:

```bash
cd container-audit-script
```

Ensure Docker is running and accessible:

```bash
docker
```

## Usage

Run the script against a container using its name or container ID:

```bash
python3 index.py <container_name_or_id>
```

For example:

```bash
python3 index.py my-container
```

## Example Security Report

```text
========== DOCKER SECURITY REPORT ==========

Target: /my-container
Type: Container

[USER]
Configured user: root (default)

[PRIVILEGED]
Privileged: False

[CONFIGURED CAPABILITIES]
CapAdd: []
CapDrop: []

[PROCESS CAPABILITIES]
CapInh: 0000000000000000
CapPrm: 00000000a80425fb
CapEff: 00000000a80425fb
CapBnd: 00000000a80425fb
CapAmb: 0000000000000000

[MOUNTS]

Source: /var/run/docker.sock
Destination: /var/run/docker.sock
Read/Write: True
WARNING: SENSITIVE HOST PATH MOUNT!

[KERNEL]
Host kernel: 6.x.x

============================================
```

*Example output for illustrative purposes.*

## Technical Implementation

| Technology | Purpose |
|---|---|
| Python 3 | Core scripting and report generation |
| `subprocess` | Executes Docker CLI and system commands |
| `json` | Parses Docker inspection output |
| `argparse` | Handles command-line arguments |
| `docker inspect` | Retrieves container configuration and security settings |
| `/proc/1/status` | Provides runtime Linux process capability information |
| `uname -r` | Retrieves the host kernel version |

## Limitations

- Host mount warnings currently focus on `/` and `/var/run/docker.sock`; other sensitive host paths may also present security risks.
- The tool provides configuration visibility and security indicators, not a definitive assessment of container exploitability.

## Disclaimer

This tool is only designed for defensive security auditing, helping identify potentially insecure Docker configurations and excessive container privileges.
