#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Install system packages..."
sudo apt update
sudo apt install -y python3-venv python3-pip libusb-1.0-0

echo "Create virtual environment..."
python3 -m venv "$PROJECT_DIR/.venv"

echo "Install Python packages..."
"$PROJECT_DIR/.venv/bin/pip" install --upgrade pip
"$PROJECT_DIR/.venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

echo "Setup completed."