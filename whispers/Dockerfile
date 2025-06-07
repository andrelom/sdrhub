FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# 1. Instala dependências do sistema
RUN apt update && apt install -y --no-install-recommends \
  build-essential cmake git libtool libusb-1.0-0-dev pkg-config \
  python3-dev libpython3-dev python3-numpy swig ffmpeg \
  && rm -rf /var/lib/apt/lists/*

# 2. Instala SoapySDR manualmente
RUN git clone https://github.com/pothosware/SoapySDR.git && \
  cd SoapySDR && mkdir build && cd build && \
  cmake .. && make -j$(nproc) && make install && ldconfig && \
  cd /app && rm -rf SoapySDR

# 3. Instala dependências Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia o código da aplicação
COPY app/ ./app/
COPY web/ ./web/

# (Comando definido pelo docker-compose)
