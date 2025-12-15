#!/bin/bash
# driver-test.sh
# Complete driver testing with both Bochs and QEMU

set -e

echo "=============================================="
echo "Network Driver Testing Suite"
echo "=============================================="

# Start the unified responder
echo "[1/4] Starting Unified Network Responder..."
python3 unified-responder.py --udp-port 6969 --tcp-port 6969 &
RESPONDER_PID=$!
sleep 2

echo "[2/4] Starting socket listener for QEMU NIC2..."
# Start socket listener for QEMU's second NIC
nc -l -k -p 5555 > /dev/null &
SOCKET_PID=$!

# Function to clean up
cleanup() {
    echo ""
    echo "Cleaning up..."
    kill $RESPONDER_PID 2>/dev/null
    kill $SOCKET_PID 2>/dev/null
    exit 0
}
trap cleanup INT TERM

echo "[3/4] Choose emulator to test:"
echo "  1) Bochs with SLiRP"
echo "  2) QEMU with multiple NICs"
echo "  3) Both (sequential)"
echo ""
read -p "Selection [1-3]: " choice

case $choice in
    1)
        echo "Starting Bochs with SLiRP..."
        bochs -q -f bochs-slirp.conf
        ;;
    2)
        echo "Starting QEMU with multiple NICs..."
        ./qemu-multi-nic.sh
        ;;
    3)
        echo "First: Bochs with SLiRP..."
        bochs -q -f bochs-slirp.conf
        echo ""
        echo "Now: QEMU with multiple NICs..."
        ./qemu-multi-nic.sh
        ;;
    *)
        echo "Invalid choice"
        ;;
esac

cleanup
