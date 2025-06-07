#!/bin/bash

# AirSpy SDR Setup Script.
# Compatible with standard AirSpy (R2, Mini) and SoapySDR integration.

set -e

echo "Installing dependencies..."

sudo apt update

sudo apt install -y build-essential cmake git libtool libudev-dev libusb-1.0-0-dev pkg-config

echo "Building and installing AirSpy library from source..."

git clone --depth=1 https://github.com/airspy/airspyone_host.git

cd airspyone_host

mkdir build && cd build

cmake ..

make -j$(nproc)

sudo make install

sudo ldconfig

cd ../..

rm -rf airspyone_host

echo "Building and installing SoapyAirspy from source for SoapySDR integration..."

git clone --depth=1 https://github.com/pothosware/SoapyAirspy.git

cd SoapyAirspy

mkdir build && cd build

cmake ..

make -j$(nproc)

sudo make install

sudo ldconfig

cd ../..

rm -rf SoapyAirspy

echo "To verify the installation, run the following command:"
echo "airspy_info"
echo "You can also run the following command to test SoapyAirspy functionality:"
echo "SoapySDRUtil --find=airspy"

echo "Installation complete!"
