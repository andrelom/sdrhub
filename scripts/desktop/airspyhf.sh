#!/bin/bash

set -e

echo "Installing dependencies..."

sudo apt update

sudo apt install -y build-essential cmake git libtool libudev-dev libusb-1.0-0-dev pkg-config

echo "Building and installing AirSpy HF+ from source..."

git clone --depth=1 https://github.com/airspy/airspyhf.git

cd airspyhf

mkdir build && cd build

cmake ..

make -j$(nproc)

sudo make install

sudo ldconfig

cd ../..

rm -rf airspyhf

echo "Building and installing SoapyAirspyHF from source for SoapySDR integration..."

git clone --depth=1 https://github.com/pothosware/SoapyAirspyHF.git

cd SoapyAirspyHF

mkdir build && cd build

cmake ..

make -j$(nproc)

sudo make install

sudo ldconfig

cd ../..

rm -rf SoapyAirspyHF

echo "To verify the installation, run the following command:"
echo "airspy_hf --version"
echo "You can also run the following command to test SoapyAirspyHF functionality:"
echo "SoapySDRUtil --find=airspyhf"

echo "Installation complete!"
