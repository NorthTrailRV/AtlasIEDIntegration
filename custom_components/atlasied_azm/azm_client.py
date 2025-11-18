"""AtlasIED AZM4/AZM8 Client Module."""
import asyncio
import json
import logging
from typing import Any, Callable, Optional

_LOGGER = logging.getLogger(__name__)

TCP_PORT = 5321
UDP_PORT = 3131
KEEPALIVE_INTERVAL = 240  # 4 minutes


class AZMClient:
    """Client for AtlasIED AZM4/AZM8 devices."""

    def __init__(self, host: str, update_callback: Optional[Callable] = None):
        """Initialize the AZM client."""
        self.host = host
        self.update_callback = update_callback
        self._tcp_reader: Optional[asyncio.StreamReader] = None
        self._tcp_writer: Optional[asyncio.StreamWriter] = None
        self._udp_transport: Optional[asyncio.DatagramTransport] = None
        self._udp_protocol: Optional[asyncio.DatagramProtocol] = None
        self._keepalive_task: Optional[asyncio.Task] = None
        self._tcp_listener_task: Optional[asyncio.Task] = None
        self._connected = False
        self._subscriptions: set[str] = set()

    async def connect(self) -> bool:
        """Connect to the AZM device via TCP and UDP."""
        try:
            # Connect TCP
            self._tcp_reader, self._tcp_writer = await asyncio.open_connection(
                self.host, TCP_PORT
            )
            _LOGGER.info("Connected to AZM device at %s:%d via TCP", self.host, TCP_PORT)

            # Setup UDP
            loop = asyncio.get_event_loop()
            self._udp_transport, self._udp_protocol = await loop.create_datagram_endpoint(
                lambda: AZMUDPProtocol(self._handle_udp_message),
                local_addr=('0.0.0.0', 0)
            )
            _LOGGER.info("UDP listener created for AZM device")

            self._connected = True

            # Start keepalive task
            self._keepalive_task = asyncio.create_task(self._keepalive_loop())

            # Start TCP listener task
            self._tcp_listener_task = asyncio.create_task(self._tcp_listener())

            return True

        except Exception as err:
            _LOGGER.error("Failed to connect to AZM device: %s", err)
            return False

    async def disconnect(self):
        """Disconnect from the AZM device."""
        self._connected = False

        # Cancel tasks
        if self._keepalive_task:
            self._keepalive_task.cancel()
            try:
                await self._keepalive_task
            except asyncio.CancelledError:
                pass

        if self._tcp_listener_task:
            self._tcp_listener_task.cancel()
            try:
                await self._tcp_listener_task
            except asyncio.CancelledError:
                pass

        # Close TCP
        if self._tcp_writer:
            self._tcp_writer.close()
            await self._tcp_writer.wait_closed()

        # Close UDP
        if self._udp_transport:
            self._udp_transport.close()

        _LOGGER.info("Disconnected from AZM device")

    async def _keepalive_loop(self):
        """Send periodic keepalive messages."""
        while self._connected:
            try:
                await asyncio.sleep(KEEPALIVE_INTERVAL)
                await self.send_get("KeepAlive", "str")
            except asyncio.CancelledError:
                break
            except Exception as err:
                _LOGGER.error("Keepalive error: %s", err)

    async def _tcp_listener(self):
        """Listen for TCP messages from the device."""
        buffer = ""
        while self._connected and self._tcp_reader:
            try:
                data = await self._tcp_reader.read(4096)
                if not data:
                    _LOGGER.warning("TCP connection closed by device")
                    break

                buffer += data.decode('utf-8')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line:
                        await self._handle_tcp_message(line)

            except asyncio.CancelledError:
                break
            except Exception as err:
                _LOGGER.error("TCP listener error: %s", err)
                break

    async def _handle_tcp_message(self, message: str):
        """Handle incoming TCP message."""
        try:
            data = json.loads(message)
            method = data.get("method")

            if method in ("update", "getResp"):
                params = data.get("params", [])
                if isinstance(params, dict):
                    params = [params]

                for param_data in params:
                    if self.update_callback:
                        await self.update_callback(param_data)

        except json.JSONDecodeError:
            _LOGGER.warning("Invalid JSON received: %s", message)
        except Exception as err:
            _LOGGER.error("Error handling TCP message: %s", err)

    def _handle_udp_message(self, message: str):
        """Handle incoming UDP message (for meter updates)."""
        try:
            data = json.loads(message)
            method = data.get("method")

            if method in ("update", "getResp"):
                params = data.get("params", [])
                if isinstance(params, dict):
                    params = [params]

                for param_data in params:
                    if self.update_callback:
                        asyncio.create_task(self.update_callback(param_data))

        except json.JSONDecodeError:
            _LOGGER.warning("Invalid JSON received via UDP: %s", message)
        except Exception as err:
            _LOGGER.error("Error handling UDP message: %s", err)

    async def _send_tcp(self, message: dict) -> bool:
        """Send a message via TCP."""
        if not self._tcp_writer or not self._connected:
            _LOGGER.error("Not connected to AZM device")
            return False

        try:
            json_str = json.dumps(message) + "\n"
            self._tcp_writer.write(json_str.encode('utf-8'))
            await self._tcp_writer.drain()
            return True
        except Exception as err:
            _LOGGER.error("Failed to send TCP message: %s", err)
            return False

    async def send_set(self, param: str, value: Any, fmt: str = "val") -> bool:
        """Set a parameter value."""
        message = {
            "jsonrpc": "2.0",
            "method": "set",
            "params": {
                "param": param,
                fmt: value
            }
        }
        return await self._send_tcp(message)

    async def send_bump(self, param: str, value: Any, fmt: str = "val") -> bool:
        """Bump (increment/decrement) a parameter value."""
        message = {
            "jsonrpc": "2.0",
            "method": "bmp",
            "params": {
                "param": param,
                fmt: value
            }
        }
        return await self._send_tcp(message)

    async def send_get(self, param: str, fmt: str = "val") -> bool:
        """Get a parameter value."""
        message = {
            "jsonrpc": "2.0",
            "method": "get",
            "params": {
                "param": param,
                "fmt": fmt
            }
        }
        return await self._send_tcp(message)

    async def subscribe(self, param: str, fmt: str = "val") -> bool:
        """Subscribe to parameter updates."""
        message = {
            "jsonrpc": "2.0",
            "method": "sub",
            "params": {
                "param": param,
                "fmt": fmt
            }
        }
        success = await self._send_tcp(message)
        if success:
            self._subscriptions.add(param)
        return success

    async def subscribe_multiple(self, params: list[tuple[str, str]]) -> bool:
        """Subscribe to multiple parameters at once."""
        message = {
            "jsonrpc": "2.0",
            "method": "sub",
            "params": [{"param": p, "fmt": f} for p, f in params]
        }
        success = await self._send_tcp(message)
        if success:
            self._subscriptions.update(p for p, _ in params)
        return success

    async def unsubscribe(self, param: str, fmt: str = "val") -> bool:
        """Unsubscribe from parameter updates."""
        message = {
            "jsonrpc": "2.0",
            "method": "unsub",
            "params": {
                "param": param,
                "fmt": fmt
            }
        }
        success = await self._send_tcp(message)
        if success:
            self._subscriptions.discard(param)
        return success

    @property
    def connected(self) -> bool:
        """Return connection status."""
        return self._connected


class AZMUDPProtocol(asyncio.DatagramProtocol):
    """UDP Protocol for receiving meter updates."""

    def __init__(self, message_callback: Callable):
        """Initialize the UDP protocol."""
        self.message_callback = message_callback

    def datagram_received(self, data: bytes, addr: tuple):
        """Handle received UDP datagram."""
        try:
            message = data.decode('utf-8').strip()
            if message:
                self.message_callback(message)
        except Exception as err:
            _LOGGER.error("Error processing UDP datagram: %s", err)
