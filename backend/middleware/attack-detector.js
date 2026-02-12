// backend/middleware/attack-detector.js
// Detect simulated attack requests (X-Simulated-Attack + X-Forwarded-For)
// Emit detection events to frontend and call model /simulate-packet for full pipeline.

const fetch = require('node-fetch'); // npm i node-fetch@2

module.exports = function (req, res, next) {
  try {
    // Only act on requests that are marked as simulated attack
    const isAttack = req.get("X-Simulated-Attack") === "true";
    if (!isAttack) return next();

    // Prefer X-Forwarded-For header for demo (first IP if comma-separated)
    const xff = req.get("X-Forwarded-For") || req.get("x-forwarded-for");
    const ip = xff ? xff.split(",")[0].trim() : (req.ip || req.connection?.remoteAddress || 'unknown');

    const io = req.app.get("io"); // socket.io instance
    console.log("⚠️  Simulated Attack Traffic:", ip, req.method, req.path);

    // Build detection object (shape your frontend expects)
    const detection = {
      ip,
      is_ddos: true,
      prediction: "ddos",
      confidence: 99,
      abuseScore: 99,
      threat_level: "HIGH",
      timestamp: new Date().toISOString()
    };

    // Emit to frontend so blocked list / detection UI updates immediately
    if (io) {
      io.emit("detection-result", detection);
      io.emit("ip_blocked", {
        ip,
        reason: "Simulated DDoS Attack (demo)",
        mitigation: "SDN DROP Rule",
        timestamp: new Date().toISOString()
      });
      // Optionally emit the updated blocked-ips list (frontend may request /api/blocked-ips)
    }

    // Non-blocking call to model to simulate a captured packet,
    // so model runs ML detection + Ryu blocking (same code path as real capture).
    (async () => {
      try {
        const MODEL_URL = "http://127.0.0.1:5001"; // change if your model runs elsewhere
        const payload = {
          srcIP: ip,
          dstIP: req.hostname || "127.0.0.1",
          protocol: "TCP",
          packetSize: 1024,
          timestamp: Date.now()
        };
        // fire-and-forget
        await fetch(`${MODEL_URL}/simulate-packet`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          timeout: 2000
        });
      } catch (err) {
        // keep middleware resilient if model unreachable
        // console.warn("simulate-packet call failed:", err && err.message);
      }
    })();

    // mark request for downstream handlers if needed
    req.isSimulatedAttack = true;

  } catch (e) {
    console.error("attack-detector middleware error:", e && e.message);
  } finally {
    // continue request chain
    next();
  }
};
