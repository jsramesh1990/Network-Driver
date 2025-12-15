Network Driver Test Environment
A comprehensive network listener/responder system for testing network device drivers with BOCHS and QEMU emulators. This project provides a unified testing environment that supports multiple networking backends and protocols.

🌟 Features
Multi-Emulator Support: Works seamlessly with both BOCHS and QEMU

Multiple Networking Backends:

Bochs SLiRP (user-mode networking)

QEMU multiple NICs with different backends

Socket connections for direct testing

Protocol Simulation:

ARP request/response handling

ICMP Ping (Echo request/reply)

DHCP simulation

Custom packet handling

Unified Responder: Single Python script handles all backend types

Debug Tools: Packet capture, logging, and test clients

📁 Project Structure
text
network-driver-test/
├── unified-responder.py    # Main responder application
├── bochs-slirp.conf        # Bochs configuration for SLiRP backend
├── qemu-multi-nic.sh       # QEMU script with multiple NICs
├── driver-test.sh          # Complete test suite
├── Makefile                # Build and test automation
└── README.md               # This file
🚀 Quick Start
Prerequisites
Python 3.6+

BOCHS emulator

QEMU emulator

Root/sudo access (for TAP interfaces)

Installation
Clone/download the project files

Make scripts executable:

bash
chmod +x qemu-multi-nic.sh driver-test.sh
Basic Usage
Start the unified responder:

bash
python3 unified-responder.py
Test with Bochs (SLiRP backend):

bash
make bochs
Test with QEMU (multiple NICs):

bash
make qemu
Run complete test suite:

bash
make full-test
🔧 Configuration
Unified Responder Options
bash
python3 unified-responder.py --help
Options:

--udp-port PORT - UDP port for Bochs SLiRP (default: 6969)

--tcp-port PORT - TCP port for QEMU user-mode (default: 6969)

--gateway IP - Gateway IP to respond as (default: 10.0.2.2)

--test - Run test clients instead of starting server

Bochs Configuration
The bochs-slirp.conf file configures:

NE2000 NIC at I/O address 0x300, IRQ 9

SLiRP user-mode networking backend

32MB RAM, single CPU core

Disk image: boot.img

QEMU Configuration
The qemu-multi-nic.sh script sets up:

NIC 1: User-mode networking (connects to UDP responder)

NIC 2: Socket backend (port 5555)

NIC 3: User backend with different subnet

NIC 4: Dummy hubport backend

Network packet capture to .pcap files

🧪 Testing Your Driver
Network Configuration for Your OS
For Bochs/SLiRP:

IP: 10.0.2.15

Gateway: 10.0.2.2

DNS: 10.0.2.3

Subnet: 255.255.255.0

For QEMU NIC1 (user-mode):

Auto-configured by QEMU

Connects to responder on port 6969

Test Packets
The responder handles various test packets:

ARP Test:

python
# Send ARP request
packet = b'TEST_ARP_REQUEST'
Ping Test:

python
# Send ICMP Echo Request
packet = b'TEST_PING_REQUEST'
Echo Test:

python
# Simple echo (responds with same data)
packet = b'Hello from driver!'
HTTP Test:

python
# Test TCP connections
packet = b'GET / HTTP/1.0\r\n\r\n'
Using Test Clients
Run the built-in test clients:

bash
make test
Or manually test:

bash
# Test UDP (Bochs SLiRP)
python3 -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.sendto(b'TEST', ('127.0.0.1', 6969)); print(s.recvfrom(1024))"

# Test TCP (QEMU user-mode)
python3 -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.connect(('127.0.0.1', 6969)); s.send(b'PING'); print(s.recv(1024))"
📋 Makefile Targets
Target	Description
make responder	Start the unified network responder
make bochs	Test with Bochs (SLiRP backend)
make qemu	Test with QEMU (multiple NIC backends)
make test	Run test clients
make full-test	Run complete test suite
make test-packets	Generate test packets
make clean	Clean up logs and processes
make help	Show all available targets
🔍 Debugging
Log Files
serial.log - Bochs serial output

qemu-serial.log - QEMU serial output

netX-dump.pcap - Network packet captures

Verbose Output
Run responder with debug output:

bash
python3 unified-responder.py 2>&1 | tee responder.log
Packet Inspection
Use Wireshark or tcpdump to inspect .pcap files:

bash
tcpdump -r net0-dump.pcap -X
🎯 Example Driver Test Scenarios
1. Basic Connectivity Test
bash
# Start responder
python3 unified-responder.py &

# Start Bochs with your driver
bochs -q -f bochs-slirp.conf

# In your OS, run:
# ping 10.0.2.2
# arp -a
2. Multiple Interface Test
bash
# Start responder
python3 unified-responder.py &

# Start QEMU with multiple NICs
./qemu-multi-nic.sh

# Test each interface in your OS
3. Stress Test
bash
# Generate high traffic
./driver-test.sh
# Check for packet loss or errors in your driver
🛠️ Customization
Adding New Protocol Handlers
Extend the UnifiedNetworkResponder class:

python
def handle_custom_protocol(self, data):
    """Handle custom protocol"""
    if data.startswith(b'MY_PROTOCOL'):
        response = b'CUSTOM_RESPONSE'
        return response
    return None
Modifying Network Parameters
Edit the configuration dictionary:

python
config = {
    'udp_port': 7777,
    'tcp_port': 8888,
    'gateway_ip': '192.168.1.1',
    'ip_pool': '192.168.1.100/28'
}
responder = UnifiedNetworkResponder(config)
🤝 Contributing
Fork the repository

Create a feature branch

Commit changes

Push to the branch

Create a Pull Request

📄 License
This project is released under the MIT License. See LICENSE file for details.

🙏 Acknowledgments
BOCHS Development Team

QEMU Development Team

All contributors and testers

🆘 Support
For issues and questions:

Check the debugging section

Review the example configurations

Open an issue with:

Emulator version

OS version

Error logs

Steps to reproduce
