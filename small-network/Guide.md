Quick Start Guide
Save all files in the same directory:

unified-responder.py

bochs-slirp.conf

qemu-multi-nic.sh

driver-test.sh

Makefile

Make scripts executable:

bash
chmod +x qemu-multi-nic.sh driver-test.sh
Start testing:

Option A - Just the responder:

bash
python3 unified-responder.py
Option B - Test Bochs with SLiRP:

bash
make bochs
Option C - Test QEMU with multiple NICs:

bash
make qemu
Option D - Full test suite:

bash
make full-test
In your OS/driver code, configure networking:

Bochs/SLiRP: Use IP 10.0.2.15, Gateway 10.0.2.2, DNS 10.0.2.3

QEMU NIC1: User-mode, connects to responder on port 6969

QEMU NIC2: Socket, connects to port 5555


