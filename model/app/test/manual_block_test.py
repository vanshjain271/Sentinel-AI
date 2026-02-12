import requests

RYU_URL = "http://192.168.0.104:8080/stats/flowentry/add"

block_rule = {
    "dpid": 1,
    "priority": 100,
    "match": {
        "nw_src": "10.0.0.2",
        "eth_type": 2048
    },
    "actions": []
}

print(f"🚫 Blocking IP: {block_rule['match']['nw_src']}")
response = requests.post(RYU_URL, json=block_rule)

if response.status_code == 200:
    print("✅ Successfully sent block rule to Ryu Controller.")
else:
    print(f"❌ Failed to send block rule. Status code: {response.status_code}")
    print(response.text)
