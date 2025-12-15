#!/usr/bin/env python3
"""
Unified Network Listener/Responder for BOCHS/QEMU Driver Testing
Supports: Bochs SLiRP + QEMU Multiple NIC Backends
"""

import socket
import threading
import time
import struct
import ipaddress
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple

class Protocol(Enum):
    ECHO = 1
    ARP = 2
    PING = 3
    DHCP = 4
    CUSTOM = 5

@dataclass
class PacketInfo:
    src_mac: str
    dst_mac: str
    eth_type: int
    src_ip: str
    dst_ip: str
    protocol: int
    payload: bytes

class UnifiedNetworkResponder:
    def __init__(self, config=None):
        self.config = config or {}
        self.running = False
        self.clients = {}  # MAC -> (IP, timestamp)
        self.interfaces = []
        
        # Default configuration
        self.udp_port = self.config.get('udp_port', 6969)
        self.tcp_port = self.config.get('tcp_port', 6969)
        self.broadcast_ip = self.config.get('broadcast_ip', '10.0.2.255')
        self.gateway_ip = self.config.get('gateway_ip', '10.0.2.2')
        self.vm_ip_pool = ipaddress.IPv4Network('10.0.2.100/28')
        
        print("=" * 60)
        print("UNIFIED NETWORK RESPONDER")
        print("=" * 60)
        print(f"UDP Port: {self.udp_port}")
        print(f"TCP Port: {self.tcp_port}")
        print(f"Gateway IP: {self.gateway_ip}")
        print(f"IP Pool: {self.vm_ip_pool}")
        print("=" * 60)
    
    def start_all_services(self):
        """Start all listener services"""
        self.running = True
        
        # Start UDP listener (for Bochs SLiRP)
        udp_thread = threading.Thread(target=self.start_udp_listener, daemon=True)
        udp_thread.start()
        
        # Start TCP listener (for QEMU user-mode)
        tcp_thread = threading.Thread(target=self.start_tcp_listener, daemon=True)
        tcp_thread.start()
        
        # Start broadcast responder
        broadcast_thread = threading.Thread(target=self.start_broadcast_responder, daemon=True)
        broadcast_thread.start()
        
        # Start ARP/DHCP simulator
        service_thread = threading.Thread(target=self.start_network_services, daemon=True)
        service_thread.start()
        
        print("All services started. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def start_udp_listener(self):
        """UDP listener for Bochs SLiRP backend"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', self.udp_port))
        
        print(f"[UDP] Listening on port {self.udp_port} (Bochs SLiRP)")
        
        while self.running:
            try:
                data, addr = sock.recvfrom(2048)
                threading.Thread(target=self.handle_udp_packet, 
                               args=(data, addr, sock)).start()
            except:
                break
    
    def start_tcp_listener(self):
        """TCP listener for QEMU user-mode connections"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', self.tcp_port))
        sock.listen(5)
        
        print(f"[TCP] Listening on port {self.tcp_port} (QEMU user-mode)")
        
        while self.running:
            try:
                client_sock, addr = sock.accept()
                threading.Thread(target=self.handle_tcp_connection,
                               args=(client_sock, addr)).start()
            except:
                break
    
    def start_broadcast_responder(self):
        """Respond to broadcast packets"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.udp_port + 1))  # Different port for broadcasts
        
        print(f"[BROADCAST] Listening on port {self.udp_port + 1}")
        
        while self.running:
            try:
                data, addr = sock.recvfrom(2048)
                if data.startswith(b'BROADCAST'):
                    response = b'BROADCAST_RESPONSE from unified responder'
                    sock.sendto(response, addr)
                    print(f"[BROADCAST] Responded to {addr}")
            except:
                break
    
    def start_network_services(self):
        """Simulate network services (ARP, DHCP, etc.)"""
        print("[SERVICES] Network services simulator started")
        
        # Simulate periodic ARP announcements
        while self.running:
            time.sleep(10)
            print("[SERVICES] Simulating network activity...")
    
    def handle_udp_packet(self, data: bytes, addr: tuple, sock: socket.socket):
        """Handle UDP packets from Bochs/QEMU"""
        client_ip, client_port = addr
        
        print(f"[UDP] Packet from {client_ip}:{client_port}, length: {len(data)}")
        
        # Decode packet based on common patterns
        response = self.decode_and_respond(data, Protocol.ECHO)
        
        if response:
            sock.sendto(response, addr)
            print(f"[UDP] Sent response to {client_ip}:{client_port}")
    
    def handle_tcp_connection(self, sock: socket.socket, addr: tuple):
        """Handle TCP connections from QEMU"""
        client_ip, client_port = addr
        
        print(f"[TCP] Connection from {client_ip}:{client_port}")
        
        try:
            while self.running:
                data = sock.recv(1024)
                if not data:
                    break
                
                print(f"[TCP] Received {len(data)} bytes from {client_ip}")
                
                # Respond based on content
                if data.startswith(b'PING'):
                    response = b'PONG'
                elif data.startswith(b'GET /'):
                    response = b'HTTP/1.0 200 OK\r\n\r\n<h1>Test Server</h1>'
                else:
                    response = data.upper()  # Echo in uppercase
                
                sock.send(response)
                print(f"[TCP] Sent response to {client_ip}")
        
        except:
            pass
        finally:
            sock.close()
            print(f"[TCP] Closed connection from {client_ip}")
    
    def decode_and_respond(self, data: bytes, protocol: Protocol) -> Optional[bytes]:
        """Decode packet and generate appropriate response"""
        
        # Handle different packet types
        if len(data) == 0:
            return None
        
        # 1. Simple echo
        if protocol == Protocol.ECHO:
            return data
        
        # 2. ARP simulation
        if len(data) >= 42 and data[12:14] == b'\x08\x06':  # ARP
            return self.generate_arp_response(data)
        
        # 3. Ping (ICMP Echo) simulation
        if len(data) >= 42 and data[12:14] == b'\x08\x00':  # IP
            if data[23] == 1:  # ICMP
                return self.generate_ping_response(data)
        
        # 4. Custom test patterns
        if data.startswith(b'TEST_'):
            if b'ARP' in data:
                return self.generate_test_arp()
            elif b'PING' in data:
                return self.generate_test_ping()
            elif b'DHCP' in data:
                return self.generate_test_dhcp()
        
        # Default: echo with prefix
        return b'RESPONSE: ' + data
    
    def generate_arp_response(self, data: bytes) -> bytes:
        """Generate ARP response"""
        # Simple ARP response (hardcoded values)
        response = (
            data[6:12] +                    # Target MAC = Source MAC
            b'\x11\x22\x33\x44\x55\x66' +   # Sender MAC (fake gateway)
            b'\x08\x06' +                   # ARP type
            b'\x00\x01\x08\x00\x06\x04\x00\x02' +  # ARP reply
            b'\x11\x22\x33\x44\x55\x66' +   # Sender MAC
            self.ip_to_bytes(self.gateway_ip) +    # Sender IP
            data[6:12] +                    # Target MAC
            data[28:34]                     # Target IP
        )
        return response
    
    def generate_ping_response(self, data: bytes) -> bytes:
        """Generate Ping (ICMP Echo Reply) response"""
        # Swap MACs and IPs, change type to Echo Reply (0)
        response = bytearray(data)
        
        # Swap MAC addresses (bytes 0-5 with 6-11)
        response[0:6], response[6:12] = response[6:12], response[0:6]
        
        # Swap IP addresses (bytes 26-29 with 30-33 in IP header)
        response[26:30], response[30:34] = response[30:34], response[26:30]
        
        # Change ICMP type to Echo Reply (0) at byte 34
        response[34] = 0
        
        # Recalculate IP checksum (simplified)
        response[24] = 0
        response[25] = 0
        
        return bytes(response)
    
    def generate_test_arp(self) -> bytes:
        """Generate test ARP packet"""
        return (
            b'\xff\xff\xff\xff\xff\xff' +   # Broadcast MAC
            b'\x11\x22\x33\x44\x55\x66' +   # Source MAC
            b'\x08\x06' +                   # ARP
            b'\x00\x01\x08\x00\x06\x04\x00\x01' +  # ARP Request
            b'\x11\x22\x33\x44\x55\x66' +   # Sender MAC
            b'\x0a\x00\x02\x02' +           # Sender IP (10.0.2.2)
            b'\x00\x00\x00\x00\x00\x00' +   # Target MAC
            b'\x0a\x00\x02\x64'             # Target IP (10.0.2.100)
        )
    
    def generate_test_ping(self) -> bytes:
        """Generate test Ping packet"""
        return (
            b'\x52\x54\x00\x12\x34\x56' +   # Dest MAC
            b'\x11\x22\x33\x44\x55\x66' +   # Source MAC
            b'\x08\x00' +                   # IPv4
            # IP Header
            b'\x45\x00\x00\x54\x00\x00\x40\x00\x40\x01\x00\x00' +
            b'\x0a\x00\x02\x64' +           # Source IP (10.0.2.100)
            b'\x0a\x00\x02\x02' +           # Dest IP (10.0.2.2)
            # ICMP Echo Request
            b'\x08\x00\xf7\xff\x00\x01\x00\x00' +
            b'PING_TEST_PACKET' * 3
        )
    
    def generate_test_dhcp(self) -> bytes:
        """Generate test DHCP response"""
        return (
            b'\xff\xff\xff\xff\xff\xff' +   # Broadcast
            b'\x11\x22\x33\x44\x55\x66' +   # Source
            b'\x08\x00' +                   # IP
            b'DHCP_OFFER:10.0.2.100/24,GW:10.0.2.2,DNS:10.0.2.3'
        )
    
    def ip_to_bytes(self, ip_str: str) -> bytes:
        """Convert IP string to bytes"""
        return socket.inet_aton(ip_str)
    
    def stop(self):
        """Stop all services"""
        self.running = False
        print("\nShutting down...")

# ============================================================================
# Test Clients for Different Backends
# ============================================================================

class TestClient:
    """Test client to verify responder is working"""
    
    @staticmethod
    def test_bochs_slirp():
        """Test Bochs SLiRP connection"""
        print("\nTesting Bochs SLiRP connection...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        
        test_packets = [
            b'TEST_ARP_REQUEST',
            b'TEST_PING_REQUEST',
            b'Hello from Bochs SLiRP!',
            b'ECHO_TEST_12345'
        ]
        
        for packet in test_packets:
            try:
                sock.sendto(packet, ('127.0.0.1', 6969))
                response, _ = sock.recvfrom(1024)
                print(f"  Sent: {packet[:20]}... -> Got: {response[:30]}...")
            except socket.timeout:
                print(f"  Timeout for: {packet[:20]}...")
        
        sock.close()
    
    @staticmethod
    def test_qemu_user():
        """Test QEMU user-mode connection"""
        print("\nTesting QEMU user-mode connection...")
        
        # Test TCP connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        
        try:
            sock.connect(('127.0.0.1', 6969))
            
            test_messages = [
                b'PING',
                b'GET / HTTP/1.0\r\n\r\n',
                b'TEST_MESSAGE',
                b'DRIVER_TEST_PACKET'
            ]
            
            for msg in test_messages:
                sock.send(msg)
                response = sock.recv(1024)
                print(f"  Sent: {msg[:20]}... -> Got: {response[:30]}...")
        
        except Exception as e:
            print(f"  Connection failed: {e}")
        finally:
            sock.close()

# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Unified Network Responder for Bochs/QEMU Driver Testing"
    )
    parser.add_argument("--udp-port", type=int, default=6969,
                       help="UDP port for Bochs SLiRP")
    parser.add_argument("--tcp-port", type=int, default=6969,
                       help="TCP port for QEMU user-mode")
    parser.add_argument("--gateway", default="10.0.2.2",
                       help="Gateway IP to respond as")
    parser.add_argument("--test", action="store_true",
                       help="Run tests instead of starting server")
    
    args = parser.parse_args()
    
    if args.test:
        # Run test clients
        TestClient.test_bochs_slirp()
        TestClient.test_qemu_user()
    else:
        # Start the unified responder
        config = {
            'udp_port': args.udp_port,
            'tcp_port': args.tcp_port,
            'gateway_ip': args.gateway
        }
        
        responder = UnifiedNetworkResponder(config)
        
        try:
            responder.start_all_services()
        except KeyboardInterrupt:
            responder.stop()
