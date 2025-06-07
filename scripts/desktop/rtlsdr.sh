#!/bin/bash

# RTL-SDR Setup Script.
# Compatible with RTL2832U devices and SoapySDR integration.

set -e

echo "Installing dependencies..."

sudo apt update

sudo apt install -y build-essential cmake git libtool libudev-dev libusb-1.0-0-dev pkg-config

echo "Building and installing RTL-SDR from source..."

git clone --depth=1 https://github.com/osmocom/rtl-sdr.git

cd rtl-sdr

mkdir build && cd build

cmake .. -DINSTALL_UDEV_RULES=ON

make -j$(nproc)

sudo make install

sudo ldconfig

sudo cp ../rtl-sdr.rules /etc/udev/rules.d/

sudo udevadm control --reload-rules

sudo udevadm trigger

cd ../..

rm -rf rtl-sdr

echo "Blacklisting DVB-T drivers (optional)..."

echo 'blacklist dvb_usb_rtl28xxu' | sudo tee /etc/modprobe.d/rtl-sdr-blacklist.conf
echo 'blacklist rtl2832' | sudo tee -a /etc/modprobe.d/rtl-sdr-blacklist.conf
echo 'blacklist rtl2830' | sudo tee -a /etc/modprobe.d/rtl-sdr-blacklist.conf

echo "Building and installing SoapyRTL from source for SoapySDR integration..."

git clone --depth=1 https://github.com/pothosware/SoapyRTLSDR.git

cd SoapyRTLSDR

mkdir build && cd build

cmake ..

make -j$(nproc)

sudo make install

sudo ldconfig

cd ../..

rm -rf SoapyRTLSDR

echo "To verify the installation, run the following command:"
echo "rtl_test"
echo "You can also run the following command to test SoapyRTLSDR functionality:"
echo "SoapySDRUtil --find=rtlsdr"

echo "Installation complete!"
