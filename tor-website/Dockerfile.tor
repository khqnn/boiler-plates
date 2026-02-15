# Tor with obfs4proxy for bridge support (from bridges@torproject.org)
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tor \
        obfs4proxy \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Ensure tor data directory exists
RUN mkdir -p /var/lib/tor/hidden_service

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
