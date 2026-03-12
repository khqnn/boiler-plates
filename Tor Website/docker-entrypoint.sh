#!/bin/sh
set -e
# Create hidden service dir if missing (e.g. fresh volume)
mkdir -p /var/lib/tor/hidden_service
# Tor requires strict permissions on HiddenServiceDir (0700)
chown -R debian-tor:debian-tor /var/lib/tor
chmod 700 /var/lib/tor
chmod 700 /var/lib/tor/hidden_service
exec runuser -u debian-tor -- /usr/bin/tor -f /etc/tor/torrc
