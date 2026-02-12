# locustfile.py — send packets directly to Sentinel /simulate-packet
from locust import HttpUser, task, between
import random
import time
import uuid

# Change this if Sentinel is on a different host/port
SENTINEL_BACKEND = "http://127.0.0.1:5001"  # your Flask app (app.py)


def rand_ip():
    """Generate a fake IPv4 address."""
    return "{}.{}.{}.{}".format(
        random.randint(11, 223),
        random.randint(1, 254),
        random.randint(1, 254),
        random.randint(1, 254),
    )


class SentinelAttacker(HttpUser):
    """
    This Locust user sends many synthetic packets directly to
    Sentinel's /simulate-packet endpoint.

    Sentinel will:
      - update rate_tracker for that srcIP
      - run is_ddos_attack_for_ip(...)
      - if attack → call block_ip() → Ryu flow
      - notify Node backend (blocked IP + live packets)
    """

    host = SENTINEL_BACKEND
    wait_time = between(0.01, 0.05)  # aggressive for demo

    def on_start(self):
        # Use a fixed attack IP per Locust user so PPS builds up
        self.attack_ip = rand_ip()

    def build_payload(self, src_ip: str) -> dict:
        now_ms = int(time.time() * 1000)
        return {
            "srcIP": src_ip,          # Sentinel uses this for rate + blocking
            "dstIP": "127.0.0.1",     # or protected service IP
            "protocol": "TCP",
            "packetSize": random.randint(500, 900),
            "timestamp": now_ms,
            "network_slice": "eMBB",
            # NOTE: your current /simulate-packet ignores this field,
            # but you can wire it in later if you want ML vs simulated.
            "simulated": True,
        }

    def build_headers(self, src_ip: str) -> dict:
        return {
            "User-Agent": f"LocustSentinel/{uuid.uuid4().hex[:6]}",
            "X-Forwarded-For": src_ip,  # for logs / consistency
        }

    @task
    def send_attack_packets(self):
        """
        High-rate synthetic packets from a single srcIP.
        In your Sentinel code:

          - /simulate-packet reads srcIP, packetSize, timestamp
          - rate_tracker.add(src_ip, ts) -> PPS calculation
          - is_ddos_attack_for_ip(..., simulated=True) -> always True
          - block_ip(src_ip) -> Ryu DROP rule
          - POST to Node_URL -> frontend gets blocked attacker

        So running this will continuously:
          - block that IP in Ryu
          - show it in your frontend tables as malicious.
        """
        src_ip = self.attack_ip
        payload = self.build_payload(src_ip)
        headers = self.build_headers(src_ip)

        self.client.post(
            "/simulate-packet",
            json=payload,
            headers=headers,
            name="SENTINEL /simulate-packet",
            timeout=10,
        )
