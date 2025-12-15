# Makefile for Network Driver Testing

.PHONY: all bochs qemu test clean

all: test

# Start the unified responder
responder:
	python3 unified-responder.py --udp-port 6969 --tcp-port 6969

# Test Bochs with SLiRP
bochs: responder
	@echo "Starting Bochs with SLiRP backend..."
	@echo "Make sure responder is running in another terminal!"
	bochs -q -f bochs-slirp.conf

# Test QEMU with multiple NICs
qemu: responder
	@echo "Starting QEMU with multiple NIC backends..."
	@echo "Make sure responder is running in another terminal!"
	chmod +x qemu-multi-nic.sh
	./qemu-multi-nic.sh

# Run test clients
test:
	python3 unified-responder.py --test

# Run complete test suite
full-test:
	./driver-test.sh

# Generate test packets
test-packets:
	@echo "Generating test packets..."
	@echo "Testing UDP (Bochs SLiRP)..."
	@python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for i in range(3):
    s.sendto(b'TEST_PACKET_\${i}'.format(i=i), ('127.0.0.1', 6969))
    resp, _ = s.recvfrom(1024)
    print('UDP Response:', resp[:30])
s.close()
"
	@echo ""
	@echo "Testing TCP (QEMU user-mode)..."
	@python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 6969))
s.send(b'PING')
resp = s.recv(1024)
print('TCP Response:', resp)
s.close()
"

clean:
	@rm -f *.log *.pcap serial.log qemu-serial.log
	@pkill -f "python3 unified-responder.py" || true
	@pkill -f "qemu-system" || true
	@pkill -f "bochs" || true

help:
	@echo "Available targets:"
	@echo "  responder   - Start the unified network responder"
	@echo "  bochs       - Test with Bochs (SLiRP backend)"
	@echo "  qemu        - Test with QEMU (multiple NIC backends)"
	@echo "  test        - Run test clients"
	@echo "  full-test   - Run complete test suite"
	@echo "  test-packets - Generate test packets"
	@echo "  clean       - Clean up logs and processes"
