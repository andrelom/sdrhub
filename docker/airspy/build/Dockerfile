#
# Build

FROM ubuntu:latest AS build

ARG AIRSPY_TARGET_PLATFORM

WORKDIR /airspy

RUN apt-get update && apt-get install -y wget

RUN set -ex; \
  if [ "$AIRSPY_TARGET_PLATFORM" = "linux/amd64" ]; then \
  URL="https://airspy.com/downloads/spyserver-linux-x64.tgz"; \
  elif [ "$AIRSPY_TARGET_PLATFORM" = "linux/arm64" ]; then \
  URL="https://airspy.com/downloads/spyserver-arm64.tgz"; \
  elif [ "$AIRSPY_TARGET_PLATFORM" = "linux/arm/v7" ]; then \
  URL="https://airspy.com/downloads/spyserver-arm32.tgz"; \
  else \
  echo "Unsupported AirSpy Target Platform: $AIRSPY_TARGET_PLATFORM"; \
  exit 1; \
  fi; \
  wget -O spyserver.tgz "$URL"; \
  tar xvzf spyserver.tgz;

RUN set -ex; \
  sed -i "s/^bind_port = .*/bind_port = 5555/" spyserver.config

#
# Main

FROM ubuntu:latest AS main

WORKDIR /airspy

COPY entrypoint.sh /airspy/entrypoint.sh

COPY --from=build /airspy/spyserver /airspy/spyserver
COPY --from=build /airspy/spyserver.config /airspy/spyserver.config

RUN apt-get update && \
  apt-get install -y rtl-sdr librtlsdr-dev && \
  apt-get clean && rm -rf /var/lib/apt/lists/* && \
  chmod +x /airspy/entrypoint.sh

CMD ["/airspy/entrypoint.sh"]
