# flow_capture.py
# model/app/flow_capture.py
import asyncio
import pyshark
import logging
from typing import Optional
import threading

# ✅ Add these three lines below ↓↓↓
pyshark.tshark.tshark.get_tshark_path.cache_clear()
pyshark.tshark.tshark.TSHARK_PATH_OVERRIDE = r"C:\Program Files\Wireshark\tshark.exe"
logging.info("✅ TShark path set to C:\\Program Files\\Wireshark\\tshark.exe")

class FlowCapture:
    def __init__(self, interface: str, feature_extractor):
        self.interface = interface
        self.feature_extractor = feature_extractor
        self.capture: Optional[pyshark.LiveCapture] = None
        self.logger = logging.getLogger(__name__)

    def start(self):
        if self.thread is not None:
            return
        self.thread = threading.Thread(target=self._run_async_capture, daemon=True)
        self.thread.start()

    def _run_async_capture(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.capture_loop())
        except Exception as e:
            logging.error(f"Capture loop crashed: {e}")
        finally:
            if self.loop:
                self.loop.close()

    async def capture_loop(self):
        logging.info(f"Started real live capture on {self.interface}")
        try:
            self.capture = pyshark.LiveCapture(
                interface=self.interface,
                bpf_filter='ip',
                use_json=True,
                include_raw=True
            )
            async for packet in self.capture.sniff_continuously():
                try:
                    if hasattr(packet, 'ip'):
                        self.ml_engine.process_packet(packet)
                except Exception as e:
                    logging.debug(f"Packet processing error: {e}")
        except Exception as e:
            logging.error(f"Capture error: {e}")
        finally:
            if self.capture:
                self.capture.close()
