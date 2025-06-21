FROM tailscale/tailscale:latest

# Install additional tools
RUN apk add --no-cache \
    curl \
    iptables \
    iproute2 \
    bash

# Create tailscale directory
RUN mkdir -p /var/lib/tailscale

# Copy configuration script
COPY scripts/tailscale-init.sh /usr/local/bin/tailscale-init.sh
RUN chmod +x /usr/local/bin/tailscale-init.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD tailscale status --json | grep -q '"BackendState":"Running"' || exit 1

# Expose Tailscale port
EXPOSE 41641/udp

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/tailscale-init.sh"]

