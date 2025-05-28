#!/bin/bash

set -e

# ##################################################
# Shared                                           #
# ##################################################

# Global Variables

SRV_DIR="/srv/sdrhub"
ENV_FILE="${SRV_DIR}/.env"

# Environment Variables

if [ -f "$ENV_FILE" ]; then
  source "$ENV_FILE"
else
  echo "Error: Environment file not found at $ENV_FILE" >&2
  exit 1
fi

# ##################################################
# Setup Systemd Services                           #
# ##################################################

# The directory where systemd service files are stored.
SYSTEMD_DIR="/etc/systemd/system"

if [[ "$EUID" -ne 0 ]]; then
  echo "This script must be run as root. Try: sudo $0"
  exit 1
fi

# This function installs a service by copying the service file,
# making the script executable, and enabling it to start on boot.
systemd() {
  local service_name="$1"
  local service_file="$2"
  local script_file="$3"

  echo "Installing ${service_name}..."

  cp "${service_file}" "${SYSTEMD_DIR}/"

  if [ -n "$script_file" ] && [ -f "$script_file" ]; then
    chmod +x "${script_file}"
  fi

  systemctl daemon-reexec
  systemctl daemon-reload
  systemctl enable "${service_name}"
  systemctl start "${service_name}"

  echo "Checking status of ${service_name}..."

  if ! systemctl is-active --quiet "${service_name}"; then
    echo "Error: ${service_name} failed to start." >&2
    systemctl status "${service_name}"
    exit 1
  else
    echo "The ${service_name} is active."
  fi
}

echo "Starting installation of SDR Hub services..."

systemd \
  "sdrhub-start-docker" \
  "${SRV_DIR}/systemd/sdrhub-start-docker/sdrhub-start-docker.service"

systemd \
  "sdrhub-stop-docker" \
  "${SRV_DIR}/systemd/sdrhub-stop-docker/sdrhub-stop-docker.service"

systemd \
  "sdrhub-ufw-monitor" \
  "${SRV_DIR}/systemd/sdrhub-ufw-monitor/sdrhub-ufw-monitor.service" \
  "${SRV_DIR}/systemd/sdrhub-ufw-monitor/agent.py"

echo "All services installed and running successfully."
