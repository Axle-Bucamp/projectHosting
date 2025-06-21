#!/bin/bash

set -e

echo "Starting Tailscale VPN Bridge..."

# Check for required environment variables
if [ -z "$TAILSCALE_AUTHKEY" ]; then
    echo "ERROR: TAILSCALE_AUTHKEY environment variable is required"
    exit 1
fi

# Start tailscaled in background
echo "Starting tailscaled daemon..."
tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
TAILSCALED_PID=$!

# Wait for tailscaled to be ready
echo "Waiting for tailscaled to be ready..."
for i in {1..30}; do
    if tailscale status >/dev/null 2>&1; then
        echo "tailscaled is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "ERROR: tailscaled failed to start"
        exit 1
    fi
    sleep 1
done

# Authenticate with Tailscale
echo "Authenticating with Tailscale..."
tailscale up --authkey="$TAILSCALE_AUTHKEY" \
    --hostname="${TAILSCALE_HOSTNAME:-projecthosting-vpn}" \
    --advertise-routes="${TAILSCALE_ROUTES:-10.0.0.0/8,172.16.0.0/12,192.168.0.0/16}" \
    --accept-routes \
    --accept-dns=false \
    --ssh

# Enable IP forwarding
echo "Enabling IP forwarding..."
echo 1 > /proc/sys/net/ipv4/ip_forward
echo 1 > /proc/sys/net/ipv6/conf/all/forwarding

# Configure iptables for forwarding
echo "Configuring iptables..."
iptables -t nat -A POSTROUTING -o tailscale0 -j MASQUERADE
iptables -A FORWARD -i tailscale0 -j ACCEPT
iptables -A FORWARD -o tailscale0 -j ACCEPT

# Configure specific port forwarding for services
if [ -n "$FORWARD_PORTS" ]; then
    echo "Configuring port forwarding: $FORWARD_PORTS"
    IFS=',' read -ra PORTS <<< "$FORWARD_PORTS"
    for port_mapping in "${PORTS[@]}"; do
        IFS=':' read -ra PORT_PARTS <<< "$port_mapping"
        external_port=${PORT_PARTS[0]}
        internal_host=${PORT_PARTS[1]}
        internal_port=${PORT_PARTS[2]}
        
        echo "Forwarding port $external_port to $internal_host:$internal_port"
        iptables -t nat -A PREROUTING -p tcp --dport $external_port -j DNAT --to-destination $internal_host:$internal_port
        iptables -t nat -A PREROUTING -p udp --dport $external_port -j DNAT --to-destination $internal_host:$internal_port
    done
fi

# Get Tailscale IP
TAILSCALE_IP=$(tailscale ip -4)
echo "Tailscale IP: $TAILSCALE_IP"

# Create status endpoint
echo "Creating status endpoint..."
cat > /tmp/vpn-status.sh << 'EOF'
#!/bin/bash
TAILSCALE_STATUS=$(tailscale status --json 2>/dev/null || echo '{"BackendState":"Stopped"}')
TAILSCALE_IP=$(tailscale ip -4 2>/dev/null || echo "unknown")

cat << JSON
{
    "status": "healthy",
    "timestamp": "$(date -Iseconds)",
    "service": "vpn-bridge",
    "tailscale": {
        "ip": "$TAILSCALE_IP",
        "status": $TAILSCALE_STATUS
    },
    "forwarding": {
        "ipv4": $(cat /proc/sys/net/ipv4/ip_forward),
        "ipv6": $(cat /proc/sys/net/ipv6/conf/all/forwarding)
    }
}
JSON
EOF
chmod +x /tmp/vpn-status.sh

# Start simple HTTP server for health checks
echo "Starting health check server..."
while true; do
    echo -e "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n$(/tmp/vpn-status.sh)" | nc -l -p 8080 -q 1
done &

# Monitor tailscaled process
echo "VPN Bridge is ready. Monitoring tailscaled..."
while kill -0 $TAILSCALED_PID 2>/dev/null; do
    sleep 10
    
    # Check if Tailscale is still connected
    if ! tailscale status >/dev/null 2>&1; then
        echo "WARNING: Tailscale connection lost, attempting to reconnect..."
        tailscale up --authkey="$TAILSCALE_AUTHKEY" \
            --hostname="${TAILSCALE_HOSTNAME:-projecthosting-vpn}" \
            --advertise-routes="${TAILSCALE_ROUTES:-10.0.0.0/8,172.16.0.0/12,192.168.0.0/16}" \
            --accept-routes \
            --accept-dns=false \
            --ssh
    fi
done

echo "tailscaled process died, exiting..."
exit 1

