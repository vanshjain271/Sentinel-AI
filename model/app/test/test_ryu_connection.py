# test_ryu.py — Test Ryu Controller Connection
import requests
import json

RYU_IP   = "192.168.56.101"   # Your RYU VM IP
RYU_PORT = 8080               # Default Ryu REST API port
RYU_URL  = f"http://{RYU_IP}:{RYU_PORT}"

def test_ryu_connection():
    # Test 1: List switches
    url = f"{RYU_URL}/stats/switches"
    print(f"Testing Ryu at {url}...")

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            switches = response.json()
            print("SUCCESS: Ryu Controller is LIVE!")
            print(f"   → Switches: {switches}")
            return True
        else:
            print(f"Failed: HTTP {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("Failed: Cannot reach Ryu. Is it running?")
        return False
    except requests.exceptions.Timeout:
        print("Failed: Request timed out (5s)")
        return False
    except Exception as e:
        print(f"Failed: Unexpected error: {e}")
        return False

# Run test
if __name__ == "__main__":
    test_ryu_connection()