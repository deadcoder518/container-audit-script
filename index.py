#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys

RISKY_HOST_PATHS = {
    "/",
    "/var/run/docker.sock",
}

def run(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
    if result.returncode != 0:
            raise subprocess.CalledProcessError(result.stderr.strip())
    return result

def docker_inspect_container(containerid):
    command = ["docker", "inspect", containerid]

    result = run(command)

    data = json.loads(result.stdout)
    return data[0]

def get_container_capabilities(info):
    command = ["docker", "exec", info["Id"], "cat", "/proc/1/status"]

    pid = info.get("State", {}).get("Pid", 0)

    if not pid:
        return None

    result = run(command)

    caps = {}

    for line in result.stdout.splitlines():
        if line.startswith("Cap"):
            key, value = line.split(":", 1)
            caps[key] = value.strip()

    return caps


def get_kernel_version():
    command = ["uname", "-r"]

    result = run(command)

    return result.stdout.strip()


def report(info):
    config = info.get("Config", {})
    host = info.get("HostConfig", {})

    print("\n========== DOCKER SECURITY REPORT ==========")
    print(f"Target: {info.get('Name', info.get('Id', 'Unknown'))}")
    print(f"Type: {'Container'}")

    user = config.get("User") or "root (default)"
    print(f"\n[USER]")
    print(f"Configured user: {user}")

    print("\n[PRIVILEGED]")
    privileged = host.get("Privileged", False)
    print(f"Privileged: {privileged}")

    if privileged:
        print("WARNING: Container has privileged mode enabled!")

    print("\n[CONFIGURED CAPABILITIES]")
    print(f"CapAdd: {host.get('CapAdd') or []}")
    print(f"CapDrop: {host.get('CapDrop') or []}")

    caps = get_container_capabilities(info)
    
    print("\n[PROCESS CAPABILITIES]")

    if caps is None:
        print("Unavailable (container not running or exec failed)")
    else:
        for key, value in caps.items():
            print(f"{key}: {value}")

    print("\n[MOUNTS]")

    mounts = info.get("Mounts", [])

    if not mounts:
        print("No mounts found.")

    for mount in mounts:
        source = mount.get("Source", "")
        destination = mount.get("Destination", "")
        mode = mount.get("Mode", "")
        rw = mount.get("RW", False)

        risky = (
            source in RISKY_HOST_PATHS
            or source.startswith("/var/run/docker.sock")
        )

        print(f"\nSource:      {source}")
        print(f"Destination: {destination}")
        print(f"Mode:        {mode}")
        print(f"Read/Write:  {rw}")

        if risky:
            print("WARNING: SENSITIVE HOST PATH MOUNT!")
        elif source.startswith("/"):
            print("Host path bind mount: YES")

    print("\n[KERNEL]")
    print(f"Host kernel: {get_kernel_version()}")

    print("\n============================================")


def main():
    parser = argparse.ArgumentParser(
        description="Docker container/image security inspector"
    )

    parser.add_argument(
        "target",
        help="Container name/ID"
    )

    args = parser.parse_args()

    try:
        info = docker_inspect_container(args.target, args.image)
        report(info, args.image)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
