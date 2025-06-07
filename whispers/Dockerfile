# ==============================================
# File: Dockerfile
# ==============================================
FROM python:3.10-slim

ENV PYTHONPATH=/app
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# System dependencies (build + runtime)
RUN apt update && apt install -y --no-install-recommends \
  build-essential cmake git libtool libusb-1.0-0-dev pkg-config \
  python3-dev libpython3-dev python3-numpy swig ffmpeg curl \
  && rm -rf /var/lib/apt/lists/*

# Build SoapySDR manually
RUN git clone https://github.com/pothosware/SoapySDR.git && \
  cd SoapySDR && mkdir build && cd build && \
  cmake .. && make -j$(nproc) && make install && ldconfig && \
  cd /app && rm -rf SoapySDR

# Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY app/ ./app/
COPY web/ ./web/

# Optional: multi-stage optimization for production
# TODO: Use a builder image to keep only runtime deps in final container

# Copia o startup.sh
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh
