# Tor hidden service (Docker)

Serve `website/index.html` as a Tor hidden service (.onion). No Tor installation on the host—everything runs in Docker.

## Quick start

```bash
docker compose up -d --build
```

After Tor has connected (usually 1–2 minutes), get your .onion address:

```bash
docker exec tor-website-tor cat /var/lib/tor/hidden_service/hostname
```

Open that address in **Tor Browser** to view your site.

## Layout

| Path | Purpose |
|------|--------|
| `website/` | Static files (e.g. `index.html`) served by Nginx |
| `config/torrc` | Tor config: hidden service, bridges, logging |
| `config/nginx.conf` | Nginx vhost for the site |
| `docker-compose.yml` | Nginx + Tor services |
| `Dockerfile.tor` | Tor image with obfs4proxy for bridges |

## Config

- **Tor**: Edit `config/torrc` and restart: `docker compose restart tor`
- **Site**: Change files in `website/`; Nginx serves them as-is (no restart needed for static files).
- **Bridges**: The two obfs4 bridges from bridges@torproject.org are in `config/torrc`. If your server can reach Tor without them, comment out `UseBridges 1`, the `ClientTransportPlugin` line, and the `Bridge` lines to use a direct connection.

## Commands

```bash
# Start
docker compose up -d --build

# View Tor logs
docker compose logs -f tor

# View Nginx logs
docker compose logs -f nginx

# Show .onion hostname
docker exec tor-website-tor cat /var/lib/tor/hidden_service/hostname

# Stop
docker compose down
```

## Notes

- The .onion address is created on first run and stored in the `tor-data` volume. Same address is reused as long as the volume exists.
- Access the site only via Tor Browser (or another Tor client) using the printed .onion URL; there is no public HTTP port on the host.
