#!/bin/sh

set -e

mkdir -p /airspy/data

if [ ! -f /airspy/data/spyserver.config ]; then
  cp /airspy/spyserver.config /airspy/data/spyserver.config
fi

exec stdbuf -oL ./spyserver ./data/spyserver.config 2>&1 | tee /var/log/spyserver.log
