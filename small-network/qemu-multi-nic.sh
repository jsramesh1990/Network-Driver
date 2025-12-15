#!/bin/bash
# qemu-multi-nic.sh
# QEMU with multiple NICs using different backends

set -e

echo "Starting QEMU with multiple NIC backends..."
echo "Make sure the Unified Network Responder is running!"
echo ""

# Clean up any previous instances
pkill -f "qemu-system.*" || true

# Start QEMU with multiple NICs
qemu-system-x86_64 \
    -name "Driver-Test-VM" \
    -m 256M \
    -cpu qemu64 \
    -drive format=raw,file=boot.img,if=ide \
    -monitor stdio \
    -serial file:qemu-serial.log \
    \
    # ========================================================================
    # NETWORK CONFIGURATION - Multiple Backends
    # ========================================================================
    \
    # NIC 1: User-mode networking (SLiRP-like) - Connects to UDP responder
    -netdev user,id=net0,hostfwd=udp::6969-:6969 \
    -device e1000,netdev=net0,mac=52:54:00:11:11:11 \
    \
    # NIC 2: Socket backend - Direct connection to responder
    -netdev socket,id=net1,listen=:5555 \
    -device rtl8139,netdev=net1,mac=52:54:00:22:22:22 \
    \
    # NIC 3: Another user backend with different configuration
    -netdev user,id=net2,host=10.0.3.1,dhcpstart=10.0.3.100 \
    -device virtio-net-pci,netdev=net2,mac=52:54:00:33:33:33 \
    \
    # NIC 4: Dummy backend (no external connection)
    -netdev hubport,id=net3,hubid=0 \
    -device e1000,mac=52:54:00:44:44:44,netdev=net3 \
    \
    # Enable network dump for debugging
    -object filter-dump,id=dump0,netdev=net0,file=net0-dump.pcap \
    -object filter-dump,id=dump1,netdev=net1,file=net1-dump.pcap \
    \
    # Additional options
    -no-reboot \
    -nographic

echo ""
echo "QEMU stopped. Network dumps saved to netX-dump.pcap files"
