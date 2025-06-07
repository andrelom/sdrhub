#!/bin/bash

set -e

# SoapySDR Setup Script.
# Compatible with various SDR devices that support SoapySDR.

echo "Installing dependencies..."

sudo apt update

sudo apt install -y cmake g++ git libpython3-dev python3-numpy swig

echo "Building and installing SoapySDR from source..."

git clone https://github.com/pothosware/SoapySDR.git

cd SoapySDR

mkdir -p build && cd build

cmake ..

make -j$(nproc)

sudo make install

sudo ldconfig

echo "To verify the installation, run the following command:"
echo "SoapySDRUtil --info"
echo "You can also run the following command to list available devices:"
echo "SoapySDRUtil --find"

echo "Installation complete!"
